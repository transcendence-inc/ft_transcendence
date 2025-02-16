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
			'friends_users': [
				{
					'username': friend.username,
					# 'profile_picture': friend.image.url if friend.image else None,
				}
				for friend in friends_of
			],
		}
	)

@login_required_redirect
def requests(request):
	"""
	API Endpoint: /users/api/friends/inactive/
	"""
	return JsonResponse(
		{
			'success': True,
			'received': list(
				{
					friendship.origin.username
					for friendship in Friends.objects.filter(target=request.user, accepted=False)
				}
			),
			'sent': list(
				{
					friendship.target.username
					for friendship in Friends.objects.filter(origin=request.user, accepted=False)
				}
			),
		}
	)


@login_required_redirect
def send_request(request, username):
	"""
	API endpoint: `/users/api/friends/request/<str:username>/`
	"""
	try:
		Friends_Manager.request(origin=request.user, target_username=username)
	except ValidationError as e:
		return JsonResponse({'success': False, 'message': str(e.message)})
	return JsonResponse({'success': True, 'message': _('Friend request sent successfully.')})


@login_required_redirect
def cancel_request(request, username):
	"""
	API endpoint: `/users/api/friends/cancel/<str:username>/`
	"""
	try:
		Friends_Manager.cancel_request(origin=request.user, target_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e.message)})
	return JsonResponse({'success': True, 'message': _('Friend request cancelled.')})


@login_required_redirect
def accept_request(request, username):
	"""
	API endpoint: `/users/api/friends/accept/<str:username>/`
	"""
	try:
		Friends_Manager.accept_request(target=request.user, origin_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e.message)})
	return JsonResponse({'success': True, 'message': _('Friend request accepted.')})


@login_required_redirect
def deny_request(request, username):
	"""
	API endpoint: `/users/api/friends/deny/<str:username>/`
	"""
	try:
		Friends_Manager.deny_request(target=request.user, origin_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e.message)})
	return JsonResponse({'success': True, 'message': _('Friend request denied.')})


@login_required_redirect
def remove(request, username):
	"""
	API endpoint: `/users/api/friends/remove/<str:username>/`
	"""
	try:
		Friends_Manager.remove_friend(remover=request.user, target_username=username)
	except Exception as e:
		return JsonResponse({'success': False, 'message': str(e.message)})
	return JsonResponse({'success': True, 'message': _('Friendship ended.')})
