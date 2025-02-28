from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from transcendence.decorators import login_required_redirect
from user_management.friends_blocked_users import Block_Manager, Friends_Manager
from user_management.models import CustomUser


def profile_list(request):
	"""
	Api call that returns all profiles.
	dashboard/api/profile_list is API endpoint.
	"""
	users = CustomUser.objects.all()
	profile_data = [
		{
			'username': user.username,
			'image_url': user.image.url,
		}
		for user in users
	]
	return JsonResponse({
		'success': True,
		'profiles': profile_data,
	})

@login_required_redirect
def get_profile(request, username):
	"""
	Api call that returns a specific profile.
	dashboard/api/get_profile/profilename is API endpoint.
	"""
	user = get_object_or_404(CustomUser, username=username)

	is_requests_profile = False
	is_user_blocked_by_requester = False
	if (request.user == user):
		is_requests_profile = True
	else:
		if Block_Manager.is_blocked_by(blockee=user, blocker=request.user):
			is_user_blocked_by_requester = True

	if Block_Manager.is_blocked_by(blockee=request.user, blocker=user):
		return JsonResponse({
			'success': True,
			'username': user.username,
			'image_url': user.image.url,
			'blocked': True,
			'is_user_blocked_by_requester': is_user_blocked_by_requester,
		})

	friend_count = Friends_Manager.count_friends(user)

	friend_status = 'not_friends'
	if request.user != user:
		status, pending = Friends_Manager.status(request.user, user)
		if status:
			friend_status = 'friends'
		elif pending is None:
			friend_status = 'not_friends'
		elif pending:
			friend_status = 'friend_request_sent'
		else:
			friend_status = 'friend_request_received'

	profile_data = {
		'username': user.username,
		'image_url': user.image.url,
		'quiz_games_played': user.quiz_games_played,
		'quiz_games_won': user.quiz_games_won,
		'quiz_total_score': user.quiz_total_score,
		'quiz_high_score': user.quiz_high_score,
		'quiz_questions_asked': user.quiz_questions_asked,
		'quiz_correct_answers': user.quiz_correct_answers,
		'is_requests_profile': is_requests_profile,
		'is_user_blocked_by_requester': is_user_blocked_by_requester,
		'friend_count': friend_count,
		'friend_status': friend_status,
		'pong_matches_won': user.matches_won,
		'pong_matches_lost': user.matches_lost,
	}
	return JsonResponse({
		'success': True,
		'profile': profile_data,
		'blocked': False,
	})
