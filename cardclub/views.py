from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404

from .models import Card, User
from .rest import CardViewSet

@login_required
def friend_relation(request, username):
	"""Returns a string representing the relationship to another user:
	'none' if neither user has added each other;
	'friends' if both users have added each other;
	'pending' if the request's user has added the target;
	'requested' if the target user has added the request's user.

	Keyword Arguments:
	request -- The request.
	username -- The target user
	"""
	if not request.user.is_authenticated:
		return HttpResponse(status = 401)
	if not request.method == 'GET':
		return HttpResponse(status = 405)
	target = get_object_or_404(User, username = username)
	my_friend = len(self.request.user.friends.filter(username = username)) == 1
	their_friend = len(target.friends.filter(username = self.request.user.username)) == 1
	output = { 'rel': 'none' }
	if my_friend and their_friend:
		output['rel'] = 'friends'
	elif my_friend and not their_friend:
		output['rel'] = 'pending'
	elif their_friend and not my_friend:
		output['rel'] = 'requested'
	return JsonResponse(output)

@login_required
def add_friend(request, username):
	if not request.user.is_authenticated:
		return HttpResponse(status = 401)
	if not request.method == 'POST':
		return HttpResponse(status = 405)
	if username == request.user.username:
		return HttpResponse(status = 403)
	target = get_object_or_404(User, username = username)
	if len(request.user.friends.filter(username = username)) != 0:
		return HttpResponse(status = 202)
	request.user.friends.add(target)
	request.user.save()
	return HttpResponse(status = 200)

@login_required
def del_friend(request, username):
	if not request.user.is_authenticated:
		return HttpResponse(status = 401)
	if not request.method == 'POST':
		return HttpResponse(status = 405)
	if request.user.username == username:
		return HttpResponse(status = 403)
	target = get_object_or_404(User, username = username)
	if len(request.user.friends.filter(username = username)) == 0:
		return HttpResponse(status = 202)
	request.user.friends.remove(target)
	request.user.save()
	return HttpResponse(200)
