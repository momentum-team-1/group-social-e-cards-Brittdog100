from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Card, Comment, User

router = routers.DefaultRouter()

class FriendSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name']
class UserSerializer(serializers.HyperlinkedModelSerializer):
	friends = FriendSerializer(read_only = True, many = True, required = False, default = [])
	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'friends'
		]
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'username'
	@action(detail = False, methods = ['GET'])
	def friends(self, request):
		serializer = UserSerializer(
			UserViewSet.queryset.filter(user__in = request.user.friends.all()),
			many = True,
			context = { 'context': request }
		)
		return Response(serializer.data)
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def friend(self, request, username):
		target = get_object_or_404(User, username = username)
		if request.user.username == username:
			return HttpResponse(status = 403)
		if request.method == 'GET':
			my_friend = len(self.request.user.friends.filter(username = username)) == 1
			their_friend = len(target.friends.filter(username = self.request.user.username)) == 1
			rel = 0
			if my_friend:
				rel += 1
			if their_friend:
				rel += 2
			return JsonResponse({ 'rel': rel })
		elif request.method == 'POST':
			if len(request.user.friends.filter(username = username)) != 0:
				return HttpResponse(status = 202)
			request.user.friends.add(target)
			request.user.save()
			return HttpResponse(status = 200)
		elif request.method == 'DELETE':
			if len(request.user.friends.filter(username = username)) == 0:
				return HttpResponse(status = 202)
			request.user.friends.remove(target)
			request.user.save()
			return HttpResponse(200)
router.register('user', UserViewSet)

class CommentSerializer(serializers.HyperlinkedModelSerializer):
	author = serializers.ReadOnlyField(source = 'author.username')
	post = serializers.ReadOnlyField(source = 'post.pk')
	class Meta:
		model = Comment
		fields = [
			'id',
			'author',
			'post',
			'text',
			'timestamp'
		]

class CardSerializer(serializers.HyperlinkedModelSerializer):
	author = serializers.ReadOnlyField(source = 'author.username')
	recipient = serializers.ReadOnlyField(source = 'recipient.username')
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
	pager = PageNumberPagination()
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)
	def get_queryset(self):
		return CardViewSet.queryset.all()
	@action(detail = False, methods = ['GET'])
	def mine(self, request, page = 0):
		results = self.pager.paginate_queryset(CardViewSet.queryset.filter(Q(author = request.user) | Q(recipient = request.user)), request)
		serializer = CardSerializer(
			results,
			many = True,
			context = { 'request': request }
		)
		return self.pager.get_paginated_response(serializer.data)
	@action(detail = False, methods = ['GET'])
	def feed(self, request, page = 0):
		results = self.pager.paginate_queryset(CardViewSet.queryset.filter(author__followers = request.user), request)
		serializer = CardSerializer(
			results,
			many = True,
			context = { 'request': request }
		)
		return self.pager.get_paginated_response(serializer.data)
	@action(detail = True, methods = ['GET', 'POST'])
	def comment(self, request, pk):
		post = get_object_or_404(Card, pk = pk)
		if(request.method == 'GET'):
			serializer = CommentSerializer(
				Comment.objects.filter(post = post),
				many = True,
				context = { 'request': request }
			)
			return Response(serializer.data)
		if(request.method == 'POST'):
			serializer = CommentSerializer(data = request.data)
			if not serializer.is_valid():
				return HttpResponse(status = 400)
			serializer.save(author = self.request.user, post = post)
			return HttpResponse(status = 201)
		if(request.method == 'DELETE'):
			comment = get_object_or_404(Comment, pk = request.data['id'])
			comment.delete()
			return HttpResponse(status = 200)
router.register('card', CardViewSet)
