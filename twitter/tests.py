from django.test import TestCase, Client
from .models import User, Tweet, UpdateUser, UpdateTweet, DeleteTweet, CreateTweet
from .saved_responses import *
from django.urls import reverse
# Create your tests here.
class CheckIndexView(TestCase):

	@classmethod
	def setUpTestData(cls):
		sa = User.objects.create_user(username="abc", email="abc@gmail.com", password="abcd12345", is_staff=True, is_superuser=True)
		a = User.objects.create_user(username='foo', email='foo@gmail.com', password='abcd12345', is_staff = True)
		u = User.objects.create_user(username='bar', email='bar@gmail.com', password='abcd12345')

	
	def test_AnonymourUserCheck(self):
		c = Client()
		response = c.get('')
		self.assertEqual(response.json(), ANONYMOUS_USER)

	def test_NormalUserCheck(self):
		c = Client()
		c.login(username='bar', password='abcd12345')
		response = c.get('')
		self.assertEqual(response.json(), NORMAL_USER)

	def test_AdminUserCheck(self):
		c = Client()
		c.login(username='foo', password='abcd12345')
		response = c.get('')
		self.assertEqual(response.json(), ADMIN_USER)

	def test_SuperAdminUserCheck(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.get('')
		self.assertEqual(response.json(), SUPER_ADMIN_USER)


class CheckLoginRegisterLogoutView(TestCase):

	@classmethod
	def setUpTestData(cls):
		sa = User.objects.create_user(username="abc", email="abc@gmail.com", password="abcd12345", is_staff=True, is_superuser=True)
		a = User.objects.create_user(username='foo', email='foo@gmail.com', password='abcd12345', is_staff = True)
		u = User.objects.create_user(username='bar', email='bar@gmail.com', password='abcd12345')


	def test_login_success(self):
		c = Client()
		login = c.post('/login', {
				'username': 'foo', 'password': 'abcd12345'
			}, content_type='application/json')
		self.assertRedirects(login, '/')

	def test_login_fail(self):
		c = Client()
		login = c.post('/login', {
				'username': 'foos', 'password': 'abcd12345'
			}, content_type='application/json')
		self.assertEqual(login.json(), {"error": "Invalid username and/or password."})


	def test_logout_success(self):
		c = Client()
		c.login(username='foo', password='abcd12345')
		logout = c.get('/logout')
		self.assertRedirects(logout, '/')


	def test_logout_fail(self):
		c = Client()
		logout = c.get('/logout')
		self.assertRedirects(logout, '/login?next=/logout')

	def test_register_success(self):
		c = Client()
		response = c.post('/register', content_type='application/json', data= {
				'username': 'a', 'password': 'abcd12345', 'confirmation': 'abcd12345', 'email': 'a@gmail.com'
			}, follow = True)
		self.assertEqual(response.json(), NORMAL_USER)

	def test_register_password_match_fail(self):
		c = Client()
		response = c.post('/register', content_type='application/json', data= {
				'username': 'a', 'password': 'abcd12345', 'confirmation': 'abcd123456', 'email': 'a@gmail.com'
			}, follow = True)
		self.assertEqual(response.json(), {"error": "Passwords must match."})

	def test_register_fields_missing(self):
		c = Client()
		response = c.post('/register', content_type='application/json', data= {
				'username': 'a', 'confirmation': 'abcd123456', 'email': 'a@gmail.com'
			}, follow = True)
		self.assertEqual(response.json(), {"error": "Necessary fields like email, password, confirmation are misssing."})

	def test_register_user_exists(self):
		c = Client()
		response = c.post('/register', content_type='application/json', data= {
				'username': 'foo', 'password': 'abcd12345', 'confirmation': 'abcd12345', 'email': 'foo@gmail.com'
			}, follow = True)
		self.assertEqual(response.json(), {'error':'Email/Username address already taken.'})


class CheckUserViews(TestCase):

	@classmethod
	def setUpTestData(cls):
		sa = User.objects.create_user(username="abc", email="abc@gmail.com", password="abcd12345", is_staff=True, is_superuser=True)
		a = User.objects.create_user(username='foo', email='foo@gmail.com', password='abcd12345', is_staff = True)
		u = User.objects.create_user(username='bar', email='bar@gmail.com', password='abcd12345')
		cls.tweets=[]
		for i in range(10):
			cls.tweets.append(Tweet.objects.create(user=u, tweet='Hello there !!! {}'.format(i)))
		

	def test_user_profile_success(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.get('/user/profile')
		self.assertEqual(response.json()['username'], 'bar')

	def test_user_tweets_success(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.get('/user/tweets')
		self.assertEqual(len(response.json()), 10)

	def test_edit_tweets_not_present(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.put('/edittweet', {
				'tweet_id': 20, 'new_tweet': "hi there",
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "tweet not present"})

	def test_edit_tweet_success(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.put('/edittweet', {
				'tweet_id': self.tweets[2].id, 'new_tweet': 'hi there'
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)


	def test_delete_tweets_not_present(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.put('/deletetweet', {
				'tweet_id': 20, 'new_tweet': "hi there",
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "tweet not present"})

	def test_delete_tweet_success(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.put('/deletetweet', {
				'tweet_id': self.tweets[5].id,
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)

	def test_new_tweet_success(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.post('/newtweet', {
				'tweet': "Hello from other side"
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)

	def test_new_tweet_cannot_be_empty(self):
		client = Client()
		client.login(username='bar', password='abcd12345')
		response = client.post('/newtweet', {
				'tweet': ""
			}, content_type='application/json')
		self.assertEqual(response.json(), {'error': "tweet cannot be empty."})


class CheckAdminViews(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.sa = User.objects.create_user(username="abc", email="abc@gmail.com", password="abcd12345", is_staff=True, is_superuser=True)
		cls.a1 = User.objects.create_user(username='foo1', email='foo1@gmail.com', password='abcd12345', is_staff = True)
		cls.a2 = User.objects.create_user(username='foo2', email='foo2@gmail.com', password='abcd12345', is_staff = True)
		cls.u1 = User.objects.create_user(username='bar1', email='bar1@gmail.com', password='abcd12345')
		cls.u2 = User.objects.create_user(username='bar2', email='bar2@gmail.com', password='abcd12345')
		cls.tweets_u1=[]
		for i in range(10):
			cls.tweets_u1.append(Tweet.objects.create(user=cls.u1, tweet='Hello there !!! {}'.format(i)))
		cls.tweets_u2=[]
		for i in range(5):
			cls.tweets_u2.append(Tweet.objects.create(user=cls.u2, tweet='Hi there !!! {}'.format(i)))

	def test_all_user_profile_view(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.get('/all/user/profile')
		self.assertEqual(len(response.json()), 2)

	def test_access_other_user_profile_success(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.get(reverse('userprofile', args=[self.u1.id]))
		self.assertEqual(response.json()['username'], 'bar1')

	def test_access_other_user_profile_failed(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.get(reverse('userprofile', args=[self.sa.id]))
		self.assertEqual(response.json(), BAD_REQUEST)

	def test_access_user_tweets_success(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.get(reverse('usertweets', args=[self.u1.id]))
		self.assertEqual(len(response.json()['tweets']), 10)

	def test_access_user_tweets_failed(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.get(reverse('usertweets', args=[self.a2.id]))
		self.assertEqual(response.json(), BAD_REQUEST)

	def test_update_tweet_request_success(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('update_tweet_request'), {
				"tweet_id": self.tweets_u2[0].id, 'new_tweet': "update from admin"
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)

	def test_update_tweet_request_failed(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('update_tweet_request'), {
				"tweet_id": 100, 'new_tweet': "update from admin"
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "tweet not present."})

	def test_delete_tweet_request_success(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('delete_tweet_request'), {
				"tweet_id": self.tweets_u1[5].id,
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)

	def test_delete_tweet_request_failed(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('delete_tweet_request'), {
				"tweet_id": 100,
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "tweet not present."})


	def test_create_tweet_request_success(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('create_tweet_request'), {
				"user_id": self.u1.id, 'tweet': 'new tweet from admin.'
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)

	def test_create_tweet_request_user_not_present(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('create_tweet_request'), {
				"user_id": 100, 'tweet': 'new tweet from admin.'
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "user not present."})

	def test_create_tweet_request_not_have_access(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('create_tweet_request'), {
				"user_id": self.sa.id, 'tweet': 'new tweet from admin.'
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "not have access to tweet from this user."})


	def test_create_tweet_request_tweet_not_present(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('create_tweet_request'), {
				"user_id": self.u1.id, 'tweet': ''
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "tweet not present."})

	def test_update_user_request_success(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('update_user_request'), {
				"user_id": self.u2.id, 'new_bio': 'User 1'
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)

	def test_update_user_request_no_field_provided(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.post(reverse('update_user_request'), {
				"user_id": self.u1.id,
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "Provide atleast one updated field."})


class CheckSuperAdminViews(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.sa = User.objects.create_user(username="abc", email="abc@gmail.com", password="abcd12345", is_staff=True, is_superuser=True)
		cls.a1 = User.objects.create_user(username='foo1', email='foo1@gmail.com', password='abcd12345', is_staff = True)
		cls.a2 = User.objects.create_user(username='foo2', email='foo2@gmail.com', password='abcd12345', is_staff = True)
		cls.u1 = User.objects.create_user(username='bar1', email='bar1@gmail.com', password='abcd12345')
		cls.u2 = User.objects.create_user(username='bar2', email='bar2@gmail.com', password='abcd12345')
		cls.tweets_u1=[]
		for i in range(10):
			cls.tweets_u1.append(Tweet.objects.create(user=cls.u1, tweet='Hello there !!! {}'.format(i)))
		cls.tweets_u2=[]
		for i in range(5):
			cls.tweets_u2.append(Tweet.objects.create(user=cls.u2, tweet='Hi there !!! {}'.format(i)))

		cls.update_tweets=[]
		for i in range(4):
			cls.update_tweets.append(UpdateTweet.objects.create(admin=cls.a1, tweet=cls.tweets_u1[i], new_tweet="Update from admin {}".format(i)))

		cls.delete_tweets=[]
		for i in range(4):
			cls.delete_tweets.append(DeleteTweet.objects.create(admin=cls.a1, tweet=cls.tweets_u1[i+5]))

		cls.create_tweets=[]
		for i in range(4):
			cls.create_tweets.append(CreateTweet.objects.create(admin=cls.a1, userid=cls.u2.id, tweet="New tweet created from admin {}".format(i)))

		cls.update_user=[]
		cls.update_user.append(UpdateUser.objects.create(admin=cls.a1, user=cls.u1, new_bio="bio updated from admin"))
		cls.update_user.append(UpdateUser.objects.create(admin=cls.a1, user=cls.u2, new_bio="bio updated from admin"))

	def test_accessing_user_update_requests_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.get(reverse('request_user'))
		self.assertEqual(len(response.json()), 2)

	def test_accessing_user_update_requests_failed(self):
		c = Client()
		c.login(username='foo1', password='abcd12345')
		response = c.get(reverse('request_user'))
		self.assertEqual(response.json(), BAD_REQUEST)


	def test_accessing_tweet_requests_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.get(reverse('request_tweets'))
		self.assertEqual(len(response.json()['create_request']), 4)
		self.assertEqual(len(response.json()['update_request']), 4)
		self.assertEqual(len(response.json()['delete_request']), 4)

	def test_responding_user_update_request_id_not_present(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_users'), [{
			"request_id": 9, 'action_granted': False
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": 9, 'error': 'Id not present.'
			}])


	def test_responding_user_update_request_rejected_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_users'), [{
			"request_id": self.update_user[0].id, 'action_granted': False
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.update_user[0].id, 'message': 'Response saved.'
			}])


	def test_responding_user_update_request_granted_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_users'), [{
			"request_id": self.update_user[1].id, 'action_granted': True
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.update_user[1].id, 'message': 'Response saved.'
			}])


	def test_responding_tweet_update_request_rejected_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_tweets_update'), [{
			"request_id": self.update_tweets[0].id, 'action_granted': False
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.update_tweets[0].id, 'message': 'Response saved.'
			}])

	def test_responding_tweet_update_request_granted_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_tweets_update'), [{
			"request_id": self.update_tweets[1].id, 'action_granted': True
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.update_tweets[1].id, 'message': 'Response saved.'
			}])

	def test_responding_tweet_delete_request_rejected_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_tweets_delete'), [{
			"request_id": self.delete_tweets[0].id, 'action_granted': False
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.delete_tweets[0].id, 'message': 'Response saved.'
			}])

	def test_responding_tweet_delete_request_granted_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_tweets_delete'), [{
			"request_id": self.delete_tweets[1].id, 'action_granted': True
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.delete_tweets[1].id, 'message': 'Response saved.'
			}])

	def test_responding_tweet_create_request_rejected_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_tweets_create'), [{
			"request_id": self.create_tweets[0].id, 'action_granted': False
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.create_tweets[0].id, 'message': 'Response saved.'
			}])

	def test_responding_tweet_create_request_granted_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.put(reverse('respond_tweets_create'), [{
			"request_id": self.create_tweets[1].id, 'action_granted': True
			}], content_type='application/json')
		self.assertEqual(response.json(), [{"request_id": self.create_tweets[1].id, 'message': 'Response saved.'
			}])

	def test_accessing_logs_view(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.get(reverse('logs'))
		self.assertNotEqual(response.json(), REQUEST_FAILED)

	def test_query_logs_failed_no_query(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.post(reverse('logs_query'), {
				"show_logs": True
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "No query present in request."})

	def test_query_logs_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.post(reverse('logs_query'), {
				"show_logs": True, "query": {"source": self.sa.username}
			}, content_type='application/json')
		self.assertNotEqual(response.json()['count'], 0)
		self.assertNotEqual(len(response.json()['logs']), 0)

	def test_register_new_admin_success(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.post(reverse('register_admin'), {
				"username": 'foo3', 'email': 'foo3@gmail.com', 'password': 'abcd12345', 'confirmation': 'abcd12345', 'is_admin': True, 'bio': "Admin created by superuser."
			}, content_type='application/json')
		self.assertEqual(response.json(), REQUEST_SUCCESS)


	def test_register_new_admin_username_already_taken(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.post(reverse('register_admin'), {
				"username": 'foo1', 'email': 'foo1@gmail.com', 'password': 'abcd12345', 'confirmation': 'abcd12345', 'is_admin': True, 'bio': "Admin created by superuser."
			}, content_type='application/json')
		self.assertEqual(response.json(), {'error':'Email/Username address already taken.'})

	def test_register_new_admin_fields_missing(self):
		c = Client()
		c.login(username='abc', password='abcd12345')
		response = c.post(reverse('register_admin'), {
				"username": 'foo3', 'password': 'abcd12345', 'confirmation': 'abcd12345', 'is_admin': True, 'bio': "Admin created by superuser."
			}, content_type='application/json')
		self.assertEqual(response.json(), {"error": "Necessary fields like email, password, confirmation are misssing."})