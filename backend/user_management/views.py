import json
import re

from django.contrib.auth import (
	authenticate,
	get_user_model,
	login,
	logout,
	update_session_auth_hash,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import F
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.translation import gettext as _
from pong.models import PongGame
from pong.utils import win_to_loss_ratio
from transcendence.decorators import login_required_redirect

from .blocked_users import Block_Manager, BlockedUsers

# from .consumers import UserProfileConsumer

User = get_user_model()


@login_required_redirect
def block_user(request, username):
	"""
	Block a user. This will return an error if the user is already blocked.
	API Endpoint: /users/api/block/
	"""

	try:
		Block_Manager.block_user(blocker=request.user, target_username=username)
		return JsonResponse({'success': True, 'message': _('User blocked successfully.')})
	except ValidationError:
		return JsonResponse({'success': False, 'message': _('Invalid request method.')})


@login_required_redirect
def unblock_user(request, username):
	"""
	Unblock a user. This is successful even if the user was not blocked.
	API Endpoint: /users/api/unblock/
	"""

	try:
		Block_Manager.unblock_user(origin=request.user, target_username=username)
		return JsonResponse({'success': True, 'message': _('User unblocked successfully.')})
	except ValidationError:
		return JsonResponse({'success': False, 'message': _('Invalid request method.')})


@login_required_redirect
def blocked_users(request):
	"""
	Shows for the request user, their blocked users.
	API Endpoint: /users/api/blocked/
	"""
	blocked_by_request_user = BlockedUsers.objects.filter(blocker=request.user)
	if blocked_by_request_user.count() == 0:
		return JsonResponse({'success': True, 'blocked_users': []})
	return JsonResponse(
		{
			'success': True,
			'blocked_users': [blocked.blockee.username for blocked in blocked_by_request_user],
		}
	)


def register(request):
	"""
	Registers a new user.
	API Endpoint: /users/api/register/
	"""
	if request.method == 'POST':
		username = request.POST.get('username')
		email = request.POST.get('email')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')

		if password1 != password2:
			return JsonResponse(
				{'success': False, 'type': 'password', 'message': _('Passwords do not match.')}
			)
		validation_response = validate_data(username, email)
		if validation_response:
			return validation_response
		# If not done automatically, ensure passwords are checked for lenght etc
		user = User.objects.create_user(username=username, email=email, password=password1)
		user.save()
		return JsonResponse({'success': True, 'message': _('Account created successfully.')})
	else:
		return JsonResponse({'success': False, 'message': _('Invalid request method.')})


def login_view(request):
	"""
	Login a user.
	API Endpoint: /users/api/login/
	"""
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			new_csrf_token = get_token(request)
			return JsonResponse(
				{'success': True, 'message': _('Login successful.'), 'csrf_token': new_csrf_token, 'username': username}
			)
		else:
			return JsonResponse({'success': False, 'message': _('Invalid username or password!')})
	else:
		return JsonResponse({'success': False, 'message': _('Invalid request method.')})


def logout_view(request):
	"""
	Logout a user.
	API Endpoint: /users/api/logout/
	"""
	if request.method == 'POST':
		logout(request)
		new_csrf_token = get_token(request)
		return JsonResponse(
			{'success': True, 'message': _('Logout successful.'), 'csrf_token': new_csrf_token}
		)
	else:
		return JsonResponse({'success': False, 'message': _('Invalid request method.')})


@login_required_redirect
def get_account_details(request):
	"""
	Get the account details of the logged in user.
	API Endpoint: /users/api/get_account_details/
	"""
	if request.method == 'GET':
		user = request.user
		return JsonResponse(
			{
				'success': True,
				'username': user.username,
				'email': user.email,
				'image_url': user.image.url,
			}
		)
	else:
		return JsonResponse({'success': False, 'message': _('Invalid request method.')})


@login_required_redirect
def update_profile(request):
	"""
	Inputs new profile data.
	API Endpoint: /users/api/update_profile/
	"""
	if request.method == 'POST':
		user = request.user
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = request.POST.get('password')
		image = request.FILES.get('image')

		validation_response = validate_data(username, email, user)
		if validation_response:
			return validation_response

		if not authenticate(username=user.username, password=password):
			return JsonResponse({'success': False, 'message': _('Invalid password.')})
		if username:
			user.username = username
		if email:
			user.email = email
		if image:
			user.image = image
		user.save()
		return JsonResponse({'success': True, 'message': _('Profile updated successfully.')})
	return JsonResponse({'success': False, 'message': _('Invalid request method.')})


def validate_data(username, email, current_user=None):
	if email:
		try:
			validate_email(email)
		except ValidationError:
			return JsonResponse(
				{'success': False, 'type': 'mail', 'message': _('Invalid email address.')}
			)
		if current_user:
			if User.objects.filter(email=email).exclude(id=current_user.id).exists():
				return JsonResponse(
					{
						'success': False,
						'type': 'mail',
						'message': _('An Account with this email already exists.'),
					}
				)
		else:
			if User.objects.filter(email=email).exists():
				return JsonResponse(
					{
						'success': False,
						'type': 'mail',
						'message': _('An Account with this email already exists.'),
					}
				)
	if username:
		if len(username.strip()) == 0 or not re.match(r'^\w+$', username):
			return JsonResponse(
				{
					'success': False,
					'type': 'username',
					'message': _(
						'Invalid username. Username must contain only letters, numbers, and underscores, and cannot be empty or contain only whitespace.'
					),
				}
			)
		if current_user:
			if User.objects.filter(username=username).exclude(id=current_user.id).exists():
				return JsonResponse(
					{'success': False, 'type': 'username', 'message': _('Username already taken.')}
				)
		else:
			if User.objects.filter(username=username).exists():
				return JsonResponse(
					{'success': False, 'type': 'username', 'message': _('Username already taken.')}
				)
	return None


@login_required_redirect
def change_password(request):
	"""
	Change the password of the logged in user.
	"""
	if request.method == 'POST':
		data = json.loads(request.body)
		current_password = data.get('current_password')
		new_password = data.get('new_password')

		user = request.user

		if not user.check_password(current_password):
			return JsonResponse({'success': False, 'message': _('Invalid current password.')})
		# If not done automatically, ensure passwords are checked for lenght etc
		user.set_password(new_password)
		user.save()
		update_session_auth_hash(request, user)
		return JsonResponse({'success': True, 'message': _('Password changed successfully.')})
	return JsonResponse({'success': False, 'message': _('Invalid request method.')})


def check_authentication(request):
	"""
	Check if the user is authenticated.
	API Endpoint: /users/api/check_authentication/
	"""
	return JsonResponse({'is_authenticated': request.user.is_authenticated})


@login_required_redirect
def public_profile(request, query_user):
	query_user_instance = User.objects.get(username=query_user)
	pong_games_finished = PongGame.objects.filter(
		player1=query_user_instance, pending=False
	) | PongGame.objects.filter(player2=query_user_instance, pending=False)
	pong_games_won = pong_games_finished.filter(
		player1=query_user_instance, score1__gt=F('score2')
	) | pong_games_finished.filter(player2=query_user_instance, score2__gt=F('score1'))
	pong_games_lost = [game for game in pong_games_finished if game not in pong_games_won]
	pong_games_won = sorted(pong_games_won, key=lambda game: game.played_at, reverse=True)
	pong_games_lost = sorted(pong_games_lost, key=lambda game: game.played_at, reverse=True)
	pong_ratio = win_to_loss_ratio(
		query_user_instance.matches_won, query_user_instance.matches_lost
	)
	return render(
		request,
		'users/public_profile.html',
		{
			'request_user': request.user,
			'query_user': query_user_instance,
			'pong_matches_lost': query_user_instance.matches_lost,
			'pong_matches_won': query_user_instance.matches_won,
			'pong_win_loss_ratio': pong_ratio,
			'games_won': pong_games_won,
			'games_lost': pong_games_lost,
		},
	)
