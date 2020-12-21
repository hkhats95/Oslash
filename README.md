# Oslash

This backend project provides you with the following API's to work with the database:

```python
ANONYMOUS_USER = {
	"register": {
		"url": "www.oslash-backend-project.herokuapp.com/register",
		"method": "POST",
		"body": {
			"username": "user_name",
			"email": "email",
			"password": "password",
			"confirmation": "repeat password",
			"first_name": "first_name",
			"last_name": "last_name",
			"bio": "bio",
		},
	},
	"login": {
		"url": "www.oslash-backend-project.herokuapp.com/login",
		"method": "POST",
		"body": {
			"username": "user_name",
			"password": "password",
		}
	},
	"logout": {
		"url": "www.oslash-backend-project.herokuapp.com/logout",
		"method": "GET",
	}
}

NORMAL_USER = {
	"profile": {
		"url": "www.oslash-backend-project.herokuapp.com/user/profile",
		"method": "GET",
	},
	"tweets": {
		"url": "www.oslash-backend-project.herokuapp.com/user/tweets",
		"method": "GET",
	},
	"new_tweet": {
		"url": "www.oslash-backend-project.herokuapp.com/newtweet",
		"method": "POST",
		"body": {
			"tweet": "tweet",
		},
	},
	"edit_tweet": {
		"url": "www.oslash-backend-project.herokuapp.com/edittweet",
		"method": "PUT",
		"body": {
			"tweet_id": "<int: tweet_id>",
			"new_tweet": "tweet",
		},
	},
	"delete_tweet": {
		"url": "www.oslash-backend-project.herokuapp.com/deletetweet",
		"method": "PUT",
		"body": {
			"tweet_id": "<int: tweet_id>",
		},
	},
	"logout": {
		"url": "www.oslash-backend-project.herokuapp.com/logout",
		"method": "GET",
	}
}

ADMIN_USER = {
	"profile": {
		"url": "www.oslash-backend-project.herokuapp.com/user/profile",
		"method": "GET",
	},
	"some_user_profile": {
		"url": "www.oslash-backend-project.herokuapp.com/user/<int: user_id>/profile",
		"method": "GET",
	},
	"all_user_profiles": {
		"url": "www.oslash-backend-project.herokuapp.com/all/user/profile",
		"method": "GET",
	},
	"some_user_tweets": {
		"url": "www.oslash-backend-project.herokuapp.com/user/<int: user_id>/tweets",
		"method": "GET",
	},
	"update_user_profile": {
		"url": "www.oslash-backend-project.herokuapp.com/user/update/request",
		"method": "POST",
		"body": {
			"user_id": "<int: user_id>",
			"new_bio": "new_bio",
			"new_first_name": "new_first_name",
			"new_last_name": "new_last_name",
		},
	},
	"update_tweet": {
		"url": "www.oslash-backend-project.herokuapp.com/tweet/update/request",
		"method": "POST",
		"body": {
			"tweet_id": "<int: tweet_id>",
			"new_tweet": "new_tweet",
		},
	},
	"delete_tweet": {
		"url": "www.oslash-backend-project.herokuapp.com/tweet/delete/request",
		"method": "POST",
		"body": {
			"tweet_id": "<int: tweet_id>",
		},
	},
	"create_tweet": {
		"url": "www.oslash-backend-project.herokuapp.com/tweet/create/request",
		"method": "POST",
		"body": {
			"user_id": "<int: user_id>",
			"tweet": "tweet",
		},
	},
	"logout": {
		"url": "www.oslash-backend-project.herokuapp.com/logout",
		"method": "GET",
	}
}

SUPER_ADMIN_USER = {
	"profile": {
		"url": "www.oslash-backend-project.herokuapp.com/user/profile",
		"method": "GET",
	},
	"register_admin": {
		"url": "www.oslash-backend-project.herokuapp.com/register/admin",
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
	},
	"update_user_request": {
		"url": "www.oslash-backend-project.herokuapp.com/request/user",
		"method": "GET",
	},
	"CUD_tweet_requests": {
		"url": "www.oslash-backend-project.herokuapp.com/request/tweets",
		"method": "GET",
	},
	"response_to_update_user_requests": {
		"url": "www.oslash-backend-project.herokuapp.com/respond/user",
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"response_to_update_tweet_requests": {
		"url": "www.oslash-backend-project.herokuapp.com/respond/tweets/update",
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"response_to_delete_tweet_requests": {
		"url": "www.oslash-backend-project.herokuapp.com/respond/tweets/delete",
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"response_to_create_tweet_requests": {
		"url": "www.oslash-backend-project.herokuapp.com/respond/tweets/create",
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"view_logs": {
		"url": "www.oslash-backend-project.herokuapp.com/logs",
		"method": "GET",
	},
	"query_logs": {
		"url": "www.oslash-backend-project.herokuapp.com/logs/query",
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
	},
	"logout": {
		"url": "www.oslash-backend-project.herokuapp.com/logout",
		"method": "GET",
	},
}
```
