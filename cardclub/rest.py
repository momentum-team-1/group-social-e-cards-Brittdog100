from rest_framework import routers, serializers, viewsets

from .models import Card, User

router = routers.DefaultRouter()

class FriendSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'url']
class UserSerializer(serializers.HyperlinkedModelSerializer):
	friends = FriendSerializer(many = True, required = False, default = [])
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
			'image_url'
		]
class CardViewSet(viewsets.ModelViewSet):
	queryset = Card.objects.all()
	serializer_class = CardSerializer
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)
	def get_queryset(self):
		return CardViewSet.queryset.filter(author = self.request.user)
router.register('card', CardViewSet)
