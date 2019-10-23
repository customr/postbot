import os


#paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, 'clients/photo/')
AUDIO_DIR = os.path.join(BASE_DIR, 'clients/audio/')
OPTIONS_DIR = os.path.join(BASE_DIR, 'clients/options/')
ACCESS_TOKEN_DIR = os.path.join(BASE_DIR, 'access_token.txt')
CLIENTS_LIST_DIR = os.path.join(BASE_DIR, 'clients_list.txt')

SAVE_DIR = '/home/customr/Downloads' #where html files should be saved


#create dir's and file's if not exists
for directory in (PHOTO_DIR, AUDIO_DIR, OPTIONS_DIR):
	if not os.path.exists(directory):
		os.makedirs(directory)

if not os.path.exists(ACCESS_TOKEN_DIR):
	open(ACCESS_TOKEN_DIR, 'w').write(input('VK access token: ')).close()

if not os.path.exists(CLIENTS_LIST_DIR):
	open(CLIENTS_LIST_DIR, 'w')


#read access token
ACCESS_TOKEN = open(ACCESS_TOKEN_DIR, 'r').readline()
API_V = 5.92


#default user params
OPTIONS_PARAMS = (
	'GROUP_ID', 	#group id or num where to make posts
	'COUNT_PHOTO', 	#how much photos per post
	'COUNT_AUDIO', 	#how much audio per post
	'PHRASES', 		#phrases to choice with comma separator
	'HOURS', 		#hours to post everyday comma separated
	'MINUTE', 		#minute of post time
	'PHOTO_ID', 	#last posted photo pointer
	'AUDIO_ID', 	#last posted audio pointer
	'PHOTO_URL', 	#url of photos to post
	'AUDIO_URL', 	#url of audios to post
	'SHUFFLE_AUDIO',#flag for randomly shuffles audio data
	'RENT_FROM', 	#date from where bot were rented
	'USER_URL' 		#client vk page
	)