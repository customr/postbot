"""2019
AUTHOR: Shipitsin Maxim
USERNAME: customr
GITHUB: https://github.com/customr/
EMAIL: shipicin_max@mail.ru

Structure:
	-Client: data-manager, keeps all clients attributes and returns batches of data
	-Post: VK-api worker, collaborates with Client

not quite good optimization, but actually we don't need that
because VK-api doesn't allow us to make requests too often

TODO: 
	1. color recognizer, that can make an assembly of similar photos (most common color)
	   based on my other project COLORSCHEME (https://github.com/customr/COLORSCHEME)
	2. add README.md
"""

import os
import re
import requests
import time
from time import sleep, mktime, strftime
from datetime import datetime
from random import choice, shuffle

import settings


class Client:
	"""id-manager, keeps all clients attributes and returns batches of data
	Attrs:
		group_num (int): id or number of group to make posts
		uniq_p (str): yields data while photo id != this value
		uniq_a (str): yields data while audio id != this value
		update (bool): if True, uploads new ids to database

	Params:
		photo_list (list): list of photo ids
		audio_list (list): list of audio ids
		pid (int): photo pointer
		aid (int): audio pointer

	function 'get_ids' is the main function in Client
	it can return for you batch of data in special client's format for one post
	"""
	def __init__(self, group_num, uniq_p='', uniq_a='', update=False):

		if 0<group_num<1000: #otherwise it's unique group id format (9 digits)
			with open('clients_list.txt', 'r') as r_list:
				try:
					group_id = r_list.readlines()[group_num-1]
				except Exception as ex:
					print('Error in client_list.txt\n\n', ex)
				else:
					assert group_num==int(group_id.split('@')[0])
					self.group_id = int(group_id.split('@')[1].rstrip('\n'))

		else:
			self.group_id = group_num

		self.photo_list = []
		self.audio_list = []
		self.unique_photo = uniq_p
		self.unique_audio = uniq_a
		self.update = update

		#check what we need to create
		self.options_exist = os.path.exists(os.path.join(settings.OPTIONS_DIR, str(self.group_id)))
		self.photo_exist = os.path.exists(os.path.join(settings.PHOTO_DIR, str(self.group_id)))
		self.audio_exist = os.path.exists(os.path.join(settings.AUDIO_DIR, str(self.group_id)))

		if not self.options_exist:
			self.create_optionsfile()
		
		self.parse_optionsfile()

		if (not self.photo_exist or not self.audio_exist) or update:
			photo_htmlname = input('\nPhoto album id: ')
			audio_htmlname = ''
			if int(self.COUNT_AUDIO):
				audio_htmlname = input('\nAudio html name: ')

			self.create_mediafiles(photo_htmlname, audio_htmlname)

		self.parse_mediafiles()

	def get_ids(self): #generator that yields data to make 1 post
		counts_photo = int(self.COUNT_PHOTO)
		counts_audio = int(self.COUNT_AUDIO)
		self.pid = 0
		self.aid = 0

		while True:
			data = [[], [], '']
			#even if in our data list will run out of data, we will starts over the list
			if len(self.photo_list)>0:
				for _ in range(counts_photo):
					id = self.photo_list[self.pid%len(self.photo_list)]
					data[0].append(id)

					if id == self.unique_photo:
						raise ValueError('Detected previosly used photo id')

					self.pid += 1 #update pointer

			if len(self.audio_list)>0:
				for _ in range(counts_audio):
					id = self.audio_list[self.aid%len(self.audio_list)]
					data[1].append(id)

					if id == self.unique_audio:
						raise ValueError('Detected previosly used audio id')

					self.aid += 1 #update pointer

			if self.PHRASES:
				data[2] = choice(self.PHRASES)

			yield data

	def save_ids(self, offset=0):
		"""
		Args:
			offset (int): if we need to backup for *offset* days
		"""
		settings_old = open(settings.OPTIONS_DIR + str(self.group_id), 'r').readlines()
		settings_new = open(settings.OPTIONS_DIR + str(self.group_id), 'w+')

		#found lines with id's and saves new values
		for line in settings_old:
			if 'PHOTO_ID' in line:
				new_id = int(line.split(' = ')[1]) + self.pid + offset*int(self.COUNT_PHOTO)
				settings_new.write(f'PHOTO_ID = {new_id}\n')
				self.pid = 0

			elif 'AUDIO_ID' in line:
				new_id = int(line.split(' = ')[1]) + self.aid + offset*int(self.COUNT_AUDIO)
				settings_new.write(f'AUDIO_ID = {new_id}\n')
				self.aid = 0

			else:
				settings_new.write(line)

		settings_new.close()

	def create_mediafiles(self, album_id, audio_html):
		"""
		Args:
			photo_html (str): name of html file that contains in SAVE_DIR
			audio_html (str): name of html file that contains in SAVE_DIR
		"""
		photo_file = open(settings.PHOTO_DIR + str(self.group_id), 'w+')
		audio_file = open(settings.AUDIO_DIR + str(self.group_id), 'w+')
		
		#parse ids from saved on disk html file
		self.photo_ids = Client.album_parser(album_id)
		self.audio_ids = Client.html_parser(audio_html)

		#shuffles data if needed before being saved
		if int(self.SHUFFLE_PHOTO):
			print('SHUFFLING PHOTO')
			shuffle(self.photo_ids)

		if int(self.SHUFFLE_AUDIO):
			print('SHUFFLING AUDIO')
			shuffle(self.audio_ids)

		#loads data into database
		if len(self.photo_ids):
			for uid in self.photo_ids:
				photo_file.write(uid+'\n')

		if len(self.audio_ids):
			for uid in self.audio_ids[1:]: #starts from 1 because of html parse crutch
				audio_file.write(uid+'\n')

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
		with open('clients_list.txt', 'r') as r_list:
			last_id = len(r_list.readlines())

		with open('clients_list.txt', 'a') as w_list:
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
	def album_parser(album_id):
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
			req = request + f'offset={i*1000}' + access_part
			req = requests.get(req)
			req = req.json()

			if 'error' in req.keys():
				raise SystemExit(req['error'])

			for item in req['response']['items']:
				if f'{item["owner_id"]}_{item["id"]}' in all_ids: break
				ids.append(f'{item["owner_id"]}_{item["id"]}')

			all_ids.extend(ids)	

		return all_ids

	@staticmethod
	def html_parser(html_name):
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
	Attrs:
		group_num (int): id or number of group to make posts
		uniq_p (str): yields data while photo id != this value
		uniq_a (str): yields data while audio id != this value
		update (bool): if True, uploads new ids to database
		drange (int): how many days to make posts
		from_day (int): starts from that day
		new_month (int): this month + this value

	Params:
		saveday (int): crutch for new month exception
		id (generator): returns tuples of data to post
	"""
	def __init__(self, group_num, update, uniq_p, uniq_a, drange, from_day, new_month=0):
		self.client = Client(group_num, update, uniq_p, uniq_a)
		self.range = drange
		self.from_day = from_day
		self.new_month = new_month
		self.saveday = 0
		self.id = self.client.get_ids()

	def get_times(self, dshift):
		"""Get list of times to post in mktime format

		Args:
			dshift (int): offset from start
		"""
		y = int(strftime('%Y'))
		m =	int(strftime('%m'))
		d = self.from_day+dshift
		times = []

		for hour in self.client.HOURS:
			try:
				dt = datetime(
					year=y, month=m+self.new_month, 
					day=d-self.saveday, hour=hour, 
					minute=int(self.client.MINUTE)
					)
			except Exception:
				self.new_month += 1
				self.saveday = d+1
				if m+self.new_month>12:
					m = 1
					self.new_month = 0

				dt = datetime(
					year=y, month=m+self.new_month, 
					day=d-self.saveday, hour=hour, 
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

				response = requests.get(req)
				
				if 'error' in response.json().keys():
					self.client.save_ids(-1)
					error = response.json()['error']['error_msg']
					make_log(f'ERROR: {error}')
					raise SystemExit(error)

				sleep(0.5)

		self.client.save_ids()


def make_log(message):
	if settings.LOG:
		with open(settings.LOG_DIR, 'a') as log:
			if message:
				ntime = time.strftime('%c')
				message = f'\n[{ntime}] {message}'
				log.write(message)

			else:
				log.write('\n'+'-'*90)