from django.core.exceptions import ValidationError
from django.test import TestCase

from user_management.blocked_users import Block_Manager, BlockedUsers
from user_management.friends import Friends, Friends_Manager
from user_management.models import CustomUser

User = CustomUser


class FriendsApiTest(TestCase):
	def setUp(self):
		# Create a test user
		self.user = User.objects.create_user(username='testuser', password='testpassword')

		# Authenticate the user
		self.client.login(username='testuser', password='testpassword')

		self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')

	def test_friendships(self):
		response = self.client.get('/users/api/friends/active/', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		expected_json = {'success': True, 'friends_users': []}
		self.assertJSONEqual(response.content.decode('utf-8'), expected_json)
		# check existing user
		response = self.client.get(
			'/users/api/friends/request/testuser2/', content_type='application/json'
		)
		self.assertEqual(response.status_code, 200)
		expected_json = {'success': True, 'message': 'Friend request sent successfully.'}
		self.assertJSONEqual(response.content.decode('utf-8'), expected_json)
		# check non-existent user
		response = self.client.get(
			'/users/api/friends/request/testuser3/', content_type='application/json'
		)
		self.assertJSONEqual(
			response.content.decode('utf-8'),
			{'success': False, 'message': 'The target user does not exist!'},
		)
		self.client.logout()
		self.client.login(username='testuser2', password='testpassword2')
		response = self.client.get('/users/api/friends/inactive/', content_type='application/json')
		self.assertJSONEqual(
			response.content.decode('utf-8'),
			{'success': True, 'received': ['testuser'], 'sent': []},
		)
		response = self.client.get(
			'/users/api/friends/accept/testuser/', content_type='application/json'
		)
		self.assertJSONEqual(
			response.content.decode('utf-8'),
			{'success': True, 'message': 'Friend request accepted.'},
		)
		response = self.client.get('/users/api/friends/active/', content_type='application/json')
		self.assertJSONEqual(
			response.content.decode('utf-8'), {'success': True, 'friends_users': ['testuser']}
		)
		response = self.client.get(
			'/users/api/friends/active/testuser/', content_type='application/json'
		)
		self.assertJSONEqual(
			response.content.decode('utf-8'), {'success': True, 'friends_users': ['testuser2']}
		)
		self.client.logout()
		self.client.login(username='testuser', password='testpassword')
		response = self.client.get(
			'/users/api/friends/remove/testuser2/', content_type='application/json'
		)
		self.assertJSONEqual(
			response.content.decode('utf-8'), {'success': True, 'message': 'Friendship ended.'}
		)
		response = self.client.get('/users/api/friends/active/', content_type='application/json')
		self.assertJSONEqual(
			response.content.decode('utf-8'), {'success': True, 'friends_users': []}
		)


class BlockManagerTest(TestCase):
	def setUp(self):
		# Create test users
		self.user1 = User.objects.create_user(username='user1', password='password1')
		self.user2 = User.objects.create_user(username='user2', password='password2')
		self.user3 = User.objects.create_user(username='user3', password='password3')

	def test_blocked(self):
		Block_Manager.block_user(self.user1, 'user2')
		self.assertTrue(
			BlockedUsers.objects.filter(blocker=self.user1, blockee=self.user2).exists()
		)
		self.assertTrue(
			Block_Manager.is_blocked_by(blockee=self.user2, blocker=self.user1),
		)
		self.assertTrue(
			Block_Manager.has_blocked(blocker=self.user1, blockee=self.user2),
		)
		self.assertTrue(
			Block_Manager.have_block(origin=self.user2, target=self.user1),
			Block_Manager.have_block(origin=self.user1, target=self.user2),
		)

	def test_unblocked(self):
		# Test unblocking a user: origin has to unblock target - blocking can be done by either party and will have multiple instances
		Block_Manager.block_user(self.user1, 'user2')
		Block_Manager.block_user(self.user2, 'user1')
		Block_Manager.unblock_user(self.user1, 'user2')
		self.assertFalse(
			BlockedUsers.objects.filter(blocker=self.user1, blockee=self.user2).exists()
		)
		self.assertTrue(
			BlockedUsers.objects.filter(blocker=self.user2, blockee=self.user1).exists()
		)
		Block_Manager.unblock_user(self.user2, 'user1')
		self.assertFalse(
			BlockedUsers.objects.filter(blocker=self.user1, blockee=self.user2).exists()
		)
		self.assertFalse(
			BlockedUsers.objects.filter(blocker=self.user2, blockee=self.user1).exists()
		)

	def test_cannot_block_oneself(self):
		with self.assertRaises(ValidationError):
			Block_Manager.block_user(self.user1, 'user1')
		self.assertFalse(
			BlockedUsers.objects.filter(blocker=self.user1, blockee=self.user1).exists()
		)


class FriendsManagerTest(TestCase):
	def setUp(self):
		# Create test users
		self.user1 = User.objects.create_user(username='user1', password='password1')
		self.user2 = User.objects.create_user(username='user2', password='password2')
		self.user3 = User.objects.create_user(username='user3', password='password3')

	def test_request(self):
		# Test sending a friend request to another user
		Friends_Manager.request(self.user1, 'user2')
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=False).exists()
		)
		# Test sending a friend request to oneself
		with self.assertRaises(ValidationError):
			Friends_Manager.request(self.user1, 'user1')
		self.assertFalse(
			Friends.objects.filter(origin=self.user1, target=self.user1, accepted=False).exists()
		)
		self.assertFalse(
			Friends.objects.filter(origin=self.user1, target=self.user1, accepted=True).exists()
		)
		# Test sending a second friend request
		with self.assertRaises(ValidationError):
			Friends_Manager.request(self.user1, 'user2')
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=False).exists()
		)
		self.assertFalse(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=True).exists()
		)
		# Test sending a friend request to a non-existent user
		with self.assertRaises(ValidationError):
			Friends_Manager.request(self.user1, 'nonexistentuser')

	def test_cancel_request(self):
		# Test canceling a friend request
		Friends_Manager.request(self.user1, 'user2')
		with self.assertRaises(ValidationError):
			Friends_Manager.cancel_request(self.user2, 'user1')
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=False).exists()
		)
		Friends_Manager.cancel_request(self.user1, 'user2')
		with self.assertRaises(ValidationError):
			Friends_Manager.cancel_request(self.user2, 'nonexistentuser')
		self.assertFalse(Friends.objects.filter(origin=self.user1, target=self.user2).exists())

	def test_deny_request(self):
		# Test denying a friend request
		Friends_Manager.request(self.user1, 'user2')
		Friends_Manager.deny_request(self.user2, 'user1')
		with self.assertRaises(ValidationError):
			Friends_Manager.deny_request(self.user2, 'nonexistentuser')
		with self.assertRaises(ValidationError):
			Friends_Manager.deny_request(self.user1, 'user2')
		self.assertFalse(Friends.objects.filter(origin=self.user1, target=self.user2).exists())

	def test_accept_request(self):
		# Test accepting a friend request
		Friends_Manager.request(self.user1, 'user2')
		Friends_Manager.accept_request(self.user2, 'user1')
		with self.assertRaises(ValidationError):
			Friends_Manager.accept_request(self.user2, 'nonexistentuser')
		with self.assertRaises(ValueError):
			Friends_Manager.accept_request(self.user2, 'user3')
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=True).exists()
		)

	def test_remove_friend(self):
		# Test removing a friend
		Friends_Manager.request(self.user1, 'user2')
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=False).exists()
		)
		Friends_Manager.accept_request(self.user2, 'user1')
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=True).exists()
		)
		Friends_Manager.remove_friend(self.user1, 'user2')
		self.assertFalse(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=True).exists()
		)
		self.assertFalse(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=False).exists()
		)
		# Test removing a friend by any party
		Friends_Manager.request(self.user2, 'user1')
		Friends_Manager.accept_request(self.user1, 'user2')
		Friends_Manager.remove_friend(self.user1, 'user2')
		Friends_Manager.request(self.user2, 'user1')
		Friends_Manager.accept_request(self.user1, 'user2')
		Friends_Manager.remove_friend(self.user2, 'user1')
		# Test removing a non-existent user
		with self.assertRaises(ValidationError):
			Friends_Manager.remove_friend(self.user1, 'nonexistentuser')
		with self.assertRaises(ValueError):
			Friends_Manager.remove_friend(self.user1, 'user3')
		with self.assertRaises(ValueError):
			Friends_Manager.remove_friend(self.user1, 'user2')
		self.assertFalse(Friends.objects.filter(origin=self.user1, target=self.user2).exists())
		self.assertFalse(Friends.objects.filter(origin=self.user2, target=self.user1).exists())

	def test_persistence(self):
		# Test persistence of friendships
		Friends_Manager.request(self.user1, 'user2')
		Friends_Manager.accept_request(self.user2, 'user1')
		# Retrieve the friendship from the database
		friendship = Friends.objects.get(origin=self.user1, target=self.user2)
		self.assertIsNotNone(friendship)
		self.assertTrue(friendship.accepted)
		# Ensure the friendship is still present after a new request
		Friends_Manager.request(self.user1, 'user3')
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user2, accepted=True).exists()
		)
		self.assertTrue(
			Friends.objects.filter(origin=self.user1, target=self.user3, accepted=False).exists()
		)

	def test_status(self):
		# Test friendship status function
		# No friendship
		self.assertEqual(Friends_Manager.status(self.user1, self.user2), (False, None))

		# Request sent from user1 to user2
		Friends_Manager.request(self.user1, 'user2')
		self.assertEqual(Friends_Manager.status(self.user1, self.user2), (False, True))
		self.assertEqual(Friends_Manager.status(self.user2, self.user1), (False, False))

		# Request accepted
		Friends_Manager.accept_request(self.user2, 'user1')
		self.assertEqual(Friends_Manager.status(self.user1, self.user2), (True, None))
		self.assertEqual(Friends_Manager.status(self.user2, self.user1), (True, None))

		# Remove friendship
		Friends_Manager.remove_friend(self.user1, 'user2')
		self.assertEqual(Friends_Manager.status(self.user1, self.user2), (False, None))
		self.assertEqual(Friends_Manager.status(self.user2, self.user1), (False, None))

		# Test same user
		self.assertEqual(Friends_Manager.status(self.user1, self.user1), (False, None))
