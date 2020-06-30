from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	pass

class Card(models.Model):
	author = models.ForeignKey(to = User, on_delete = models.CASCADE, related_name = 'cards')
	recipient = models.ForeignKey(to = user, null = True, on_delete = models.SET_NULL, related_name = "recieved")
