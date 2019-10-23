"""2019
AUTHOR: Shipitsin Maxim
USERNAME: customr
GITHUB: https://github.com/customr/
EMAIL: shipicin_max@mail.ru

Structure:
	-Client: initializes client, keeps all his attributes
	-Post: VK-api worker, based on Client
"""

import re
import os
import requests
from time import sleep, mktime, strftime
from datetime import datetime
from random import choice, shuffle

import settings
from parser import html_parser, album_parser


class Client:
	"""
	Params:
		group_id (int): id of group to make posts
		photo_list (list): list of photo ids
		audio_list (list): list of audio ids
		update (bool): if True, uploads new ids to database
		pid (int): photo pointer
		aid (int): audio pointer
	"""
	def __init__(self, group_num, update=False):

		if -10000000<group_num<10000000: #otherwise it's unique group id format (9 digits)
			with open('clients_list.txt', 'r') as r_list:
				try:
					group_id = r_list.readlines()[group_num-1]
				except Exception as ex:
					print('Error in client_list.txt\n', ex)
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
					data[0].append(self.photo_list[self.pid%len(self.photo_list)])
					self.pid += 1 #update pointer

			if len(self.audio_list)>0:
				for _ in range(counts_audio):
					data[1].append(self.audio_list[self.aid%len(self.audio_list)])
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
		
		#parse ids from html file
		self.photo_ids = album_parser(album_id)
		self.audio_ids = html_parser(audio_html)

		#loads data into database
		for uid in self.photo_ids:
			photo_file.write(uid+'\n')

		for uid in self.audio_ids:
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

			if int(self.SHUFFLE_AUDIO):
				shuffle(self.audio_list)

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

		input('Waiting for parse settings... [Press ENTER if ready to parse it]')
		
	def parse_optionsfile(self):
		options_file = open(os.path.join(settings.OPTIONS_DIR, str(self.group_id)), 'r')

		for option in options_file.readlines():
			param, value = option.split(' = ')
			setattr(self, param, value)

		self.HOURS = list(map(int, self.HOURS.split(',')))
		self.MINUTE = int(self.MINUTE)
		self.PHRASES = self.PHRASES.split(',')
		

class Post:
	"""
	Params:
		client (Client object): client object
		drange (int): how many days to make posts
		from_day (int): starts from that day
		new_month (bool): if true: posts on the next month
		id (generator): returns tuples of data to post
	"""
	def __init__(self, client, drange, from_day, new_month=0):
		self.client = client
		self.range = drange
		self.from_day = from_day
		self.new_month = new_month
		self.saveday = 0 #crutch for new month exception
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
				dt = datetime(year=y, month=m+self.new_month, day=d-self.saveday, hour=hour, minute=int(self.client.MINUTE))
			except Exception:
				assert self.new_month<2 #leave if we'll get two errors in a row
				self.new_month += 1
				self.from_day -= 1
				self.saveday = d-1
				dt = datetime(year=y, month=m+self.new_month, day=d%self.saveday, hour=hour, minute=int(self.client.MINUTE))

			times.append(int(mktime(dt.timetuple())))

		return times

	def run(self): #main loop
		for day in range(self.range):
			times = self.get_times(day)
			for d in range(len(times)):
				try:
					data = next(self.id)

				except StopIteration: #starts over the list again
					self.id = self.client.get_ids()
					data = next(self.id)

				attachments = ','.join([f'photo{photo}' for photo in data[0]]+[f'audio{audio}' for audio in data[1]])
				
				req = 'https://api.vk.com/method/wall.post?'
				req += f'owner_id={self.client.group_id}&from_group=1'
				req += f'&attachments={attachments}&message={data[2]}&publish_date={times[d]}'
				req += f'&access_token={settings.ACCESS_TOKEN}&v={settings.API_V}'

				print(attachments)

				response = requests.get(req)
				
				if 'error' in response.json().keys():
					self.client.save_ids(-1)
					raise Exception(response.json()['error']['error_msg'])

				sleep(0.3)

		self.client.save_ids()
