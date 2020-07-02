from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	friends = models.ManyToManyField(to = 'self', symmetrical = False)

MAX_FIELD_LEN = 256
MAX_INTERNAL_LEN = 512

class Card(models.Model):
	author = models.ForeignKey(to = User, on_delete = models.CASCADE, related_name = 'cards')
	recipient = models.ForeignKey(to = User, null = True, on_delete = models.SET_NULL, related_name = "recieved")
	text_inner = models.CharField(max_length = MAX_FIELD_LEN)
	text_outer = models.CharField(max_length = MAX_FIELD_LEN)
	styles = models.CharField(max_length = MAX_INTERNAL_LEN, blank = True)
	image_url = models.CharField(max_length = MAX_INTERNAL_LEN, null = True)
	timestamp = models.DateTimeField(auto_now_add = True)
