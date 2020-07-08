from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from .models import User

class TestSomething(TestCase):
	def setup(self):
		self.client = APIClient()
		self.factory = APIRequestFactory()
		self.u1 = User.object.create(username = 'jim')
		self.u2 = User.object.create(username = 'bono')
	def test_card_post(self):
		self.client.login(self.u1)
		request = self.factory.post('/api/card/', { 'outer_text': 'foo', 'inner_text': 'bar' }, format = 'json')
