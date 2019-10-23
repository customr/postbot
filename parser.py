import os
import re
import requests

import settings


def album_parser(album_id):
	"""Get photo ids in album by VK-api method

	Args:
		album_id (int): must be in format 'ownerid_albumid'

	Return:
		list with ids
	"""
	album_id = str(album_id).split('_')
	request = 'https://api.vk.com/method/photos.get?'
	request += f'owner_id={album_id[0]}&album_id={album_id[1]}&count=1000'
	request += f'&access_token={settings.ACCESS_TOKEN}&v={settings.API_V}'

	req = requests.get(request)
	req = req.json()

	ids = []
	for item in req['response']['items']:
		ids.append(f'{item["owner_id"]}_{item["id"]}')

	return ids[::-1]


def html_parser(html_name):
	"""VK-api haven't get-method for audio, so i decided to parse them from html 
	
	Args:
		html_name (str): name of saved html file in SAVE_DIR

	Return:
		list with ids
	"""
	def ordered_set(array):
		orset = []

		for item in array:
			if item not in orset:
				orset.append(item)

		return orset

	if html_name != '':
		html_file = open(os.path.join(settings.SAVE_DIR, html_name+'.html'), 'r', encoding="latin-1").read()
		ids = re.findall(r'\d{9}_\d{9}|-\d{8}_\d{9}', html_file) #search id in that unique format

		return ordered_set(ids)

	return []
