from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext

from .models import CustomUser

User = CustomUser


class Friends(models.Model):
	origin = models.ForeignKey(User, models.CASCADE)
	target = models.ForeignKey(User, models.CASCADE, related_name='target_for_friends')
	accepted = models.BooleanField(default=False)

	def __hash__(self):
		return hash((self.origin, self.target))

	def __eq__(self, other):
		return (self.origin, self.target) == (other.origin, other.target)


class Friends_Manager:
	@staticmethod
	def status(request_user, target_user):
		"""User instance, target instance: returns a tuple of (friendship: yes/no, None/pending request(from/to))"""
		if request_user == target_user:
			return (False, None)
		from_user = Friends.objects.filter(origin=request_user, target=target_user)
		to_user = Friends.objects.filter(origin=target_user, target=request_user)
		if from_user.filter(accepted=True).exists() or to_user.filter(accepted=True).exists():
			return (True, None)
		elif from_user.filter(accepted=False).exists():
			return (False, True)
		elif to_user.filter(accepted=False).exists():
			return (False, False)
		return (False, None)

	@staticmethod
	def count_friends(user):
		"""User instance: returns the number of friends the user has"""
		return Friends.objects.filter(
			models.Q(origin=user) | models.Q(target=user),
			accepted=True
		).count()

	@staticmethod
	# send a friend request
	def request(origin, target_username):
		"""User instance, target username"""
		target_friend = Friends_Manager.__get_existing_user_instance(target_username)
		if target_friend == origin:
			raise ValidationError(gettext('You cannot befriend yourself!'))
		elif (
			Friends.objects.filter(origin=target_friend, target=origin).exists()
			or Friends.objects.filter(origin=origin, target=target_friend, accepted=False).exists()
		):
			raise ValidationError(gettext('Friend request pending approval.'))
		if Friends.objects.filter(origin=origin, target=target_friend, accepted=True).exists():
			raise ValidationError(gettext('You are already friends!'))
		Friends.objects.create(origin=origin, target=target_friend, accepted=False)

	# cancel the request as origin
	@staticmethod
	def cancel_request(origin, target_username):
		"""User instance, target username"""
		target = Friends_Manager.__get_existing_user_instance(target_username)
		try:
			Friends_Manager.__delete_instance(
				Friends.objects.filter(origin=origin, target=target, accepted=False).first()
			)
		except ValueError:
			raise ValidationError(
				gettext('you did not send the friend request, you can only deny it!')
			)

	# deny request as target
	@staticmethod
	def deny_request(target, origin_username):
		"""User instance (target), origin username: deny"""
		origin = Friends_Manager.__get_existing_user_instance(origin_username)
		request = Friends.objects.filter(origin=origin, target=target, accepted=False).first()
		if request is None:
			raise ValidationError(gettext('There is no request to deny'))
		try:
			Friends_Manager.__delete_instance(request)
		except ValueError:
			raise ValidationError(gettext('you sent the friend request, you can only cancel it!'))

	# accept request as target
	@staticmethod
	def accept_request(target, origin_username):
		"""User instance (target), origin username: accept"""
		origin = Friends_Manager.__get_existing_user_instance(origin_username)
		friendship = Friends.objects.filter(origin=origin, target=target, accepted=False).first()
		if friendship:
			friendship.accepted = True
			friendship.save()
		else:
			raise ValueError(gettext('the request you are trying to accept does not exist'))

	# delete a friendship from either side
	@staticmethod
	def remove_friend(remover, target_username):
		"""either User instance, other username: remove"""
		target = Friends_Manager.__get_existing_user_instance(target_username)
		Friends_Manager.__delete_instance(
			friendship=Friends.objects.filter(origin=remover, target=target, accepted=True).first()
			or Friends.objects.filter(origin=target, target=remover, accepted=True).first()
		)

	# internal
	def __get_existing_user_instance(string_target_friend):
		if not User.objects.filter(username=string_target_friend).exists():
			raise ValidationError(gettext('The target user does not exist!'))
		return User.objects.get(username=string_target_friend)

	def __delete_instance(friendship):
		if friendship:
			friendship.delete()
		else:
			raise ValueError(gettext('the friendship you are trying to delete does not exist'))
