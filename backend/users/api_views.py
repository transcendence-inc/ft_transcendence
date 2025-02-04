from urllib.parse import urlencode

import django.shortcuts
import requests
from django.contrib.auth import login

# import rest_framework
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import OAuth_Manager, OAuthUsers


class CreateOAUTHUserView(APIView):
	permission_classes = [AllowAny]
	OAUTH_CALLBACK = 'http://localhost:8000/users/oauth/callback'
	from transcendence.settings import CLIENT_ID, REMOTE_OAUTH_SECRET, SECRET_STATE

	def request_login_oauth(self):
		"""request user login on API endpoint"""
		params = {
			'client_id': CreateOAUTHUserView.CLIENT_ID,
			'redirect_uri': CreateOAUTHUserView.OAUTH_CALLBACK,
			'response_type': 'code',
			'state': CreateOAUTHUserView.SECRET_STATE,
			'scope': 'public',
		}

		auth_url = f'https://api.intra.42.fr/oauth/authorize?{urlencode(params)}'

		return django.shortcuts.redirect(auth_url)

	def __bearer_token(self, request):
		"""exchange the code for a users' bearer token"""
		from transcendence.settings import SECRET_STATE

		code = request.GET.get('code')
		state = request.GET.get('state')
		if code is None:
			return HttpResponse('Error: user did not authorize the app')
		if state != SECRET_STATE:
			return HttpResponse('Error: state mismatch')

		params = {
			'grant_type': 'authorization_code',
			'client_id': CreateOAUTHUserView.CLIENT_ID,
			'client_secret': CreateOAUTHUserView.REMOTE_OAUTH_SECRET,
			'code': code,
			'redirect_uri': CreateOAUTHUserView.OAUTH_CALLBACK,
			'state': CreateOAUTHUserView.SECRET_STATE,
		}

		bearer_token_response = requests.post(
			f'https://api.intra.42.fr/oauth/token?{urlencode(params)}'
		)
		# Error: could not exchange code for token
		bearer_token_response.raise_for_status()
		return bearer_token_response.json()

	def create_user(request, jsonresponse, BEARER_TOKEN, REFRESH_TOKEN):
		"""handle user management from oauth"""
		already_exists = OAuthUsers.objects.filter(login=jsonresponse['login'])
		if not already_exists.exists():
			# create the account
			user = OAuth_Manager.create_user(jsonresponse['login'], jsonresponse['email'])
		already_exists = OAuthUsers.objects.filter(login=jsonresponse['login'])
		user = already_exists.first()
		# log the user into the account - this took way longer than it should have
		print(user.instance)
		# user = authenticate(request, username=user.instance)
		# WIP: this is not working with @login_required
		login(request, user.instance, backend='django.contrib.auth.backends.RemoteUserBackend')
		from .views import public_profile

		return public_profile(request, jsonresponse['login'])

	def get(self, request):
		"""handle the callback from the 42 API: obtain user public data"""
		bearer_token_response = CreateOAUTHUserView.__bearer_token(self, request)
		BEARER_TOKEN = bearer_token_response.get('access_token')
		REFRESH_TOKEN = bearer_token_response.get('refresh_token')
		if BEARER_TOKEN is None:
			return HttpResponse('Error: bearer token invalid/not found')
		response = requests.get(
			'https://api.intra.42.fr/v2/me',
			headers={
				'Content-Type': 'application/x-www-form-urlencoded',
				'Authorization': f'Bearer {BEARER_TOKEN}',
			},
		)
		if not response.ok:
			django.contrib.messages.error(request, 'user did not authorize')
			return django.shortcuts.redirect('users:login')
		jsonresponse = response.json()
		username, email = jsonresponse['login'], jsonresponse['email']
		if username is None or email is None:
			return HttpResponse('Error: could not obtain username from token')
		return CreateOAUTHUserView.create_user(request, jsonresponse, BEARER_TOKEN, REFRESH_TOKEN)
