from django.test import APIClient, APIRequestFactory, TestCase

class TestSomething(TestCase):
	def setup(self):
		self.client = APIClient()
		self.factory = APIRequestFactory()
		self.u1 = User.object.create(username = 'jim')
		self.u2 = User.object.create(username = 'bono')
	def test_foo(self):
		self.client.login(self.u1)
