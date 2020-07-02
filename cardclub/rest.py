from django.db.models import Q
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Card, User
from . import views as ajax

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
router.register('user', UserViewSet)

class CardSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Card
		fields = [
			'id',
			'url',
			'recipient',
			'text_inner',
			'text_outer',
			'styles',
			'image_url',
			'timestamp'
		]
class CardViewSet(viewsets.ModelViewSet):
	queryset = Card.objects.order_by('-timestamp').all()
	serializer_class = CardSerializer
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)
	def get_queryset(self):
		return CardViewSet.queryset.all()
	@action(detail = False, methods = ['GET'])
	def mine(self, request, page):
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
