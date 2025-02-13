from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.http import JsonResponse
from django.utils.translation import gettext as _
from transcendence.decorators import login_required_redirect

from user_management.friends import Friends, Friends_Manager

User = get_user_model()


@login_required_redirect
def friendships(request, username=None):
	"""
	wrapper for fetch_friends_public

	API Endpoint: /users/api/friends/active/<str:username>/ where username is optional
	"""
	if username is None:
		user = request.user
	else:
		user = User.objects.get(username=username)
	friends_of = {
		friendship.origin for friendship in Friends.objects.filter(target=user, accepted=True)
	} | {friendship.target for friendship in Friends.objects.filter(origin=user, accepted=True)}
	return JsonResponse(
		{
			'success': True,
			'friends_users': [friend.username for friend in friends_of],
		}
	)


@login_required_redirect
def requests(request):
	"""
	wrapper for fetch_received, fetch_sent

	API Endpoint: /users/api/friends/inactive/
	"""
	received = Friends_Manager.fetch_received(target=request.user)
	sent = Friends_Manager.fetch_sent(origin=request.user)
	return JsonResponse(
		{
			'success': True,
			'received': [sender.username for sender in received],
			'sent': [receiver.username for receiver in sent],
		}
	)


@login_required_redirect
def send_request(request, username):
	"""
	API endpoint: `/users/api/friends/request/<str:username>/`
	"""
	try:
		Friends_Manager.friends_request(origin=request.user, target_username=username)
	except ValidationError as e:
		return JsonResponse({'success': False, 'message': str(e)})
	return JsonResponse({'success': True, 'message': _('Friend request sent successfully.')})


@login_required_redirect
def cancel_request(request, username):
	"""
	API endpoint: `/users/api/friends/cancel/<str:username>/`
	"""
	try:
		Friends_Manager.cancel_friends_request(origin=request.user, target_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e)})
	return JsonResponse({'success': True, 'message': _('Friend request cancelled.')})


@login_required_redirect
def accept_request(request, username):
	"""
	API endpoint: `/users/api/friends/accept/<str:username>/`
	"""
	try:
		Friends_Manager.accept_request_as_target(target=request.user, origin_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e)})
	return JsonResponse({'success': True, 'message': _('Friend request accepted successfully.')})


@login_required_redirect
def deny_request(request, username):
	"""
	API endpoint: `/users/api/friends/deny/<str:username>/`
	"""
	try:
		Friends_Manager.deny_friends_request(target=request.user, origin_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e)})
	return JsonResponse({'success': True, 'message': _('Friend request denied.')})


@login_required_redirect
def remove(request, username):
	"""
	API endpoint: `/users/api/friends/remove/<str:username>/`
	"""
	try:
		Friends_Manager.remove_friend(remover=request.user, target_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e)})
	return JsonResponse({'success': True, 'message': _('Friendship ended.')})
