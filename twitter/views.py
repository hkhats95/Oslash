import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Tweet, UpdateTweet, DeleteTweet, CreateTweet, UpdateUser
from .saved_responses import *
import logging
import pythonjsonlogger
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

#Initializing logger
logger = logging.getLogger('twitter_logs')

# Create your views here.
#default view
def index(request):
	if request.user.is_authenticated:
		u = request.user
		#Show relevant urls to each user
		if u.is_superuser:
			return JsonResponse(SUPER_ADMIN_USER, safe=False)
		elif u.is_staff:
			return JsonResponse(ADMIN_USER, safe=False)
		else:
			return JsonResponse(NORMAL_USER, safe=False)
	else:
		return JsonResponse(ANONYMOUS_USER, safe=False)


#Login controller
@csrf_exempt
def login_view(request):
	if request.method == 'POST':

		data = json.loads(request.body.decode('utf-8'))
		
		# Attempt to log user in
		username = data.get('username', '')
		password = data.get('password', '')
		user = authenticate(request, username=username, password=password)

		# Check if authentication successful
		if user is not None:
			login(request, user)
			#log
			logger.info('{} logs in'.format(user.username), extra={'source': user.username, 'log_type': 'access'})
			return HttpResponseRedirect(reverse('index'))
		else:
			return JsonResponse({"error": "Invalid username and/or password."})
	return JsonResponse({
		"message": "Please login to continue.",
		"method": "POST",
		"body": {
			"username": "user_name",
			"password": "password",
			}
		})


#Logout controller
@login_required(login_url='/login')
def logout_view(request):
	#log
	logger.info('{} logs out'.format(request.user.username), extra={'source': request.user.username, 'log_type': 'access'})
	logout(request)
	return HttpResponseRedirect(reverse('index'))


#Create new profile as a user
@csrf_exempt
def register(request):
	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		#Check if all the necessary fields are present
		if not (data.get('email', False) and data.get('password', False) and data.get('confirmation', False)):
			return JsonResponse({"error": "Necessary fields like email, password, confirmation are misssing."})

		email = data.get('email')
		username = data.get('email')
		if data.get('username') is not None:
			username = data['username']

		# Ensure password matches confirmation
		password = data.get('password')
		confirmation = data.get('confirmation')
		if password != confirmation:
			return JsonResponse({"error": "Passwords must match."})

		# Attempt to create new user
		try:
			user = User.objects.create_user(username, email, password)
			if data.get('first_name') is not None:
				user.first_name = data['first_name']
			if data.get('last_name') is not None:
				user.last_name = data['last_name']
			if data.get('bio') is not None:
				user.bio = data['bio']
			user.save()
			login(request, user)

			#log
			logger.info('{} signs up'.format(user.username), extra={'source': user.username, 'log_type': 'access'})
			#log
			logger.info('{} logs in'.format(user.username), extra={'source': user.username, 'log_type': 'access'})
			return HttpResponseRedirect(reverse('index'))
		except IntegrityError as e:
			return JsonResponse({'error':'Email/Username address already taken.'})
	else:
		return JsonResponse({
			"method": "POST",
			"body": {
				"username": "user_name",
				"email": "email",
				"password": "password",
				"confirmation": "repeat password",
				"first_name": "first_name",
				"last_name": "last_name",
				"bio": "bio",
			}
		})


#Superadmin creating new profile
@csrf_exempt
@login_required(login_url='/login')
def register_admin(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method=="POST":
		data = json.loads(request.body.decode('utf-8'))

		#Check if all the necessary fields are present
		if not (data.get('email', False) and data.get('password', False) and data.get('confirmation', False)):
			return JsonResponse({"error": "Necessary fields like email, password, confirmation are misssing."})

		email = data.get('email')
		username = data.get('email')
		if data.get('username') is not None:
			username = data['username']

		# Ensure password matches confirmation
		password = data.get('password')
		confirmation = data.get('confirmation')
		if password != confirmation:
			return JsonResponse({"error": "Passwords must match."})

		# Attempt to create new user
		try:
			user = User.objects.create_user(username, email, password)
			if data.get('first_name') is not None:
				user.first_name = data['first_name']
			if data.get('last_name') is not None:
				user.last_name = data['last_name']
			if data.get('bio') is not None:
				user.bio = data['bio']
			if data.get('is_admin', False):
				user.is_staff = True
			if data.get('is_superadmin', False):
				user.is_superuser = True
			user.save()

			#log
			logger.info('Superadmin:{} signs up {}'.format(u.username, user.username), extra={'source': u.username, 'log_type': 'access', 'object': 'user:{}'.format(user.username)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except IntegrityError as e:
			return JsonResponse({'error':'Email/Username address already taken.'})

	else:
		return JsonResponse({
				"method": "POST",
				"body": {
					"username": "user_name",
					"email": "email",
					"password": "password",
					"confirmation": "repeat password",
					"first_name": "first_name",
					"last_name": "last_name",
					"bio": "bio",
					"is_admin": "true or false without quotes",
					"is_superadmin": "true or false without quotes",
				},
			})


#Personal details
@login_required(login_url='/login')
def profile(request):
	u = request.user
	#log
	logger.info('{} visits profile page'.format(u.username), extra={'source': u.username, 'log_type': 'access'})
	return JsonResponse(u.serialize(), safe=False)


#User tweets
@login_required(login_url='/login')
def stweets(request):
	u = request.user

	#Only user allowed to post tweet
	if u.is_staff or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	#Getting all the tweets made by user in sorted order
	tweets = Tweet.objects.filter(user=u).order_by("-timestamp").all()

	#log
	logger.info('User:{} visits tweets page'.format(u.username), extra={'source': u.username, 'log_type': 'access'})
	return JsonResponse([tweet.serialize() for tweet in tweets], safe=False)


#Admin accessing all user profiles
@login_required(login_url='/login')
def alluserprofile(request):
	u = request.user

	if (not u.is_staff) or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)
	
	#Get all user profiles
	users = User.objects.filter(is_staff=False, is_superuser=False).all()

	#log
	logger.info('Admin:{} accessing all user profiles.'.format(u.username), extra={'source': u.username, 'log_type': 'access',})
	return JsonResponse([user.serialize() for user in users], safe=False)


#Admin accessing user details
@login_required(login_url='/login')
def userprofile(request, user_id):
	u = request.user
	try:
		user = User.objects.get(id=user_id)

	#user not found
	except:
		return JsonResponse({"error": "user does not exist."})

	#admin is accessing some user profile
	if (u.id != user_id) and (u.is_staff and (not u.is_superuser) and (not user.is_staff) and (not user.is_superuser)):

		#log
		logger.info('Admin:{} accesses User:{} profile'.format(u.username, user.username), extra={'source': u.username, 'log_type': 'access', 'object': 'user:{}'.format(user.username)})
		return JsonResponse(user.serialize(), safe=False)

	#Bad request
	else:
		return JsonResponse(BAD_REQUEST, safe=False)


#Admin accessing tweets posted by some user
@login_required(login_url='/login')
def usertweets(request, user_id):
	u = request.user
	try:
		user = User.objects.get(id=user_id)

	# user not found
	except:
		return JsonResponse({"error": "user does not exist."})

	#admin accessing some other user tweets
	if (u.id != user_id) and (u.is_staff and (not u.is_superuser) and (not user.is_staff) and (not user.is_superuser)):
		tweets = Tweet.objects.filter(user=user).order_by("-timestamp").all()

		#log
		logger.info('Admin:{} accesses User:{} tweets'.format(u.username, user.username), extra={'source': u.username, 'log_type': 'access', 'object': 'user:{}'.format(user.username)})
		return JsonResponse({
		 	"tweets": [tweet.serialize() for tweet in tweets],
			}, safe=False)
	
	#Bad request
	else:
		return JsonResponse(BAD_REQUEST, safe=False)


#User posting new tweet
@csrf_exempt
@login_required(login_url='/login')
def new_tweet(request):
	user = request.user

	#Only user allowed to tweet
	if user.is_staff or user.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		# Check for empty tweet
		tweet = data.get('tweet')
		if not tweet:
			return JsonResponse({'error': "tweet cannot be empty."})

		# Check for tweet charlength
		tweet = tweet.strip()
		tlen = len(tweet)
		if tlen == 0 or tlen>280:
			return JsonResponse({'error': "tweet must be less than or equal to 280 characters and must not be empty"})

		#Attempt to create new tweet
		try:
			t = Tweet.objects.create(user=user, tweet=tweet)

			#log
			logger.info('User:{} posted new tweet with id:{}'.format(user.username, t.id), extra={'source': user.username, 'log_type': 'action', 'object': 'tweet:{}'.format(t.id)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)

	else:
		return JsonResponse({
				"method": "POST",
				"body": {
					"tweet": "tweet",
				},
			})


#User editing his tweet
@csrf_exempt
@login_required(login_url='/login')
def edit_tweet(request):
	u = request.user

	#Only user allowed to edit
	if u.is_staff or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "PUT":
		data = json.loads(request.body.decode('utf-8'))

		#Check if this tweet_id is valid
		try:
			tweet = Tweet.objects.get(id=data.get('tweet_id'))
		except:
			return JsonResponse({"error": "tweet not present"})

		#Check if this user is owner of this tweet
		user = tweet.user
		if u.id != user.id:
			return JsonResponse({"error": "Access denied to this tweet."})

		#Check whether new_tweet is valid
		new_tweet = data.get('new_tweet', '')
		if len(new_tweet)==0 or len(new_tweet)>280:
			return JsonResponse({'error': "tweet must be less than or equal to 280 characters and must not be empty"})

		#Attempt to update tweet
		try:
			tweet.tweet = new_tweet
			tweet.save()

			#log
			logger.info('User:{} edited his tweet with id:{}'.format(u.username, tweet.id), extra={'source': u.username, 'log_type': 'audit', 'object': 'tweet:{}'.format(tweet.id)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)

	else:
		return JsonResponse({
				"method": "PUT",
				"body": {
					"tweet_id": "<int: tweet_id>",
					"new_tweet": "new_tweet",
				},
			})


#User deleting his tweet
@csrf_exempt
@login_required(login_url='/login')
def delete_tweet(request):
	u = request.user

	#Only user allowed to delete
	if u.is_staff or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "PUT":
		data = json.loads(request.body.decode('utf-8'))

		#Check if tweet_id is valid
		try:
			tweet = Tweet.objects.get(id=data.get('tweet_id'))
		except:
			return JsonResponse({"error": "tweet not present"})

		#Check if this user is owner of this tweet
		user = tweet.user
		if u.id != user.id:
			return JsonResponse({"error": "Access denied to this tweet."})

		#Attempt to delete
		try:
			t_id = tweet.id
			tweet.delete()

			#log
			logger.info('User:{} deleted his tweet with id:{}'.format(u.username, t_id), extra={'source': u.username, 'log_type': 'audit', 'object': 'tweet:{}'.format(t_id)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)

	else:
		return JsonResponse({
				"method": "PUT",
				"body": {
					"tweet_id": "<int: tweet_id>",
				},
			})


#Admin makes a request to update a tweet
@csrf_exempt
@login_required(login_url='/login')
def update_tweet_request(request):
	u = request.user

	#Only admin allowed to make a request
	if (not u.is_staff) or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		#Check if tweet_id is valid
		try:
			tweet = Tweet.objects.get(id=data.get('tweet_id'))
		except:
			return JsonResponse({"error": "tweet not present."})

		#Check if new_tweet is valid
		new_tweet = data.get('new_tweet')
		if not new_tweet:
			return JsonResponse({"error": "tweet cannot be empty."})

		new_tweet = new_tweet.strip()
		if len(new_tweet)>280 or len(new_tweet)==0:
			return JsonResponse({"error": "tweet must be less than or equal to 280 characters and must not be empty."})

		#Attempt to save update request
		try:
			ut = UpdateTweet.objects.create(
					admin = u,
					tweet = tweet,
					new_tweet = new_tweet
				)

			#log
			logger.info('Admin:{} requested an update of tweet with id:{}'.format(u.username, tweet.id), extra={'source': u.username, 'log_type': 'action', 'object': 'tweet:{}'.format(tweet.id)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)
	else:
		return JsonResponse({
			"method": "POST",
			"body":{
				"tweet_id":"<int: tweet_id>",
				"new_tweet":"updated_tweet",
				},
			})


#Admin makes a request to delete a tweet
@csrf_exempt
@login_required(login_url='/login')
def delete_tweet_request(request):
	u = request.user

	#Only admin allowed to make a request
	if (not u.is_staff) or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		#Check if tweet_id is valid
		try:
			tweet = Tweet.objects.get(id=data.get('tweet_id'))
		except:
			return JsonResponse({"error": "tweet not present."})

		#Attempt to save delete request
		try:
			DeleteTweet.objects.create(
					admin=u,
					tweet=tweet,
				)

			#log
			logger.info('Admin:{} requested deletion of tweet with id:{}'.format(u.username, tweet.id), extra={'source': u.username, 'log_type': 'action', 'object': 'tweet:{}'.format(tweet.id)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)

	else:
		return JsonResponse({
				"method": "POST",
				"body": {
					"tweet_id": "<int: tweet_id>",
				},
			})


#Admin makes a request to create a tweet
@csrf_exempt
@login_required(login_url='/login')
def create_tweet_request(request):
	u = request.user

	#Only admin allowed to make a request
	if (not u.is_staff) or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		#Check if user_id is valid
		try:
			user = User.objects.get(id=data.get('user_id'))
		except:
			return JsonResponse({"error": "user not present."})
		if user.is_staff or user.is_superuser:
			return JsonResponse({"error": "not have access to tweet from this user."})

		#Check if tweet is valid
		tweet = data.get('tweet')
		if not tweet:
			return JsonResponse({"error": "tweet not present."})

		tweet = tweet.strip()
		if len(tweet)==0 or len(tweet)>280:
			return JsonResponse({"error": "tweet must be less than or equal to 280 characters and must not be empty."})

		#Attempt to save create tweet request
		try:
			CreateTweet.objects.create(
					admin=u,
					userid=user.id,
					tweet=tweet
				)

			#log
			logger.info('Admin:{} requested posting of tweet from User:{}'.format(u.username, user.username), extra={'source': u.username, 'log_type': 'action', 'object': 'user:{}'.format(user.username)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)

	else:
		return JsonResponse({
				"method": "POST",
				"body": {
					"user_id": "<int: user_id>",
					"tweet": "tweet content",
				},
			})


#Admin makes a request to update user details
@csrf_exempt
@login_required(login_url='/login')
def update_user_request(request):
	u = request.user

	#Only admin allowed to make a request
	if (not u.is_staff) or u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method=="POST":
		data = json.loads(request.body.decode('utf-8'))

		#Check if user_id is valid
		try:
			user = User.objects.get(id=data.get('user_id'))
		except:
			return JsonResponse({"error": "user not present."})
		if user.is_staff or user.is_superuser:
			return JsonResponse({"error": "not have access to update this user."})

		#Get updated details
		new_first_name = data.get('new_first_name', '')
		new_last_name = data.get('new_last_name', '')
		new_bio = data.get('new_bio', '')

		#Check if atleast one field is present
		if not (len(new_bio) or len(new_first_name) or len(new_last_name)):
			return JsonResponse({"error": "Provide atleast one updated field."})

		#Attempt to save user details update request
		try:
			upuser = UpdateUser.objects.create(
					admin=u,
					user=user
				)
			if new_first_name:
				upuser.new_first_name = new_first_name
			if new_last_name:
				upuser.new_last_name = new_last_name
			if new_bio:
				upuser.new_bio = new_bio
			upuser.save()
			#log
			logger.info("Admin:{} requested an update of User:{}'s profile".format(u.username, user.username), extra={'source': u.username, 'log_type': 'action', 'object': 'user:{}'.format(user.username)})
			return JsonResponse(REQUEST_SUCCESS, safe=False)
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)

	else:
		return JsonResponse({
				"method": "POST",
				"body": {
					"user_id": "<int: user_id>",
					"new_bio": "new_bio",
					"new_first_name": "new_first_name",
					"new_last_name": "new_last_name",
				},
			})


#Superadmin accessing requests related to user details
@login_required(login_url='/login')
def request_user(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	#Get requests which are not responded till now in sorted order
	ureqs = UpdateUser.objects.filter(responded=False).order_by("timestamp").all()

	#log
	logger.info('Superadmin:{} accesses requests related to user details'.format(u.username), extra={'source': u.username, 'log_type': 'access'})
	return JsonResponse([ureq.serialize() for ureq in ureqs], safe=False)


#Superadmin accessing requests related to tweet CUD
@login_required(login_url='/login')
def request_tweets(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	#Getting requests which are not responded till now in sorted order
	ureqs = UpdateTweet.objects.filter(responded=False).order_by("timestamp").all()
	dreqs = DeleteTweet.objects.filter(responded=False).order_by("timestamp").all()
	creqs = CreateTweet.objects.filter(responded=False).order_by("timestamp").all()

	#log
	logger.info('Superadmin:{} accesses requests related to CUD of tweets'.format(u.username), extra={'source': u.username, 'log_type': 'access'})
	return JsonResponse({
			"update_request": [ureq.serialize() for ureq in ureqs],
			"delete_request": [dreq.serialize() for dreq in dreqs],
			"create_request": [creq.serialize() for creq in creqs],
		}, safe=False)


#Superadmin responding to requests related to user details
@csrf_exempt
@login_required(login_url='/login')
def respond_users(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "PUT":
		responses = json.loads(request.body.decode('utf-8'))

		return_json = []
		for response in responses:
			try:
				upuser = UpdateUser.objects.get(id=response.get('request_id'))

			#Check if request_id is valid
			except:
				return_json.append({
						"request_id": response.get('request_id'),
						"error": "Id not present.",
					})
				continue

			#Attempt to update request_id if action is not granted
			upuser.responded = True
			user = upuser.user
			if not response.get('action_granted', False):
				try:
					upuser.save()
					return_json.append({
						"request_id": response.get('request_id'),
						"message": "Response saved.",
					})

					#log
					logger.info('Superadmin:{} rejected request to update User:{} details from Admin:{}'.format(u.username, user.username, upuser.admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(upuser.admin.username)})
					continue
				except:
					return_json.append({
						"request_id": response.get('request_id'),
						"error": "Response failed.",
					})
					continue

			#Assigning changes
			upuser.action_granted = True
			if len(upuser.new_first_name):
				user.first_name = upuser.new_first_name
			if len(upuser.new_last_name):
				user.last_name = upuser.new_last_name
			if len(upuser.new_bio):
				user.bio = upuser.new_bio

			#Attempt to update request_id and user details
			try:
				user.save()
				upuser.save()
				return_json.append({
						"request_id": response.get('request_id'),
						"message": "Response saved.",
					})

				#log
				logger.info('Superadmin:{} approved request to update User:{} details from Admin:{}'.format(u.username, user.username, upuser.admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(upuser.admin.username)})
			except:
				return_json.append({
						"request_id": response.get('request_id'),
						"error": "Response failed.",
					})

		return JsonResponse(return_json, safe=False)

	else:
		return JsonResponse({
				"method": "PUT",
				"body": [
					{
						"request_id": "<int: request_id>",
						"action_granted": "true or false without quotes",
					},
				],				
			})


#Superadmin responding to requests related to tweets update
@csrf_exempt
@login_required(login_url='/login')
def respond_tweets_update(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method=="PUT":
		return_json = []
		responses = json.loads(request.body.decode('utf-8'))

		for response in responses:

			#Check if request_id is valid or not
			try:
				update_tweet = UpdateTweet.objects.get(id=response.get('request_id'))
			except:
				return_json.append({"request_id": response.get('request_id'), "error": "Id not present."})

			update_tweet.responded = True
			tweet = update_tweet.tweet

			#if action granted then update tweet
			if response.get('action_granted', False):
				tweet.tweet = update_tweet.new_tweet
				update_tweet.action_granted = True
			else:
				#log
				logger.info('Superadmin:{} rejected request to update Tweet:{} from Admin:{}'.format(u.username, tweet.id, update_tweet.admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(update_tweet.admin.username)})

			#Attempt to save the updated tweet and request_id
			try:
				update_tweet.save()
				tweet.save()
				return_json.append({"request_id": response.get('request_id'), "message": "Response saved."})
				if update_tweet.action_granted:
					#log
					logger.info('Superadmin:{} approved request to update Tweet:{} from Admin:{}'.format(u.username, tweet.id, update_tweet.admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(update_tweet.admin.username)})
			except:
				return_json.append({"request_id": response.get('request_id'), "error": "Response failed."})

		return JsonResponse(return_json, safe=False)

	else:
		return JsonResponse({
				"method": "PUT",
				"body": [
					{
						"request_id": "<int: request_id>",
						"action_granted": "true or false without quotes",
					},
				],
			})


#Superadmin is responding to requests related to tweets delete
@csrf_exempt
@login_required(login_url='/login')
def respond_tweets_delete(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "PUT":
		return_json = []
		responses = json.loads(request.body.decode('utf-8'))

		for response in responses:

			#Check if request_id is valid
			try:
				delete_tweet = DeleteTweet.objects.get(id=response.get('request_id'))
			except:
				return_json.append({"request_id": response.get('request_id'), "error": "Id not present"})

			delete_tweet.responded = True
			tweet = delete_tweet.tweet
			tweet_id = tweet.id
			admin = delete_tweet.admin
			if response.get('action_granted', False):
				delete_tweet.action_granted = True
			else:
				#log
				logger.info('Superadmin:{} rejected request to delete Tweet:{} from Admin:{}'.format(u.username, tweet_id, admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(admin.username)})

			#Attempt to save request_id and delete tweet if granted
			try:
				delete_tweet.save()
				if response.get('action_granted', False):
					tweet.delete()
					#log
					logger.info('Superadmin:{} approved request to delete Tweet:{} from Admin:{}'.format(u.username, tweet_id, admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(admin.username)})
				return_json.append({"request_id": response.get('request_id'), "message": "Response saved."})
			except:
				return_json.append({"request_id": response.get('request_id'), "error":
					"Response failed."})

		return JsonResponse(return_json, safe=False)

	else:
		return JsonResponse({
				"method": "PUT",
				"body": [
					{
						"request_id": "<int: request_id>",
						"action_granted": "true or false without quotes",
					},
				],
			})


#Superadmin is responding to requests related to tweets create
@csrf_exempt
@login_required(login_url='/login')
def respond_tweets_create(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "PUT":
		return_json = []
		responses = json.loads(request.body.decode('utf-8'))

		for response in responses:

			#Check if request_id is valid
			try:
				create_tweet = CreateTweet.objects.get(id=response.get('request_id'))
			except:
				return_json.append({"request_id": response.get('request_id'), "error": "Id not present."})

			create_tweet.responded = True
			admin = create_tweet.admin
			create_tweet.action_granted = response.get('action_granted', False)

			#Attempt to save updated request_id and create tweet if granted
			try:
				#Posting new tweet if granted
				if response.get('action_granted', False):
					user = User.objects.get(id=create_tweet.userid)
					t = Tweet.objects.create(user=user, tweet=create_tweet)

					#log
					logger.info('Superadmin:{} approved request to create new Tweet:{} from Admin:{}'.format(u.username, t.id, admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(admin.username)})
				else:
					#log
					logger.info('Superadmin:{} rejected request to create new Tweet from Admin:{}'.format(u.username, admin.username), extra={'source': u.username, 'log_type': 'audit', 'object': 'user:{}'.format(admin.username)})
				create_tweet.save()
				return_json.append({"request_id": response.get('request_id'), "message": "Response saved."})
			except:
				return_json.append({"request_id": response.get('request_id'), "error": "Response failed."})

		return JsonResponse(return_json, safe=False)

	else:
		return JsonResponse({
				"method": "PUT",
				"body": [
					{
						"request_id": "<int: request_id>",
						"action_granted": "true or false without quotes",
					},
				],
			})


#Superadmin accessing logs
@login_required(login_url='/login')
def logs(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	#Trying to get the logs from file
	try:
		with open(os.path.join(APP_DIR, 'twitter_logs.log'), 'r') as f:
			j_dict = []
			lines = f.readlines()
			for line in lines:
				j_dict.append(json.loads(line.strip()))

			#log
			logger.info('Superadmin:{} accessing logs'.format(u.username), extra={'source': u.username, 'log_type': 'access'})
			return JsonResponse(j_dict, safe=False)
	except:
		return JsonResponse(REQUEST_FAILED, safe=False)


#Superadmin generating insights from logs
@csrf_exempt
@login_required(login_url='/login')
def logs_query(request):
	u = request.user

	#Check if superadmin or not
	if not u.is_superuser:
		return JsonResponse(BAD_REQUEST, safe=False)

	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		#Attempt to read logs from file
		try:
			with open(os.path.join(APP_DIR, 'twitter_logs.log'), 'r') as f:
				lines = f.readlines()
		except:
			return JsonResponse(REQUEST_FAILED, safe=False)

		#function to see if log satisfies query condition
		def check_cond(log, query):
			for key in query.keys():
				if key == "message":
					if query[key].lower() not in log[key].lower():
						return False
				elif key == "from":
					if query[key]>log['asctime']:
						return False
				elif key == "to":
					if query[key]<log['asctime']:
						return False
				elif query[key] != log.get(key, ''):
					return False
			return True

		#Check if query present or not
		if data.get('query') is None:
			return JsonResponse({"error": "No query present in request."}) 

		#Getting all log that satisfies query condition
		j_dict = []
		cnt = 0
		for line in lines:
			log = json.loads(line)
			if check_cond(log, data['query']):
				cnt += 1
				if data.get('show_logs', False):
					j_dict.append(log)

		#log
		logger.info('Superadmin:{} quering from logs'.format(u.username), extra={'source': u.username, 'log_type': 'access'})
		return JsonResponse({
				"count": cnt,
				"logs": j_dict,
			}, safe=False)

	else:
		return JsonResponse({
				"method": "POST",
				"body": {
					"show_logs": "true or false without quotes",
					"query": {
						"from": "oldest entry in query to be considered. Time must be in asctime format",
						"to": "latest entry in query to be considered. Time must be in asctime format",
						"log_type": "action or audit or access (any one)",
						"source": "username of the user performing access/action/audit.",
						"object": "user:username or tweet:tweet_id",
						"message": "words that must be present in message of log",
					},
				},
			})







