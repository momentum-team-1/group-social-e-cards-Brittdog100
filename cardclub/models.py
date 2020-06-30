from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	pass

MAX_FIELD_LEN = 255

class Card(models.Model):
	author = models.ForeignKey(to = User, on_delete = models.CASCADE, related_name = 'cards')
	recipient = models.ForeignKey(to = User, null = True, on_delete = models.SET_NULL, related_name = "recieved")
	text_inner = models.CharField(max_length = MAX_FIELD_LEN)
	text_outer = models.CharField(max_length = MAX_FIELD_LEN)
