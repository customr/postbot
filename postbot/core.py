"""2019
AUTHOR: Maksim Shipitsin
USERNAME: customr
GITHUB: https://github.com/customr/

Structure:
	-Client: data-manager, keeps all clients attributes and returns batches of data
	-Post: VK-api worker, collaborates with Client

not quite good optimization, but actually we don't need that
because VK-api doesn't allow us to make requests too often

!!KEEP THIS FILE TOGETHER WITH settings.py

TODO: 
	1. color recognizer, that can make an assembly of similar photos (most common color)
	   based on my other project COLORSCHEME (https://github.com/customr/COLORSCHEME)
	2. update README.md
"""

import os
import re
import json
import time
import urllib.request
from time import sleep, mktime, strftime
from datetime import datetime
from random import choice, shuffle

import postbot.settings as settings


class Client:
	"""id-manager, keeps all clients attributes and returns batches of data
	Params:
		group_num (int): id or number of group to make posts
		update (bool): if True, uploads new ids to database

	Attrs:
		photo_list (list): list of photo ids
		audio_list (list): list of audio ids
		pid (int): photo pointer
		aid (int): audio pointer

	function 'get_ids' is the main function in Client
	it can return for you batch of data in special client's format for one post
	"""
	def __init__(self, group_num:int, update:bool=False):

		if 0<group_num<1000: #otherwise it's unique group id format (9 digits)
			with open(settings.CLIENTS_LIST_DIR, 'r') as r_list:
				try:
					group_id = r_list.readlines()[group_num-1]
				except Exception as ex:
					print('Incorrect group_num\n\n', ex)
				else:
					assert group_num==int(group_id.split('@')[0])
					self.group_id = int(group_id.split('@')[1].rstrip('\n'))

		else:
			self.group_id = group_num

		self.photo_list = []
		self.audio_list = []
		self.update = update

		#check what we need to create
		self.options_exist = os.path.exists(os.path.join(settings.OPTIONS_DIR, str(self.group_id)))
		self.photo_exist = os.path.exists(os.path.join(settings.PHOTO_DIR, str(self.group_id)))
		self.audio_exist = os.path.exists(os.path.join(settings.AUDIO_DIR, str(self.group_id)))

		if not self.options_exist:
			self.create_optionsfile()
		
		self.parse_optionsfile()

		if (not self.photo_exist or not self.audio_exist) or update:
			photoalbum_id = input('\nPhoto album id: ')
			audio_htmlname = ''
			self.create_mediafiles(photoalbum_id)

		if self.update: 
			self.PHOTO_ID = 0
			self.AUDIO_ID = 0

		self.parse_mediafiles()

	def get_ids(self): #generator that yields data to make 1 post
		counts_photo = int(self.COUNT_PHOTO)
		counts_audio = int(self.COUNT_AUDIO)
		self.pid = 0
		self.aid = 0

		while True:
			data = [[], [], '']
			if self.FIRST_PHOTO: data[0].append(self.FIRST_PHOTO) #ignore this... it's just for my purpose

			#even if in our data list will run out of data, we will starts over the list
			if len(self.photo_list)>0:
				for _ in range(counts_photo):
					id = self.photo_list[self.pid%len(self.photo_list)]
					data[0].append(id)

					self.pid += 1 #update 

					if self.UNIQ_DATA:
						if self.pid >= self.pid_diff:
							make_log(f'\n\t ENDED NEW PHOTO IDS. STOPPING')
							raise ValueError('ended new photo ids')

			if len(self.audio_list)>0:
				for _ in range(counts_audio):
					id = self.audio_list[self.aid%len(self.audio_list)]
					data[1].append(id)

					self.aid += 1 #update pointer

			if self.PHRASES:
				data[2] = choice(self.PHRASES)

			yield data

	def save_ids(self, offset:int=0):
		"""saving new ids to the options file
		Args:
			offset (int): if we need to backup for *offset* days
		"""
		settings_old = open(settings.OPTIONS_DIR + str(self.group_id), 'r').readlines()
		settings_new = open(settings.OPTIONS_DIR + str(self.group_id), 'w+')

		#found lines with id's and saves new values
		for line in settings_old:
			if 'PHOTO_ID' in line:
				new_id = int(line.split(' = ')[1]) + self.pid + offset*int(self.COUNT_PHOTO)
				if self.update: 
					new_id = self.pid + offset*int(self.COUNT_PHOTO)
				settings_new.write(f'PHOTO_ID = {new_id}\n')
				self.pid = 0

			elif 'AUDIO_ID' in line:
				new_id = int(line.split(' = ')[1]) + self.aid + offset*int(self.COUNT_AUDIO)
				if self.update: 
					new_id = self.aid + offset*int(self.COUNT_AUDIO)
				settings_new.write(f'AUDIO_ID = {new_id}\n')
				self.aid = 0

			else:
				settings_new.write(line)

		settings_new.close()

	def create_mediafiles(self, album_id:str):
		"""parsing data ids and saving it into data files
		Args:
			photo_html (str): name of html file that contains in SAVE_DIR
			audio_html (str): name of html file that contains in SAVE_DIR
		"""
		if self.UNIQ_DATA:
			pcount_old = len(open(settings.PHOTO_DIR + str(self.group_id), 'rb').read())//20

		photo_file = open(settings.PHOTO_DIR + str(self.group_id), 'w+')
		self.photo_ids = Client.album_parser(album_id)

		#shuffles data if needed before being saved
		if int(self.SHUFFLE_PHOTO):
			print('SHUFFLING PHOTO')
			shuffle(self.photo_ids)

		#loads data into database
		if len(self.photo_ids):
			for uid in self.photo_ids:
				photo_file.write(uid+'\n')

		if self.UNIQ_DATA:
			self.pid_diff = len(self.photo_ids) - pcount_old
			assert self.pid_diff>0, "parsing difference error"
			print(f'PHOTO TO POST: {self.pid_diff}')

	def parse_mediafiles(self):
		#get file with ids from base
		photo_file = open(settings.PHOTO_DIR + str(self.group_id), 'r')
		
		#uploads data to client
		for uid in photo_file.readlines()[int(self.PHOTO_ID):]:
			self.photo_list.append(uid.rstrip('\n'))

		#if we have audio list to post with
		if self.audio_exist:
			audio_file = open(settings.AUDIO_DIR + str(self.group_id), 'r')

			for uid in audio_file.readlines()[int(self.AUDIO_ID):]:
				self.audio_list.append(uid.rstrip('\n'))


	def create_optionsfile(self):
		options_file = open(settings.OPTIONS_DIR + str(self.group_id), 'w+')

		for param in settings.OPTIONS_PARAMS:
			#if we have that parameter, we want to keep him in settings
			if param.lower() in self.__dict__.keys():
				options_file.write(f'{param} = {getattr(self, param.lower())}\n')
			else:
				options_file.write(f'{param} = \n')

		options_file.close()

		#get last group number for writing next
		with open(settings.CLIENTS_LIST_DIR, 'r') as r_list:
			last_id = len(r_list.readlines())

		with open(settings.CLIENTS_LIST_DIR, 'a') as w_list:
			if last_id==0:
				w_list.write(f'1@{self.group_id}')
			else:
				w_list.write(f'\n{last_id+1}@{self.group_id}')

		input('Please, set client options (/clients/options/)... [Press ENTER if ready to parse it]')
		
	def parse_optionsfile(self):
		options_file = open(os.path.join(settings.OPTIONS_DIR, str(self.group_id)), 'r')

		for option in options_file.readlines():
			param, value = option.split(' = ')
			setattr(self, param, value.rstrip('\n'))

		#parameters that required more complicated parsing procedures
		self.HOURS = list(map(int, self.HOURS.split(',')))
		self.MINUTE = int(self.MINUTE)
		self.PHRASES = self.PHRASES.split(',')

	@staticmethod
	def album_parser(album_id:str):
		"""Get photo ids in album by VK-api method

		Args:
			album_id (int): must be in format 'ownerid_albumid'

		Return:
			list with ids
		"""
		album_id = str(album_id).split('_')
		access_part = f'&access_token={settings.ACCESS_TOKEN}&v={settings.API_V}&'
		request = 'https://api.vk.com/method/photos.get?'
		request += f'owner_id={album_id[0]}&album_id={album_id[1]}&count=1000&rev=1'

		#because vk-api won't give us a permission 
		#to parse more than 1000 photos per one request 
		all_ids = []
		for i in range(10):
			ids = []
			req = request + f'&offset={i*1000+1}' + access_part
			req = urllib.request.urlopen(req).read().decode('utf-8')
			req = json.loads(req)

			if 'error' in req.keys():
				raise SystemExit(req['error'])

			for item in req['response']['items']:
				if f'{item["owner_id"]}_{item["id"]}' in all_ids: break
				ids.append(f'{item["owner_id"]}_{item["id"]}')

			all_ids.extend(ids)	

		return all_ids

	@staticmethod
	def html_parser(html_name:str):
		"""VK-api haven't get-method for audio, so i decided to parse them from html 
		
		Args:
			html_name (str): name of saved html file in SAVE_DIR

		Return:
			list with ids
		"""
		def ordered_set(array):
			#unique values with the same order
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


class PostBot:
	"""working in pair with client, scope - make posts
	Params:
		group_num (int): id or number of group to make posts
		update (bool): if True, uploads new ids to database
		drange (int): how many days to make posts
		from_day (int): starts from that day
		month (int): posting on this month
		year (int): posting on this year

	Attrs:
		id (generator): returns tuples of data to post
	"""
	def __init__(self, group_num, drange, from_day, update, month=0, year=0):
		self.client = Client(group_num, update)
		self.range = int(drange)
		self.from_day = int(from_day)
		self.month = int(month)
		self.year = int(year)
		self.id = self.client.get_ids()

	def get_times(self, dshift:int):
		"""Get list of times to post in mktime format

		Args:
			dshift (int): offset from start
		"""
		y = self.year if self.year else int(strftime('%Y'))
		m = self.month if self.month else int(strftime('%m'))
		d = self.from_day+dshift
		times = []

		for hour in self.client.HOURS:
			dt = datetime(
				year=y, month=m, day=d, hour=hour, 
				minute=int(self.client.MINUTE)
				)

			times.append(int(mktime(dt.timetuple())))

		return times

	def run(self): #main loop
		info = f'\nGROUP={self.client.group_id}\nRANGE={self.range}\nFROM_DAY={self.from_day}'
		make_log('') #means we want print separator
		make_log(info)

		for day in range(self.range):
			times = self.get_times(day)
			sleep(0.2)
			for d in range(len(times)):
				try:
					data = next(self.id) #[[photos], [audios], [phrase]]

				except StopIteration: #starts over the list again
					self.id = self.client.get_ids()
					data = next(self.id)

				attachments = ','.join([f'photo{photo}' for photo in data[0]]+[f'audio{audio}' for audio in data[1]])
				
				req = 'https://api.vk.com/method/wall.post?'
				req += f'owner_id={self.client.group_id}&from_group=1'
				req += f'&attachments={attachments}&message={data[2]}&publish_date={times[d]}'
				req += f'&access_token={settings.ACCESS_TOKEN}&v={settings.API_V}'

				ntime = datetime.fromtimestamp(times[d])
				ntime = ntime.strftime('%m/%d %H:%M:%S')
				make_log(f'\n\tPOST: {attachments} TIME={ntime}')

				req = urllib.request.urlopen(req).read().decode('utf-8')
				req = json.loads(req)
				
				if 'error' in req.keys():
					self.client.save_ids(-1)
					error = req['error']['error_msg']
					make_log(f'ERROR: {error}')
					raise SystemExit(error)

				sleep(0.5)

		self.client.save_ids()


def make_log(message:str):
	if settings.LOG:
		with open(settings.LOG_DIR, 'a') as log:
			if message:
				ntime = time.strftime('%c')
				message = f'\n[{ntime}] {message}'
				log.write(message)

			else:
				log.write('\n'+'-'*90)