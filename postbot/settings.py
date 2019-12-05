"""2019
AUTHOR: Maksim Shipitsin
USERNAME: customr
GITHUB: https://github.com/customr/

!!!KEEP THIS SETTINGS FILE WITH core.py
"""
import os


#paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, 'clients/photo/')
AUDIO_DIR = os.path.join(BASE_DIR, 'clients/audio/')
OPTIONS_DIR = os.path.join(BASE_DIR, 'clients/options/')
ACCESS_TOKEN_DIR = os.path.join(BASE_DIR, 'access_token.txt')
CLIENTS_LIST_DIR = os.path.join(BASE_DIR, 'clients_list.txt')
LOG_DIR = os.path.join(BASE_DIR, 'logs.txt')

SAVE_DIR = '/home/customr/Downloads' #where html files should be saved (for id parsing)


#create dir's and file's if not exists
for directory in (PHOTO_DIR, AUDIO_DIR, OPTIONS_DIR):
	if not os.path.exists(directory):
		os.makedirs(directory)

if not os.path.exists(ACCESS_TOKEN_DIR):
	open(ACCESS_TOKEN_DIR, 'w').write(input('VK access token: ')).close()

if not os.path.exists(CLIENTS_LIST_DIR):
	open(CLIENTS_LIST_DIR, 'w').close()

if not os.path.exists(LOG_DIR):
	open(LOG_DIR, 'w').close()


#get access token
ACCESS_TOKEN = open(ACCESS_TOKEN_DIR, 'r').readline()
API_V = 5.92


#default user params
OPTIONS_PARAMS = (
	'GROUP_ID', 	#group id or num where to make posts (int)
	'COUNT_PHOTO', 	#how much photos per post (int)
	'COUNT_AUDIO', 	#how much audio per post (int)
	'PHRASES', 		#phrases to choice with (comma separated) (str)
	'HOURS', 		#hours to post everyday (comma separated) (int)
	'MINUTE', 		#minute of post time (int)
	'PHOTO_ID', 	#last posted photo pointer (int)
	'AUDIO_ID', 	#last posted audio pointer (int)
	'PHOTO_URL', 	#url of photos to post (str)
	'AUDIO_URL', 	#url of audios to post (str)
	'SHUFFLE_PHOTO',#flag for randomly shuffles photo data (bool)
	'SHUFFLE_AUDIO',#flag for randomly shuffles audio data (bool)
	'RENT_FROM', 	#date from where bot were rented (date)
	'USER_URL' 		#client vk page (str)
	)

LOG = True #make logs if True