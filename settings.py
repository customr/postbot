import os


#paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, 'clients/photo/')
AUDIO_DIR = os.path.join(BASE_DIR, 'clients/audio/')
OPTIONS_DIR = os.path.join(BASE_DIR, 'clients/options/')
ACCESS_TOKEN_DIR = os.path.join(BASE_DIR, 'access_token.txt')
HTML_DIR = '/home/customr/Downloads' #where html files have been saved

if not os.path.exists(ACCESS_TOKEN_DIR):
	open(ACCESS_TOKEN_DIR, 'w').write(input('Access token: ')).close()

#read access token
ACCESS_TOKEN = open(ACCESS_TOKEN_DIR, 'r').readline()

#api settings
API_V = 5.92


#default user params
OPTIONS_PARAMS = (
	'GROUP_ID', #group where make posts
	'COUNT_PHOTO', #how much photos per post
	'COUNT_AUDIO', #how much audio per post
	'PHRASES', #sequence of phrases to choice
	'HOURS', #hours to post everyday
	'MINUTE', #minute of post time
	'PHOTO_ID', #last posted photo pointer
	'AUDIO_ID', #last posted audio pointer
	'PHOTO_URL', #url of photos to post
	'AUDIO_URL', #url of audios to post
	'RENT_FROM', #date from where bot were rented
	'USER_ID' #client id
	)