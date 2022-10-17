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
        'required': True,
        'unique': False,
    },
    'follow_ratio': {
        'type': 'float',
        'required': True,
        'unique': False,
    },
    'follows': {
        'type': 'integer',
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
    'created_time': {
        'type': 'string',
        'required': True,
        'unique': False,
    },
    'tags': {
        'type': 'list',
        'required': True,
        'unique': False,
    }
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
DOMAIN = {
    'PreviousPost': PreviousPost,
    #'NewPost': NewPost,
    #'User': User
}
