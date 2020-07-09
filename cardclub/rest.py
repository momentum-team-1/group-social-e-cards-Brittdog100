from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, routers, serializers, viewsets
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
	pager = PageNumberPagination()
	permission_classes = [permissions.IsAuthenticated]
	lookup_field = 'username'
	def get_queryset(self):
		return User.objects.all()
	def destroy(self, request, username):
		user = get_object_or_404(User, username = username)
		if user != request.user and not request.user.is_staff:
			return HttpResponse(status = 403)
		self.perform_destroy(user)
		return HttpResponse(status = 403)
	@action(detail = True, methods = ['GET'])
	def friend_list(self, request, username):
		user = get_object_or_404(User, username = username)
		serializer = FriendSerializer(
			user.friends.all(),
			many = True,
			context = { 'context': request }
		)
		return Response(serializer.data)
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'], permission_classes = [permissions.IsAuthenticated])
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
	@action(detail = True, methods = ['GET'])
	def cards(self, request, username, page = 0):
		user = get_object_or_404(User, username = username)
		results = self.pager.paginate_queryset(user.cards.all(), request)
		serializer = CardSerializer(
			results,
			many = True,
			context = { 'request': request }
		)
		return self.pager.get_paginated_response(serializer.data)
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
			'font',
			'color',
			'image_url',
			'timestamp'
		]
class CardViewSet(viewsets.ModelViewSet):
	queryset = Card.objects.all().order_by('-timestamp')
	serializer_class = CardSerializer
	pager = PageNumberPagination()
	permission_classes = [permissions.IsAuthenticated]
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)
	def destroy(self, request, pk):
		card = get_object_or_404(Card, pk = pk)
		if card.author != request.user:
			return HttpResponse(status = 403)
		self.perform_destroy(card)
		return HttpResponse(status = 200)
	def get_queryset(self):
		request = self.request
		if not request.user.is_authenticated:
			return Card.objects.none()
		if request.method == 'GET':
			return CardViewSet.queryset.all().order_by('-timestamp')
		else:
			return request.user.cards.all().order_by('-timestamp')
	@action(detail = False, methods = ['GET'])
	def mine(self, request, page = 0):
		results = self.pager.paginate_queryset(self.get_queryset().filter(Q(author = request.user) | Q(recipient = request.user)), request)
		serializer = CardSerializer(
			results,
			many = True,
			context = { 'request': request }
		)
		return self.pager.get_paginated_response(serializer.data)
	@action(detail = False, methods = ['GET'])
	def feed(self, request, page = 0):
		results = self.pager.paginate_queryset(self.get_queryset().filter(author__followers = request.user), request)
		serializer = CardSerializer(
			results,
			many = True,
			context = { 'request': request }
		)
		return self.pager.get_paginated_response(serializer.data)
	@action(detail = True, methods = ['GET', 'POST'], permission_classes = [permissions.IsAuthenticated])
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
			if not comment.author == request.user:
				return HttpResponse(status = 403)
			comment.delete()
			return HttpResponse(status = 200)
router.register('card', CardViewSet)
