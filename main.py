import argparse
import re
import os
import requests
from time import sleep, mktime, strftime
from datetime import datetime
from random import choice

import settings


def ordered_set(array):
	orset = []

	for item in array:
		if item not in orset:
			orset.append(item)

	return orset


class Client:
	"""
	Params:
		group_id (int): id of group to make posts
		update (bool): if True, uploads new ids to database
	"""
	def __init__(self, group_id, update=False):
		self.group_id = group_id
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
			photo_htmlname = input('\nPhoto html name: ')
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

			if len(self.photo_list)>0:
				for _ in range(counts_photo):
					data[0].append(self.photo_list[self.pid%len(self.photo_list)])
					self.pid += 1

			if len(self.audio_list)>0:
				for _ in range(counts_audio):
					data[1].append(self.audio_list[self.aid%len(self.audio_list)])
					self.aid += 1

			if self.PHRASES:
				data[2] = choice(self.PHRASES)

			yield data

	def save_ids(self, offset):
		settings_old = open(settings.OPTIONS_DIR + str(self.group_id), 'r').readlines()
		settings_new = open(settings.OPTIONS_DIR + str(self.group_id), 'w+')

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

	def create_mediafiles(self, photo_html, audio_html):
		photo_file = open(settings.PHOTO_DIR + str(self.group_id), 'w+')
		audio_file = open(settings.AUDIO_DIR + str(self.group_id), 'w+')
		
		#parse ids from html file
		self.photo_ids = Client.html_parseid(photo_html)
		self.audio_ids = Client.html_parseid(audio_html)

		#loads data into database
		for uid in self.photo_ids:
			photo_file.write(uid+'\n')

		for uid in self.audio_ids:
			audio_file.write(uid+'\n')

	def parse_mediafiles(self):
		photo_file = open(settings.PHOTO_DIR + str(self.group_id), 'r')
		
		#uploads data to client
		for uid in photo_file.readlines()[int(self.PHOTO_ID):]:
			self.photo_list.append(uid.rstrip('\n'))

		if self.audio_exist:
			audio_file = open(settings.AUDIO_DIR + str(self.group_id), 'r')

			for uid in audio_file.readlines()[int(self.AUDIO_ID):]:
				self.audio_list.append(uid.rstrip('\n'))

	def create_optionsfile(self):
		options_file = open(settings.OPTIONS_DIR + str(self.group_id), 'w+')

		for param in settings.OPTIONS_PARAMS:
			#if we have that parameter, we want to save him in settings
			if param.lower() in self.__dict__.keys():
				options_file.write(f'{param} = {getattr(self, param.lower())}\n')

			else:
				options_file.write(f'{param} = \n')

		options_file.close()

		input('Waiting for parse settings... [Press ENTER if ready to parse it]')
		
	def parse_optionsfile(self):
		options_file = open(os.path.join(settings.OPTIONS_DIR, str(self.group_id)), 'r')

		for option in options_file.readlines():
			param, value = option.split(' = ')
			setattr(self, param, value)

		self.HOURS = list(map(int, self.HOURS.split(',')))
		self.MINUTE = int(self.MINUTE)
		self.PHRASES = re.findall(r"\w[a-z]*", self.PHRASES)
		
	@staticmethod
	def html_parseid(html_name):
		if html_name != '':
			html_file = open(os.path.join(settings.HTML_DIR, html_name+'.html'), 'r', encoding="latin-1").read()
			ids = re.findall(r'\d{9}_\d{9}|-\d{8}_\d{9}', html_file) #search id in that unique format

			return ordered_set(ids)

		else:
			return []


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
		self.id = self.client.get_ids()

	def get_times(self, dshift):
		"""Get list of times to post in mktime format

		Args:
			dshift (int): offset from start
		"""
		y = int(strftime('%Y'))
		m =	int(strftime('%m'))
		times = []

		for hour in self.client.HOURS:
			dt = datetime(year=y, month=m+self.new_month, day=self.from_day+dshift, hour=hour, minute=int(self.client.MINUTE))
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


if __name__=='__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-g', type=int, 
		help="Group id to post.")
	parser.add_argument('-r', type=int, 
		help="How many days to make posts.")
	parser.add_argument('-d', type=int, 
		help="From which day bot must start posting.")
	parser.add_argument('-u', type=bool, default=False, 
		help="Update mediafiles.")
	parser.add_argument('-m', type=bool, default=False, 
		help="If true - makes posts on the next month.")

	params = vars(parser.parse_args())

	client = Client(params['g'], params['u'])
	bot = Post(client, params['r'], params['d'], params['m'])

	bot.run()