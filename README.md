# Posting bot for VK

Created for simplify life of VK-group editors.

### Scope
Editor of community group only need to add photos or audio to special place
and then they can be scheduled in his VK-group with his flexible settings

## Sample how you can run it
#### Steps:
1. run run.py as a sample below
2. if you run it for the first time for your group, program will be waiting while you not set options in newly created file **/clients/options/*groupid***
3. after options have set correctly, you need to give program information from where you want to get photo and/or audio information
4. for the first time it is all what you need to do

**`python3 run.py -g=123456789 -r=5 -d=1`**

#### run.py flags:
- **-g** (int) - Group number or id
- **-r** (int) - How many days to make posts
- **-d** (int) - From which day bot must start posting
- **-u** (bool) - Update mediafiles if True
- **--pp** (bool) - Posting while didn't met photo id
- **--pa** (bool) - Posting while didn't met audio id
- **-m** (int) - Schedule from this month + this value


## Contents
- folder **clients** (keeps all clients settings and data)
	- *audio*
		- files named *group id*
		these files contains audio ids separated with \n
	- *options*
		- files named *group id*
		these files contain clients options (that written in *settings.py*)
	- *photo*
		- files named *group id*
		these files contains audio ids separated with \n
- **core.py** (main file, contains Client and Postbot classes)
- **settings.py** (managing files and set global options)
- **logs.txt** (saves all posting history)
- **clients.txt** (you can use this numeric contractions instead of full group id)
- **access_token.txt** (contains your VK-api access token)

## Credits
Written by Maksim Shipitsin (2019)
[VK page](https://vk.com/mshipits)
