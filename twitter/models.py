from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
#Model to save user details
class User(AbstractUser):
	bio = models.TextField(blank=True)

	def serialize(self):
		return {
		"id": self.id,
		"username": self.username,
		"email": self.email,
		"first_name": self.first_name,
		"last_name": self.last_name,
		"bio": self.bio,
		}

#Model to save tweet
class Tweet(models.Model):
	user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='tweets')
	timestamp = models.DateTimeField(auto_now_add=True)
	tweet = models.CharField(blank=False, null=False, max_length=280)

	def serialize(self):
		return {
			"id": self.id,
			"user": self.user.id,
			"timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
			"tweet": self.tweet,
		}

#Model to save admin requests to update tweet
class UpdateTweet(models.Model):
	tweet = models.ForeignKey("Tweet", on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	admin = models.ForeignKey("User", on_delete=models.CASCADE, related_name='update_tweets_requests')
	new_tweet = models.CharField(blank=False, null=False, max_length=280)
	responded = models.BooleanField(default=False)
	action_granted = models.BooleanField(default=False)

	def serialize(self):
		return {
			"id": self.id,
			"user": self.tweet.user.username,
			"admin": self.admin.username,
			"old_tweet": self.tweet.tweet,
			"new_tweet": self.new_tweet,
			"timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
			"action": "update",
		}

#Model to save admin requests to delete tweet
class DeleteTweet(models.Model):
	tweet = models.ForeignKey("Tweet", on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	admin = models.ForeignKey("User", on_delete=models.CASCADE, related_name='delete_tweets_requests')
	responded = models.BooleanField(default=False)
	action_granted = models.BooleanField(default=False)

	def serialize(self):
		return {
			"id": self.id,
			"user": self.tweet.user.username,
			"admin": self.admin.username,
			"tweet": self.tweet.tweet,
			"timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
			"action": "delete",
		}

#Model to save admin requests to create tweet
class CreateTweet(models.Model):
	admin = models.ForeignKey("User", on_delete=models.CASCADE, related_name='create_tweets_requests')
	userid = models.IntegerField(blank=False, null=False)
	tweet = models.CharField(blank=False, null=False, max_length=280)
	timestamp = models.DateTimeField(auto_now_add=True)
	responded = models.BooleanField(default=False)
	action_granted = models.BooleanField(default=False)

	def serialize(self):
		return {
			"id": self.id,
			"admin": self.admin.username,
			"user_id": self.userid,
			"tweet": self.tweet,
			"timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
			"action": "create",
		}

#Model to save admin requests to update user details
class UpdateUser(models.Model):
	admin = models.ForeignKey("User", on_delete=models.CASCADE, related_name="update_user_requests")
	user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='update_requests_made_for_me')
	new_first_name = models.CharField(blank=True, null=False, max_length=255)
	new_last_name = models.CharField(blank=True, null=False, max_length=255)	
	new_bio = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	responded = models.BooleanField(default=False)
	action_granted = models.BooleanField(default=False)

	def serialize(self):
		return {
			"id": self.id,
			"admin": self.admin.username,
			"username": self.user.username,
			"old_first_name": self.user.first_name,
			"old_last_name": self.user.last_name,
			"old_bio": self.user.bio,
			"new_first_name": self.new_first_name,
			"new_last_name": self.new_last_name,
			"new_bio": self.new_bio,
			"timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
			"action": "update",
		}


