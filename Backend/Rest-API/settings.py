"""
Settings.py
Pradyumn Nukala
June 23, 2017
Description: Settings class for all json schema and input output.This is
             where HTTP requests get handled.
"""
from cerberus import Validator

MONGO_HOST = '35.185.100.103'
MONGO_PORT = 27017
PAGINATION_DEFAULT = 1000
MONGO_USERNAME = 'admin'
MONGO_PASSWORD = 'braxday123'
MONGO_DBNAME = 'admin'
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

previousPostSchema = {
    'PostID': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 40,
        'required': True,
        'unique': False,
    },
    'Links': {
        'type': 'list',
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
    'Location': {
        'type': 'point',
        'maxlength': 45,
        'required': True,
        'unique': False,
    },
    'PostTime': {
        'type': 'datetime',
        'maxlength': 45,
        'required': True,
        'unique': False,
    },
}

newPostSchema = {
    'PostID': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 40,
        'required': True,
        'unique': False,
    },
    'Image': {
        'type': '',
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
    'BestPicture': {
        'type': 'string',
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
        'type': 'datetime',
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
        'type': 'datetime',
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
        'field': 'PostID'
    },

    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET','PATCH', 'PUT'],
    'schema': previousPostSchema
}

NewPost = {
    'item_title': 'NewPost',
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'PostID'
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
    'NewPost': NewPost,
    'User': User
}
