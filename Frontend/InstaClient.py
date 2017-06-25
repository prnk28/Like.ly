"""
Insta Client Temp Class for authentication
Pradyumn Nukala
6/25/17
"""

import requests
from instagram.client import InstagramAPI
# Once we opensource repo we will remove both of these with dummy details
INSTAGRAM_CLIENT_ID = "31ea4441212c40278342c17738448aa8"
INSTAGRAM_CLIENT_SECRET = "ace0ae44071f41ac854e8423e63ea95c"

def ReturnPopularMedia():
    api = InstagramAPI(access_token=INSTAGRAM_CLIENT_ID, client_secret=INSTAGRAM_CLIENT_SECRET)
    recent_media, next_ = api.user_recent_media(user_id="userid", count=10)
    for media in recent_media:
        print (media.caption.text)

ReturnPopularMedia()
