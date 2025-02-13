from django.db import models
from django.forms import ValidationError

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
	# origin should be the request user, target is their request
	# origin_username and target_username are their usernames
	@staticmethod
	def friends_request(origin, target_username):
		"""User instance, target username"""
		target_friend = Friends_Manager.__get_existing_user_instance(target_username)
		if target_friend == origin:
			raise ValidationError('You cannot befriend yourself!')
		if Friends.objects.filter(origin=target_friend, target=origin).exists():
			raise ValidationError(
				'there is already a friends request from this user for you to accept.'
			)
		if Friends.objects.filter(origin=origin, target=target_friend, accepted=True).exists():
			raise ValidationError('There is already a friendship between these users')
		elif Friends.objects.filter(origin=origin, target=target_friend, accepted=False).exists():
			raise ValidationError(
				'you cannot request the same user again, wait for your request to be handled'
			)
		Friends.objects.create(origin=origin, target=target_friend, accepted=False)

	# cancel the request as origin
	@staticmethod
	def cancel_friends_request(origin, target_username):
		"""User instance, target username"""
		target = Friends_Manager.__get_existing_user_instance(target_username)
		try:
			Friends_Manager.__delete_instance(
				Friends.objects.filter(origin=origin, target=target, accepted=False).first()
			)
		except ValueError:
			raise ValidationError('you did not send the friend request, you can only deny it!')

	# deny request as target
	@staticmethod
	def deny_friends_request(target, origin_username):
		"""User instance (target), origin username: deny"""
		origin = Friends_Manager.__get_existing_user_instance(origin_username)
		request = Friends.objects.filter(origin=origin, target=target, accepted=False).first()
		if request is None:
			raise ValidationError('There is no request to deny')
		try:
			Friends_Manager.__delete_instance(request)
		except ValueError:
			raise ValidationError('you sent the friend request, you can only cancel it!')

	# accept request as target
	@staticmethod
	def accept_request_as_target(target, origin_username):
		"""User instance (target), origin username: accept"""
		origin = Friends_Manager.__get_existing_user_instance(origin_username)
		Friends_Manager.__create_friendship(
			Friends.objects.filter(origin=origin, target=target, accepted=False).first()
		)

	# delete a friendship from either side
	@staticmethod
	def remove_friend(remover, target_username):
		"""either User instance, other username: remove"""
		target = Friends_Manager.__get_existing_user_instance(target_username)
		Friends_Manager.__delete_instance(
			friendship=Friends.objects.filter(origin=remover, target=target, accepted=True).first()
			or Friends.objects.filter(origin=target, target=remover, accepted=True).first()
		)

	# this is only called in a user (self-serving) context
	def fetch_received(target):
		"""receiver User instance: get inactive (not yet accepted)"""
		origin_users = set()
		requests_received = Friends_Manager.__get_requests_received(user_instance=target)
		for received in requests_received:
			origin_users.add(received.origin)
		return origin_users

	# requests can be accepted/denied
	def __get_requests_received(user_instance):
		return Friends.objects.filter(target=user_instance, accepted=False)

	# this can be called by sender/origin user to cancel the request
	def fetch_sent(origin):
		"""sender User instance: get inactive (not yet accepted)"""
		target_users_cancelable = set()
		requests_sent = Friends_Manager.__get_requests_sent(user_instance=origin)
		for sent in requests_sent:
			target_users_cancelable.add(sent.target)
		return target_users_cancelable

	# requests can be canceled
	def __get_requests_sent(user_instance):
		return Friends.objects.filter(origin=user_instance, accepted=False)

	# internal
	def __get_existing_user_instance(string_target_friend):
		if not User.objects.filter(username=string_target_friend).exists():
			raise ValidationError('The target user does not exist!')
		return User.objects.get(username=string_target_friend)

	def __delete_instance(friendship):
		if friendship:
			friendship.delete()
		else:
			raise ValueError('the friendship you are trying to delete does not exist')

	def __create_friendship(friendship):
		if friendship:
			friendship.accepted = True
			friendship.save()
			# some sort of confirmation for the user @todo
		else:
			raise ValueError('the request you are trying to accept does not exist')
