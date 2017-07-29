"""
Settings.py
Pradyumn Nukala
June 23, 2017
Description: Settings class for all json schema and input output.This is
             where HTTP requests get handled.
"""

from cerberus import Validator

MONGO_HOST = '104.199.211.96'
MONGO_PORT = 27017
MONGO_USERNAME = 'root'
MONGO_PASSWORD = 'hjPy796z'
PAGINATION_DEFAULT = 1000
MONGO_DBNAME = 'admin'
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

previousPostSchema = {
    'postid': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 40,
        'required': True,
        'unique': False,
    },
    'image_link': {
        'type': 'string',
        'required': True,
        'unique': False,
    },
    'likes': {
        'type': 'integer',
        'maxlength': 45,
        'required': True,
        'unique': False,
    },
    'followed_by': {
        'type': 'integer',
        'maxlength': 45,
        'required': True,
        'unique': False,
    },
    'follows': {
        'type': 'integer',
        'maxlength': 45,
        'required': True,
        'unique': False,
    },
    'meanLikes': {
        'type': 'float',
        'required': True,
        'unique': False,
    },
    'days_since_posting': {
        'type': 'float',
        'required': True,
        'unique': False,
    },
    'location': {
        'type': 'string',
        'maxlength': 45,
        'required': True,
        'unique': False,
    },
    'created_time': {
        'type': 'string',
        'maxlength': 45,
        'required': True,
        'unique': False,
    },
    'tags': {
        'type': 'list',
        'required': True,
        'unique': False,
    }
}

if False:
    newPostSchema = {
        'PostID': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 40,
            'required': True,
            'unique': False,
        },
        'Image': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 40,
            'required': True,
            'unique': True,
        },
        'UserID': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 40,
            'required': True,
            'unique': True,
        },
        'RealLikes': {
            'type': 'integer',
            'maxlength': 45,
            'required': True,
            'unique': False,
        },
        'EstimatedLikes': {
            'type': 'integer',
            'maxlength': 45,
            'required': True,
            'unique': False,
        },
        'EstimatedTime': {
            'type': 'integer',
            'maxlength': 45,
            'required': True,
            'unique': False,
        },
        'Location': {
            'type': 'point',
            'maxlength': 45,
            'required': True,
            'unique': False,
        },
        'PostTime': {
            'type': 'string',
            'maxlength': 45,
            'required': True,
            'unique': False,
        },
    }

    userSchema = {
        'UserID': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 40,
            'required': True,
            'unique': False,
        },
        'Name': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 60,
            'required': True,
            'unique': False,
        },
        'AverageLocation': {
            'type': 'point',
            'minlength': 1,
            'maxlength': 40,
            'required': True,
            'unique': False,
        },
        'Followers': {
            'type': 'integer',
            'minlength': 1,
            'maxlength': 60,
            'required': True,
            'unique': False,
        },
        'LastPictureTime': {
            'type': 'datetime',
            'minlength': 1,
            'maxlength': 40,
            'required': True,
            'unique': False,
        },
        'TimeBetweenEachPicture': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 60,
            'required': True,
            'unique': False,
        },
    }

PreviousPost = {
    'item_title': 'PreviousPost',
    'allow_unknown': True,
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'postid'
    },

    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET','PATCH', 'PUT'],
    'schema': previousPostSchema
}
if False:
    NewPost = {
        'item_title': 'NewPost',
        'additional_lookup': {
            'url': 'regex("[\w]+")',
            'field': 'postid'
        },

        'cache_control': 'max-age=10,must-revalidate',
        'cache_expires': 10,
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET','PATCH', 'PUT'],
        'schema': newPostSchema
    }

    User = {
        'item_title': 'User',
        'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'UserID'
        },

        'cache_control': 'max-age=10,must-revalidate',
        'cache_expires': 10,
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        'schema': userSchema
        }

DOMAIN = {
    'PreviousPost': PreviousPost,
    #'NewPost': NewPost,
    #'User': User
}
