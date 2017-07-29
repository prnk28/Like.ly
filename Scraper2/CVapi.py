# The inputs to this file are the JSON that are created via the instagram-scraper
# In this file, each image_link in each JSON will be sent to the Microsoft Computer Vision API
# The relevant information returned will be added to the JSON, and sent to the server


import json
import httplib, urllib, base64, json

with open('/media/akanumuru/Windows/Users/Arun/Google Drive/Project_Aditi/Project-Aditi/Scraper2/instagram-scraper/test/thisisprad/thisisprad.json') as json_data:
    d = json.load(json_data)

# print len(d)
# for i in range(0, len(d)):
#     image_link = d[i]['image_link']
#     # make microsoft CV call here
#     print d[i]['image_link']
image_link = d[0]['image_link']

########### Python 2.7 #############
import httplib, urllib, base64

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '7eb7e9da359d4d02b4ef770238913c0f',
}

params = urllib.urlencode({
})

try:
    conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
    conn.request("POST", "/vision/v1.0/tag?%s" % params, {"url" : "https://scontent-iad3-1.cdninstagram.com/t51.2885-15/s640x640/sh0.08/e35/c0.134.1080.1080/19931591_913758048774760_8137673633788067840_n.jpg"}, headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################
