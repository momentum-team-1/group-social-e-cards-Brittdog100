from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Card, User
from . import views as ajax

router = routers.DefaultRouter()

class FriendSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'url']
class UserSerializer(serializers.HyperlinkedModelSerializer):
	friends = FriendSerializer(read_only = True, many = True, required = False, default = [])
	class Meta:
		model = User
		fields = [
			'username',
			'url',
			'friends'
		]
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
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
	queryset = Card.objects.all()
	serializer_class = CardSerializer
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)
	def get_queryset(self):
		return CardViewSet.queryset.all()
	@action(detail = False, methods = ['GET'])
	def mine(self, request):
		serializer = CardSerializer(
			CardViewSet.queryset.filter(author = request.user),
			many = True,
			context = { 'request': request }
		)
		return Response(serializer.data)
	@action(detail = False, methods = ['GET'])
	def feed(self, request):
		serializer = CardSerializer(
			CardViewSet.queryset.filter(author__in = request.user.friends.all()),
			many = True,
			context = { 'request': request }
		)
		return Response(serializer.data)
router.register('card', CardViewSet)
