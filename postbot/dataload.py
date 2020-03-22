import urllib.request
import urllib.parse
import requests
import json

import settings


access_part = f'&access_token={settings.ACCESS_TOKEN}&v={settings.API_V}'
upload_req = 'https://api.vk.com/method/video.save?'+access_part
vk_upload_url = urllib.request.urlopen(upload_req).read().decode('utf-8')
vk_upload_url = json.loads(vk_upload_url)
owner_id = vk_upload_url['response']['owner_id']
video_id = vk_upload_url['response']['video_id']
upload_url = vk_upload_url['response']['upload_url']
video = open('/home/customr/Downloads/1.mp4', 'rb').read()

resp = requests.post(upload_url, files={'video_file': video}).json()
print(resp)