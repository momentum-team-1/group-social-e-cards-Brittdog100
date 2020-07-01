from rest_framework import routers, serializers, viewsets

from .models import Card

router = routers.DefaultRouter()

class CardSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Card
		fields = [
			'id',
			'url',
			'recipient',
			'text_inner',
			'text_outer',
		]
class CardViewSet(viewsets.ModelViewSet):
	queryset = Card.objects.all()
	serializer_class = CardSerializer
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)
	def get_queryset(self):
		return CardViewSet.queryset.filter(author = self.request.user)
router.register('card', CardViewSet)
