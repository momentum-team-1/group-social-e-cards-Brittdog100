from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Card, User

router = routers.DefaultRouter()

class FriendSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'url', 'first_name', 'last_name']
class UserSerializer(serializers.HyperlinkedModelSerializer):
	friends = FriendSerializer(read_only = True, many = True, required = False, default = [])
	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'url',
			'friends'
		]
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	@action(detail = False, methods = ['GET'])
	def friends(self, request):
		serializer = UserSerializer(
			UserViewSet.queryset.filter(user__in = request.user.friends.all()),
			many = True,
			context = { 'context': request }
		)
		return Response(serializer.data)
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def friend(self, request, pk):
		target = get_object_or_404(User, pk = pk)
		if request.user.username == target.username:
			return HttpResponse(status = 403)
		if request.method == 'GET':
			my_friend = len(self.request.user.friends.filter(username = target.username)) == 1
			their_friend = len(target.friends.filter(username = self.request.user.username)) == 1
			rel = 0
			if my_friend:
				rel += 1
			if their_friend:
				rel += 2
			return JsonResponse({ 'rel': rel })
		elif request.method == 'POST':
			if len(request.user.friends.filter(username = target.username)) != 0:
				return HttpResponse(status = 202)
			request.user.friends.add(target)
			request.user.save()
			return HttpResponse(status = 200)
		elif request.method == 'DELETE':
			if len(request.user.friends.filter(username = target.username)) == 0:
				return HttpResponse(status = 202)
			request.user.friends.remove(target)
			target.friends.remove(request.user)
			request.user.save()
			return HttpResponse(200)
router.register('user', UserViewSet)

class CommentSerializer(serializers.HyperlinkedModelSerializer):
	author = serializers.ReadOnlyField(source = 'author.username')
	post = serializers.ReadOnlyField(source = 'post.pk')
	class Meta:
		pass

class CardSerializer(serializers.HyperlinkedModelSerializer):
	author = serializers.ReadOnlyField(source = 'author.username')
	class Meta:
		model = Card
		fields = [
			'id',
			'url',
			'author',
			'recipient',
			'text_inner',
			'text_outer',
			'styles',
			'image_url',
			'timestamp'
		]
class CardViewSet(viewsets.ModelViewSet):
	queryset = Card.objects.all().order_by('-timestamp')
	serializer_class = CardSerializer
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)
	def get_queryset(self):
		return CardViewSet.queryset.all()
	@action(detail = False, methods = ['GET'])
	def mine(self, request, page = 0):
		serializer = CardSerializer(
			CardViewSet.queryset.filter(Q(author = request.user) | Q(recipient = request.user)),
			many = True,
			context = { 'request': request }
		)
		return Response(serializer.data)
	@action(detail = False, methods = ['GET'])
	def feed(self, request, page = 0):
		serializer = CardSerializer(
			CardViewSet.queryset.filter(author__in = request.user.friends.all()),
			many = True,
			context = { 'request': request }
		)
		pager = self.paginate_queryset(CardViewSet.queryset)
		if page == 0 or pager is None:
			return Response(serializer.data)
		return self.get_paginated_response(serializer.data)
router.register('card', CardViewSet)
