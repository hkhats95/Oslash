domain = "www.oslash-backend-project.herokuapp.com"

BAD_REQUEST = {"error": "Bad Request."}

REQUEST_FAILED = {"error": "Request failed."}

REQUEST_SUCCESS = {"message": "Request successful."}

ANONYMOUS_USER = {
	"register": {
		"url": "{}/register".format(domain),
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
		"url": "{}/login".format(domain),
		"method": "POST",
		"body": {
			"username": "user_name",
			"password": "password",
		}
	},
	"logout": {
		"url": "{}/logout".format(domain),
		"method": "GET",
	}
}

NORMAL_USER = {
	"profile": {
		"url": "{}/user/profile".format(domain),
		"method": "GET",
	},
	"tweets": {
		"url": "{}/user/tweets".format(domain),
		"method": "GET",
	},
	"new_tweet": {
		"url": "{}/newtweet".format(domain),
		"method": "POST",
		"body": {
			"tweet": "tweet",
		},
	},
	"edit_tweet": {
		"url": "{}/edittweet".format(domain),
		"method": "PUT",
		"body": {
			"tweet_id": "<int: tweet_id>",
			"new_tweet": "tweet",
		},
	},
	"delete_tweet": {
		"url": "{}/deletetweet".format(domain),
		"method": "PUT",
		"body": {
			"tweet_id": "<int: tweet_id>",
		},
	},
	"logout": {
		"url": "{}/logout".format(domain),
		"method": "GET",
	}
}

ADMIN_USER = {
	"profile": {
		"url": "{}/user/profile".format(domain),
		"method": "GET",
	},
	"some_user_profile": {
		"url": "{}/user/<int: user_id>/profile".format(domain),
		"method": "GET",
	},
	"all_user_profiles": {
		"url": "{}/all/user/profile".format(domain),
		"method": "GET",
	},
	"some_user_tweets": {
		"url": "{}/user/<int: user_id>/tweets".format(domain),
		"method": "GET",
	},
	"update_user_profile": {
		"url": "{}/user/update/request".format(domain),
		"method": "POST",
		"body": {
			"user_id": "<int: user_id>",
			"new_bio": "new_bio",
			"new_first_name": "new_first_name",
			"new_last_name": "new_last_name",
		},
	},
	"update_tweet": {
		"url": "{}/tweet/update/request".format(domain),
		"method": "POST",
		"body": {
			"tweet_id": "<int: tweet_id>",
			"new_tweet": "new_tweet",
		},
	},
	"delete_tweet": {
		"url": "{}/tweet/delete/request".format(domain),
		"method": "POST",
		"body": {
			"tweet_id": "<int: tweet_id>",
		},
	},
	"create_tweet": {
		"url": "{}/tweet/create/request".format(domain),
		"method": "POST",
		"body": {
			"user_id": "<int: user_id>",
			"tweet": "tweet",
		},
	},
	"logout": {
		"url": "{}/logout".format(domain),
		"method": "GET",
	}
}

SUPER_ADMIN_USER = {
	"profile": {
		"url": "{}/user/profile".format(domain),
		"method": "GET",
	},
	"register_admin": {
		"url": "{}/register/admin".format(domain),
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
		"url": "{}/request/users".format(domain),
		"method": "GET",
	},
	"CUD_tweet_requests": {
		"url": "{}/request/tweets".format(domain),
		"method": "GET",
	},
	"response_to_update_user_requests": {
		"url": "{}/respond/users".format(domain),
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"response_to_update_tweet_requests": {
		"url": "{}/respond/tweets/update".format(domain),
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"response_to_delete_tweet_requests": {
		"url": "{}/respond/tweets/delete".format(domain),
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"response_to_create_tweet_requests": {
		"url": "{}/respond/tweets/create".format(domain),
		"method": "PUT",
		"body": [
			{
				"request_id": "<int: request_id>",
				"action_granted": "true or false without quotes",
			},
		],
	},
	"view_logs": {
		"url": "{}/logs".format(domain),
		"method": "GET",
	},
	"query_logs": {
		"url": "{}/logs/query".format(domain),
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
		"url": "{}/logout".format(domain),
		"method": "GET",
	},
}


