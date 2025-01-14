from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.db.models import F
from .models import Profile, User
from game.models import Game


def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			user = form.save()  # Only saves the User instance; Profile creation is handled by the signal
			username = form.cleaned_data.get('username')
			messages.success(request, f'Your account has been created! You can now log in!')
			return redirect('login')
	else:
		form = UserRegisterForm()
	
	return render(request, 'users/register.html', {'form': form})



from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

#costum Logout, couse Idk I am stupid to get the normal working
def custom_logout(request):
	logout(request)  # Logs out the user
	return render(request, 'users/logout.html') # Redirects the user to the login page

@login_required
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		mod_pwd_form = PasswordChangeForm(request.user, request.POST)
		if u_form.is_valid() and p_form.is_valid() and mod_pwd_form.is_valid():
			u_form.save()
			p_form.save()
			user = mod_pwd_form.save()
			update_session_auth_hash(request, user)
			messages.success(request, f'Your account has been updated')
			return redirect('profile')

	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)
		mod_pwd_form = PasswordChangeForm(request.user)

	context = {
		'u_form': u_form,
		'p_form': p_form,
		'mod_pwd_form': mod_pwd_form,
	}

	return render(request, 'users/profile.html', context)

@login_required
def public_profile(request, query_user):
	user_instance = User.objects.get(username=query_user)
	user_profile = Profile.objects.get(user=user_instance)
	games = Game.objects.filter(player1=user_profile.player) | Game.objects.filter(player2=user_profile.player)
	games_won = games.filter(player1=user_profile.player, score1__gt=F('score2')) | games.filter(player2=user_profile.player, score2__gt=F('score1'))
	games_lost = [game for game in games if game not in games_won]
	games_won = sorted(games_won, key=lambda game: game.played_at, reverse=True)
	games_lost = sorted(games_lost, key=lambda game: game.played_at, reverse=True)
	return render(request, 'users/public_profile.html', {'user_profile': user_profile, 'games': games, 'games_won': games_won, 'games_lost': games_lost})
