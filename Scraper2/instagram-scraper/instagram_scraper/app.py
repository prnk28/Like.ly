#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division

import argparse
import codecs
import errno
import glob
from operator import itemgetter
import json
import logging.config
import os
import re
import sys
import textwrap
import time
import warnings
import datetime
import json
import httplib, urllib, base64, json
import concurrent.futures
import requests
import tqdm

from instagram_scraper.constants import *

try:
    reload(sys)  # Python 2.7
    sys.setdefaultencoding("UTF8")
except NameError:
    pass

warnings.filterwarnings('ignore')

class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


class PreviousPost:
    #A class that will be used to create previous post JSON objects to put in the database
    def __init__(self, postid, likes, follow_ratio, follows, meanLikes, days_since_posting, created_time, tags):
        self.postid = postid

        self.likes = likes
        self.follow_ratio = follow_ratio
        self.follows = follows
        self.meanLikes = meanLikes
        self.days_since_posting = days_since_posting

        self.created_time = created_time
        self.tags = tags

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                sort_keys=True, indent=4)


class InstagramScraper(object):
    """InstagramScraper scrapes and downloads an instagram user's photos and videos"""
    def __init__(self, **kwargs):
        default_attr = dict(username='', usernames=[], filename=None,
                            login_user=None, login_pass=None, login_only=False,
                            destination='./', retain_username=False,
                            quiet=False, maximum=0, media_metadata=False, latest=False,
                            media_types=['image', 'video', 'story'], tag=False, location=False,
                            search_location=False, comments=False, verbose=0, include_location=False, filter=None)

        allowed_attr = list(default_attr.keys())
        default_attr.update(kwargs)

        for key in default_attr:
            if key in allowed_attr:
                self.__dict__[key] = kwargs.get(key)

        # Set up a logger
        self.logger = InstagramScraper.get_logger(level=logging.DEBUG, verbose=default_attr.get('verbose'))

        self.posts = []
        self.session = requests.Session()
        self.session.headers = {'user-agent': CHROME_WIN_UA}

        self.cookies = None
        self.logged_in = False
        self.last_scraped_filemtime = 0
        if default_attr['filter']:
            self.filter = set(self.filter)

    def login(self):
        """Logs in to instagram."""
        self.session.headers.update({'Referer': BASE_URL})
        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        login_data = {'username': self.login_user, 'password': self.login_pass}
        login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies
        login_text = json.loads(login.text)

        if login_text.get('authenticated') and login.status_code == 200:
            self.logged_in = True
        else:
            self.logger.error('Login failed for ' + self.login_user)

            if 'checkpoint_url' in login_text:
                self.logger.error('Please verify your account at ' + login_text.get('checkpoint_url'))
            elif 'errors' in login_text:
                for count, error in enumerate(login_text['errors'].get('error')):
                    count += 1
                    self.logger.debug('Session error %(count)s: "%(error)s"' % locals())
            else:
                self.logger.error(json.dumps(login_text))

    def logout(self):
        """Logs out of instagram."""
        if self.logged_in:
            try:
                logout_data = {'csrfmiddlewaretoken': self.cookies['csrftoken']}
                self.session.post(LOGOUT_URL, data=logout_data)
                self.logged_in = False
            except requests.exceptions.RequestException:
                self.logger.warning('Failed to log out ' + self.login_user)

    def make_dst_dir(self, username):
        """Creates the destination directory."""
        if self.destination == './':
            dst = './'
        else:
            if self.retain_username:
                dst = self.destination + '/'
            else:
                dst = self.destination

        try:
            os.makedirs(dst)
        except OSError as err:
            if err.errno == errno.EEXIST and os.path.isdir(dst):
                # Directory already exists
                self.get_last_scraped_filemtime(dst)
                pass
            else:
                # Target dir exists as a file, or a different error
                raise

        return dst

    def get_last_scraped_filemtime(self, dst):
        """Stores the last modified time of newest file in a directory."""
        list_of_files = []
        file_types = ('*.jpg', '*.mp4')

        for type in file_types:
            list_of_files.extend(glob.glob(dst + '/' + type))

        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getmtime)
            self.last_scraped_filemtime = int(os.path.getmtime(latest_file))



    def scrape_hashtag(self):
        self.__scrape_query(self.query_hashtag_gen)

    def scrape_location(self):
        self.__scrape_query(self.query_location_gen)

    def __scrape_query(self, media_generator, executor=concurrent.futures.ThreadPoolExecutor(max_workers=10)):
        """Scrapes the specified value for posted media."""
        for value in self.usernames:
            self.posts = []
            self.last_scraped_filemtime = 0
            future_to_item = {}

            dst = self.make_dst_dir(value)

            if self.include_location:
                media_exec = concurrent.futures.ThreadPoolExecutor(max_workers=5)

            iter = 0
            for item in tqdm.tqdm(media_generator(value), desc='Searching {0} for posts'.format(value), unit=" media",
                                  disable=self.quiet):
                if ((item['is_video'] is False and 'image' in self.media_types) or \
                    (item['is_video'] is True and 'video' in self.media_types)
                ) and self.is_new_media(item):
                    future = executor.submit(self.download, item, dst)
                    future_to_item[future] = item

                if self.include_location and 'location' not in item:
                    media_exec.submit(self.__get_location, item)

                if self.comments:
                    item['edge_media_to_comment']['data'] = list(self.query_comments_gen(item['shortcode']))

                if self.media_metadata or self.comments or self.include_location:
                    self.posts.append(item)

                iter = iter + 1
                if self.maximum != 0 and iter >= self.maximum:
                    break

            if future_to_item:
                for future in tqdm.tqdm(concurrent.futures.as_completed(future_to_item), total=len(future_to_item),
                                        desc='Downloading', disable=self.quiet):
                    item = future_to_item[future]

                    if future.exception() is not None:
                        self.logger.warning(
                            'Media for {0} at {1} generated an exception: {2}'.format(value, item['urls'], future.exception()))

            if (self.media_metadata or self.comments or self.include_location) and self.posts:
                self.save_json(self.posts, '{0}/{1}.json'.format(dst, value))

    def query_hashtag_gen(self, hashtag):
        return self.__query_gen(QUERY_HASHTAG, 'hashtag', hashtag)

    def query_location_gen(self, location):
        return self.__query_gen(QUERY_LOCATION, 'location', location)


    def __query_gen(self, url, entity_name, query, end_cursor=''):
        """Generator for hashtag and location."""
        nodes, end_cursor = self.__query(url, entity_name, query, end_cursor)

        if nodes:
            try:
                while True:
                    for node in nodes:
                        yield node

                    if end_cursor:
                        nodes, end_cursor = self.__query(url, entity_name, query, end_cursor)
                    else:
                        return
            except ValueError:
                self.logger.exception('Failed to query ' + query)

    def __query(self, url, entity_name, query, end_cursor):
        resp = self.session.get(url.format(query, end_cursor))

        if resp.status_code == 200:
            payload = json.loads(resp.text)['data'][entity_name]

            if payload:
                nodes = []

                if end_cursor == '':
                    top_posts = payload['edge_' + entity_name + '_to_top_posts']
                    nodes.extend(self._get_nodes(top_posts))

                posts = payload['edge_' + entity_name + '_to_media']

                nodes.extend(self._get_nodes(posts))
                end_cursor = posts['page_info']['end_cursor']
                return nodes, end_cursor
            else:
                return iter([])
        else:
            time.sleep(6)
            return self.__query(url, entity_name, query, end_cursor)

    def _get_nodes(self, container):
        nodes = []

        for node in container['edges']:
            node = node['node']

            if node['is_video']:
                details = self.__get_media_details(node['shortcode'])

                if details:
                    node['urls'] = [details['video_url']]

                if self.include_location:
                    node['location'] = details.get('location')

                self.extract_tags(node)
            else:
                node['urls'] = [self.get_original_image(node['display_url'])]
                self.extract_tags(node)

            nodes.append(node)

        return nodes

    def __get_media_details(self, shortcode):
        resp = self.session.get(VIEW_MEDIA_URL.format(shortcode))

        if resp.status_code == 200:
            return json.loads(resp.text)['graphql']['shortcode_media']
        else:
            self.logger.warning('Failed to get media details for ' + shortcode)

    def __get_location(self, item):
        code = item.get('shortcode', item.get('code'))

        if code:
            details = self.__get_media_details(code)
            item['location'] = details.get('location')

    def scrape(self, executor=concurrent.futures.ThreadPoolExecutor(max_workers=10)):
        """Crawls through and downloads user's media"""
        if self.login_user and self.login_pass:
            self.login()
            if not self.logged_in and self.login_only:
                self.logger.warning('Fallback anonymous scraping disabled')
                return

        for username in self.usernames:
            self.posts = []
            self.last_scraped_filemtime = 0
            future_to_item = {}

            dst = self.make_dst_dir(username)

            # Get the user metadata.
            user = self.fetch_user(username)

            #if user:
                #self.get_profile_pic(dst, executor, future_to_item, user, username)
                #self.get_stories(dst, executor, future_to_item, user, username)

            # Crawls the media and sends it to the executor.
            self.get_media(dst, executor, future_to_item, username, user)

            # Displays the progress bar of completed downloads. Might not even pop up if all media is downloaded while
            # the above loop finishes.
            if future_to_item:
                for future in tqdm.tqdm(concurrent.futures.as_completed(future_to_item), total=len(future_to_item),
                                        desc='Downloading', disable=self.quiet):
                    item = future_to_item[future]

                    if future.exception() is not None:
                        self.logger.warning(
                            'Media at {0} generated an exception: {1}'.format(item['urls'], future.exception()))

            if (self.media_metadata or self.comments or self.include_location) and self.posts:
                self.save_json(self.posts, '{0}/{1}.json'.format(dst, username))

        self.logout()



    def get_media(self, dst, executor, future_to_item, username, user):
        """Scrapes the user's posts for media."""
        if self.media_types == ['story']:
            return

        if self.include_location:
            media_exec = concurrent.futures.ThreadPoolExecutor(max_workers=5)

        meanLikes = self.getMeanLikes(username)

        iter = 0
        for item in tqdm.tqdm(self.media_gen(username), desc='Searching {0} for posts'.format(username),
                              unit=' media', disable=self.quiet):
            #if self.in_media_types(item) and self.is_new_media(item):
            #    future = executor.submit(self.download, item, dst)
            #    future_to_item[future] = item

            if self.include_location:
                media_exec.submit(self.__get_location, item)

            #if self.comments:
            #    item['comments']['data'] = list(self.query_comments_gen(item['code']))
            if self.media_metadata or self.comments or self.include_location:
                image_link = item['images']['standard_resolution']['url']
                if(item['location'] != None):
                    location = item['location']['name']
                else:
                    location = ""


                likes = item['likes']['count']
                created_time = item['created_time']
                postid = item['id']

                # This posts to computer vision API
                headers = {
                    # Request headers
                    'Content-Type': 'application/json',
                    'Ocp-Apim-Subscription-Key': '7eb7e9da359d4d02b4ef770238913c0f',
                }

                params = urllib.urlencode({
                    # Request parameters
                    'visualFeatures': 'Categories, Tags, Description, Faces, ImageType, Color, Adult',
                    'language': 'en',
                })

                # Try connection for CVAPI
                try:
                    conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
                    conn.request("POST", "/vision/v1.0/analyze?%s" % params,
                                 '{"url":"%s"}' % image_link,
                                 headers)
                    response = conn.getresponse()
                    data = response.read()

                    # Utilizes JSON payload Class to Deserialize Json Object
                    p = Payload(data)

                    tags = []
                    for t in p.tags:
                        if t["confidence"] > 0.8:
                            tags.append(t["name"])
                    for t in p.categories:
                            tags.append(t["name"])

                    conn.close()
                except Exception as e:
                    print("[Errno {0}] {1}".format(e.errno, e.strerror))

                postTimeFinal=(datetime.datetime.fromtimestamp(int(created_time)))
                current = datetime.datetime.now()
                timeDiff = (current - postTimeFinal)
                timeDiff = (timeDiff.total_seconds())/(60*60*24)
                timeDiff = float('%.3f' % (timeDiff))

                # Implement creating JSON with tags and faces from CVAPI

                picture = PreviousPost(postid, likes, user['follows']['count']/user['followed_by']['count'], user['follows']['count'], meanLikes, timeDiff, created_time, tags)
                #payload = picture.toJSON()
                #print(payload)

                # This posts created JSON to our server
                """url = "http://104.199.211.96:65/PreviousPost"
                picture = PreviousPost(postid, image_link, likes, meanLikes, user['follows']['count'], user['followed_by']['count'],created_time,timeDiff,location,tags)
                payload = picture.toJSON()
                print(payload)
                headers = {
                    'content-type': "application/json",
                    'authorization': "Basic YWRtaW46YnJheGRheTEyMw==",
                    'cache-control': "no-cache",
                    }

                response = requests.request("POST", url, data=payload, headers=headers)
                """
                # This is what creates JSON
                self.posts.append({
                "follow_ratio" : user['follows']['count']/user['followed_by']['count'],
                "likes" : likes,
                "meanLikes" : meanLikes,
                "follows" : user['follows']['count'],
                "created_time" : created_time,
                "days_since_posting" : timeDiff,
                "tags" : tags})

            iter = iter + 1
            if self.maximum != 0 and iter >= self.maximum:
                break



    def getMeanLikes(self, username):
        count = 0
        average = 0
        for item in tqdm.tqdm(self.media_gen(username), desc='Searching {0} for posts'.format(username), unit=' media', disable=self.quiet):
            if self.media_metadata or self.comments or self.include_location:
                likes = item['likes']['count']
                count = count + 1
                average = likes + average
            if count == 0:
                return 0

        return (average/count)

    def fetch_user(self, username):
        """Fetches the user's metadata."""
        resp = self.session.get(BASE_URL + username)

        if resp.status_code == 200 and '_sharedData' in resp.text:
            try:
                shared_data = resp.text.split("window._sharedData = ")[1].split(";</script>")[0]
                return json.loads(shared_data)['entry_data']['ProfilePage'][0]['user']
            except (TypeError, KeyError, IndexError):
                pass

    def fetch_stories(self, user_id):
        """Fetches the user's stories."""
        resp = self.session.get(STORIES_URL.format(user_id), headers={
            'user-agent' : STORIES_UA,
            'cookie'     : STORIES_COOKIE.format(self.cookies['ds_user_id'], self.cookies['sessionid'])
        })

        retval = json.loads(resp.text)

        if resp.status_code == 200 and 'items' in retval and len(retval['items']) > 0:
            return [self.set_story_url(item) for item in retval['items']]
        return []

    def media_gen(self, username):
        """Generator of all user's media."""
        try:
            media = self.fetch_media_json(username, max_id=None)

            while True:
                for item in media['items']:
                    if not self.filter or self.filter&item['tags']:
                        yield item

                if media.get('more_available') and self.is_new_media(media['items'][-1]):
                    max_id = media['items'][-1]['id']
                    media = self.fetch_media_json(username, max_id)
                    # Post here?
                else:
                    return
        except ValueError:
            self.logger.exception('Failed to get media for ' + username)

    def fetch_media_json(self, username, max_id):
        """Fetches the user's media metadata."""
        url = MEDIA_URL.format(username)

        if max_id is not None:
            url += '?&max_id=' + max_id

        resp = self.session.get(url)

        if resp.status_code == 200:
            media = json.loads(resp.text)

            if not media['items']:
                raise ValueError('User {0} is private'.format(username))

            media['items'] = [self.augment_media_item(item) for item in media['items']]
            return media
        else:
            raise ValueError('User {0} does not exist'.format(username))

    def in_media_types(self, item):
        if item['type'] == 'carousel':
            for carousel_item in item['carousel_media']:
                if carousel_item['type'] in self.media_types:
                    return True
        else:
            return item['type'] in self.media_types

        return False

    def augment_media_item(self, item):
        """Augments media item object with new properties."""
        self.get_media_urls(item)
        self.extract_tags(item)
        return item

    def get_media_urls(self, item):
        """Sets the media url."""
        urls = []
        if item['type'] == 'carousel':
            for carousel_item in item['carousel_media']:
                url = carousel_item[carousel_item['type'] + 's']['standard_resolution']['url'].split('?')[0]
                urls.append(self.get_original_image(url))
        else:
            url = item[item['type'] + 's']['standard_resolution']['url'].split('?')[0]
            urls.append(self.get_original_image(url))

        item['urls'] = urls
        return item

    def extract_tags(self, item):
        """Extracts the hashtags from the caption text."""
        caption_text = ''
        if 'caption' in item and item['caption']:
            if isinstance(item['caption'], dict):
                caption_text = item['caption']['text']
            else:
                caption_text = item['caption']

        elif 'edge_media_to_caption' in item and item['edge_media_to_caption'] and item['edge_media_to_caption']['edges']:
            caption_text = item['edge_media_to_caption']['edges'][0]['node']['text']

        if caption_text:
            # include words and emojis
            item['tags'] = re.findall(
                r"(?<!&)#(\w+|(?:[\xA9\xAE\u203C\u2049\u2122\u2139\u2194-\u2199\u21A9\u21AA\u231A\u231B\u2328\u2388\u23CF\u23E9-\u23F3\u23F8-\u23FA\u24C2\u25AA\u25AB\u25B6\u25C0\u25FB-\u25FE\u2600-\u2604\u260E\u2611\u2614\u2615\u2618\u261D\u2620\u2622\u2623\u2626\u262A\u262E\u262F\u2638-\u263A\u2648-\u2653\u2660\u2663\u2665\u2666\u2668\u267B\u267F\u2692-\u2694\u2696\u2697\u2699\u269B\u269C\u26A0\u26A1\u26AA\u26AB\u26B0\u26B1\u26BD\u26BE\u26C4\u26C5\u26C8\u26CE\u26CF\u26D1\u26D3\u26D4\u26E9\u26EA\u26F0-\u26F5\u26F7-\u26FA\u26FD\u2702\u2705\u2708-\u270D\u270F\u2712\u2714\u2716\u271D\u2721\u2728\u2733\u2734\u2744\u2747\u274C\u274E\u2753-\u2755\u2757\u2763\u2764\u2795-\u2797\u27A1\u27B0\u27BF\u2934\u2935\u2B05-\u2B07\u2B1B\u2B1C\u2B50\u2B55\u3030\u303D\u3297\u3299]|\uD83C[\uDC04\uDCCF\uDD70\uDD71\uDD7E\uDD7F\uDD8E\uDD91-\uDD9A\uDE01\uDE02\uDE1A\uDE2F\uDE32-\uDE3A\uDE50\uDE51\uDF00-\uDF21\uDF24-\uDF93\uDF96\uDF97\uDF99-\uDF9B\uDF9E-\uDFF0\uDFF3-\uDFF5\uDFF7-\uDFFF]|\uD83D[\uDC00-\uDCFD\uDCFF-\uDD3D\uDD49-\uDD4E\uDD50-\uDD67\uDD6F\uDD70\uDD73-\uDD79\uDD87\uDD8A-\uDD8D\uDD90\uDD95\uDD96\uDDA5\uDDA8\uDDB1\uDDB2\uDDBC\uDDC2-\uDDC4\uDDD1-\uDDD3\uDDDC-\uDDDE\uDDE1\uDDE3\uDDEF\uDDF3\uDDFA-\uDE4F\uDE80-\uDEC5\uDECB-\uDED0\uDEE0-\uDEE5\uDEE9\uDEEB\uDEEC\uDEF0\uDEF3]|\uD83E[\uDD10-\uDD18\uDD80-\uDD84\uDDC0]|(?:0\u20E3|1\u20E3|2\u20E3|3\u20E3|4\u20E3|5\u20E3|6\u20E3|7\u20E3|8\u20E3|9\u20E3|#\u20E3|\\*\u20E3|\uD83C(?:\uDDE6\uD83C(?:\uDDEB|\uDDFD|\uDDF1|\uDDF8|\uDDE9|\uDDF4|\uDDEE|\uDDF6|\uDDEC|\uDDF7|\uDDF2|\uDDFC|\uDDE8|\uDDFA|\uDDF9|\uDDFF|\uDDEA)|\uDDE7\uD83C(?:\uDDF8|\uDDED|\uDDE9|\uDDE7|\uDDFE|\uDDEA|\uDDFF|\uDDEF|\uDDF2|\uDDF9|\uDDF4|\uDDE6|\uDDFC|\uDDFB|\uDDF7|\uDDF3|\uDDEC|\uDDEB|\uDDEE|\uDDF6|\uDDF1)|\uDDE8\uD83C(?:\uDDF2|\uDDE6|\uDDFB|\uDDEB|\uDDF1|\uDDF3|\uDDFD|\uDDF5|\uDDE8|\uDDF4|\uDDEC|\uDDE9|\uDDF0|\uDDF7|\uDDEE|\uDDFA|\uDDFC|\uDDFE|\uDDFF|\uDDED)|\uDDE9\uD83C(?:\uDDFF|\uDDF0|\uDDEC|\uDDEF|\uDDF2|\uDDF4|\uDDEA)|\uDDEA\uD83C(?:\uDDE6|\uDDE8|\uDDEC|\uDDF7|\uDDEA|\uDDF9|\uDDFA|\uDDF8|\uDDED)|\uDDEB\uD83C(?:\uDDF0|\uDDF4|\uDDEF|\uDDEE|\uDDF7|\uDDF2)|\uDDEC\uD83C(?:\uDDF6|\uDDEB|\uDDE6|\uDDF2|\uDDEA|\uDDED|\uDDEE|\uDDF7|\uDDF1|\uDDE9|\uDDF5|\uDDFA|\uDDF9|\uDDEC|\uDDF3|\uDDFC|\uDDFE|\uDDF8|\uDDE7)|\uDDED\uD83C(?:\uDDF7|\uDDF9|\uDDF2|\uDDF3|\uDDF0|\uDDFA)|\uDDEE\uD83C(?:\uDDF4|\uDDE8|\uDDF8|\uDDF3|\uDDE9|\uDDF7|\uDDF6|\uDDEA|\uDDF2|\uDDF1|\uDDF9)|\uDDEF\uD83C(?:\uDDF2|\uDDF5|\uDDEA|\uDDF4)|\uDDF0\uD83C(?:\uDDED|\uDDFE|\uDDF2|\uDDFF|\uDDEA|\uDDEE|\uDDFC|\uDDEC|\uDDF5|\uDDF7|\uDDF3)|\uDDF1\uD83C(?:\uDDE6|\uDDFB|\uDDE7|\uDDF8|\uDDF7|\uDDFE|\uDDEE|\uDDF9|\uDDFA|\uDDF0|\uDDE8)|\uDDF2\uD83C(?:\uDDF4|\uDDF0|\uDDEC|\uDDFC|\uDDFE|\uDDFB|\uDDF1|\uDDF9|\uDDED|\uDDF6|\uDDF7|\uDDFA|\uDDFD|\uDDE9|\uDDE8|\uDDF3|\uDDEA|\uDDF8|\uDDE6|\uDDFF|\uDDF2|\uDDF5|\uDDEB)|\uDDF3\uD83C(?:\uDDE6|\uDDF7|\uDDF5|\uDDF1|\uDDE8|\uDDFF|\uDDEE|\uDDEA|\uDDEC|\uDDFA|\uDDEB|\uDDF4)|\uDDF4\uD83C\uDDF2|\uDDF5\uD83C(?:\uDDEB|\uDDF0|\uDDFC|\uDDF8|\uDDE6|\uDDEC|\uDDFE|\uDDEA|\uDDED|\uDDF3|\uDDF1|\uDDF9|\uDDF7|\uDDF2)|\uDDF6\uD83C\uDDE6|\uDDF7\uD83C(?:\uDDEA|\uDDF4|\uDDFA|\uDDFC|\uDDF8)|\uDDF8\uD83C(?:\uDDFB|\uDDF2|\uDDF9|\uDDE6|\uDDF3|\uDDE8|\uDDF1|\uDDEC|\uDDFD|\uDDF0|\uDDEE|\uDDE7|\uDDF4|\uDDF8|\uDDED|\uDDE9|\uDDF7|\uDDEF|\uDDFF|\uDDEA|\uDDFE)|\uDDF9\uD83C(?:\uDDE9|\uDDEB|\uDDFC|\uDDEF|\uDDFF|\uDDED|\uDDF1|\uDDEC|\uDDF0|\uDDF4|\uDDF9|\uDDE6|\uDDF3|\uDDF7|\uDDF2|\uDDE8|\uDDFB)|\uDDFA\uD83C(?:\uDDEC|\uDDE6|\uDDF8|\uDDFE|\uDDF2|\uDDFF)|\uDDFB\uD83C(?:\uDDEC|\uDDE8|\uDDEE|\uDDFA|\uDDE6|\uDDEA|\uDDF3)|\uDDFC\uD83C(?:\uDDF8|\uDDEB)|\uDDFD\uD83C\uDDF0|\uDDFE\uD83C(?:\uDDF9|\uDDEA)|\uDDFF\uD83C(?:\uDDE6|\uDDF2|\uDDFC))))[\ufe00-\ufe0f\u200d]?)+",
                caption_text, re.UNICODE)
            item['tags'] = list(set(item['tags']))

        return item

    def get_original_image(self, url):
        """Gets the full-size image from the specified url."""
        # remove dimensions to get largest image
        url = re.sub(r'/s\d{3,}x\d{3,}/', '/', url)
        # get non-square image if one exists
        url = re.sub(r'/c\d{1,}.\d{1,}.\d{1,}.\d{1,}/', '/', url)
        return url

    def set_story_url(self, item):
        """Sets the story url."""
        urls = []
        if 'video_versions' in item:
            urls.append(item['video_versions'][0]['url'].split('?')[0])
        if 'image_versions2' in item:
            urls.append(self.get_original_image(item['image_versions2']['candidates'][0]['url'].split('?')[0]))
        item['urls'] = urls
        return item

    def download(self, item, save_dir='./'):
        """Downloads the media file."""
        for url in item['urls']:
            base_name = url.split('/')[-1]
            file_path = os.path.join(save_dir, base_name)

            if not os.path.isfile(file_path):
                with open(file_path, 'wb') as media_file:
                    try:
                        content = self.session.get(url).content
                    except requests.exceptions.ConnectionError:
                        time.sleep(5)
                        content = self.session.get(url).content

                    media_file.write(content)

                file_time = int(item.get('created_time', item.get('taken_at', item.get('date', time.time()))))
                os.utime(file_path, (file_time, file_time))

    def is_new_media(self, item):
        """Returns True if the media is new."""
        return self.latest is False or self.last_scraped_filemtime == 0 or \
               ('created_time' not in item and 'date' not in item) or \
               (int(item.get('created_time', item.get('date'))) > self.last_scraped_filemtime)

    @staticmethod
    def __search(query):
        resp = requests.get(SEARCH_URL.format(query))
        return json.loads(resp.text)

    def search_locations(self):
        query = ' '.join(self.usernames)
        result = self.__search(query)

        if len(result['places']) == 0:
            raise ValueError("No locations found for query '{0}'".format(query))

        sorted_places = sorted(result['places'], key=itemgetter('position'))

        for item in sorted_places[0:5]:
            place = item['place']
            print('location-id: {0}, title: {1}, subtitle: {2}, city: {3}, lat: {4}, lng: {5}'.format(
                place['location']['pk'],
                place['title'],
                place['subtitle'],
                place['location']['city'],
                place['location']['lat'],
                place['location']['lng']
            ))

    @staticmethod
    def save_json(data, dst='./'):
        """Saves the data to a json file."""
        if data:
            with open(dst, 'wb') as f:
                json.dump(data, codecs.getwriter('utf-8')(f), indent=4, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def get_logger(level=logging.DEBUG, verbose=0):
        """Returns a logger."""
        logger = logging.getLogger(__name__)

        fh = logging.FileHandler('instagram-scraper.log', 'w')
        fh.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
        fh.setLevel(level)
        logger.addHandler(fh)

        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter( logging.Formatter('%(levelname)s: %(message)s') )
        sh_lvls = [logging.ERROR, logging.WARNING, logging.INFO]
        sh.setLevel(sh_lvls[verbose])
        logger.addHandler(sh)

        return logger

    @staticmethod
    def parse_file_usernames(usernames_file):
        """Parses a file containing a list of usernames."""
        users = []

        try:
            with open(usernames_file) as user_file:
                for line in user_file.readlines():
                    # Find all usernames delimited by ,; or whitespace
                    users += re.findall(r'[^,;\s]+', line)
        except IOError as err:
            raise ValueError('File not found ' + err)

        return users

    @staticmethod
    def parse_delimited_str(input):
        """Parse the string input as a list of delimited tokens."""
        return re.findall(r'[^,;\s]+', input)


def main():
    parser = argparse.ArgumentParser(
        description="instagram-scraper scrapes and downloads an instagram user's photos and videos.",
        epilog=textwrap.dedent("""
        You can hide your credentials from the history, by reading your
        username from a local file:

        $ instagram-scraper @insta_args.txt user_to_scrape

        with insta_args.txt looking like this:
        -u=my_username
        -p=my_password

        You can add all arguments you want to that file, just remember to have
        one argument per line.

        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@')

    parser.add_argument('username', help='Instagram user(s) to scrape', nargs='*')
    parser.add_argument('--destination', '-d', default='./', help='Download destination')
    parser.add_argument('--login-user', '--login_user', '-u', default=None, help='Instagram login user')
    parser.add_argument('--login-pass', '--login_pass', '-p', default=None, help='Instagram login password')
    parser.add_argument('--login-only', '--login_only', '-l', default=False, action='store_true', help='Disable anonymous fallback if login fails')
    parser.add_argument('--filename', '-f', help='Path to a file containing a list of users to scrape')
    parser.add_argument('--quiet', '-q', default=False, action='store_true', help='Be quiet while scraping')
    parser.add_argument('--maximum', '-m', type=int, default=0, help='Maximum number of items to scrape')
    parser.add_argument('--retain-username', '--retain_username', '-n', action='store_true', default=False,
                        help='Creates username subdirectory when destination flag is set')
    parser.add_argument('--media-metadata', '--media_metadata', action='store_true', default=False, help='Save media metadata to json file')
    parser.add_argument('--include-location', '--include_location', action='store_true', default=False, help='Include location data when saving media metadata')
    parser.add_argument('--media-types', '--media_types', '-t', nargs='+', default=['image', 'video', 'story'], help='Specify media types to scrape')
    parser.add_argument('--latest', action='store_true', default=False, help='Scrape new media since the last scrape')
    parser.add_argument('--tag', action='store_true', default=False, help='Scrape media using a hashtag')
    parser.add_argument('--filter', default=None, help='Filter by tags in user posts', nargs='*')
    parser.add_argument('--location', action='store_true', default=False, help='Scrape media using a location-id')
    parser.add_argument('--search-location', action='store_true', default=False, help='Search for locations by name')
    parser.add_argument('--comments', action='store_true', default=False, help='Save post comments to json file')
    parser.add_argument('--verbose', '-v', type=int, default=0, help='Logging verbosity level')

    args = parser.parse_args()

    if (args.login_user and args.login_pass is None) or (args.login_user is None and args.login_pass):
        parser.print_help()
        raise ValueError('Must provide login user AND password')

    if not args.username and args.filename is None:
        parser.print_help()
        raise ValueError('Must provide username(s) OR a file containing a list of username(s)')
    elif args.username and args.filename:
        parser.print_help()
        raise ValueError('Must provide only one of the following: username(s) OR a filename containing username(s)')

    if args.tag and args.location:
        parser.print_help()
        raise ValueError('Must provide only one of the following: hashtag OR location')

    if args.tag and args.filter:
        parser.print_help()
        raise ValueError('Filters apply to user posts')

    if args.filename:
        args.usernames = InstagramScraper.parse_file_usernames(args.filename)
    else:
        args.usernames = InstagramScraper.parse_delimited_str(','.join(args.username))

    if args.media_types and len(args.media_types) == 1 and re.compile(r'[,;\s]+').findall(args.media_types[0]):
        args.media_types = InstagramScraper.parse_delimited_str(args.media_types[0])

    scraper = InstagramScraper(**vars(args))

    if args.tag:
        scraper.scrape_hashtag()
    elif args.location:
        scraper.scrape_location()
    elif args.search_location:
        scraper.search_locations()
    else:
        scraper.scrape()

if __name__ == '__main__':
    main()
