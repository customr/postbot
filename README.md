![](https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/VK.com-logo.svg/1200px-VK.com-logo.svg.png)
#Posting bot for VK

Created for simplify life of VK-group editors.

###Scope
Editor of community group only need to add photos or audio to special place
and then they can be posted in his VK-group with his flexible settings

##Sample how to run it
`python3 run.py -g=*your group id* -r=**`

##Contents
- folder "clients" (keeps all clients settings and data)
- core.py (main file, contains Client and Postbot classes)
- settings.py (managing files and set global options)
- run.py (sample code how you can run it)
- logs.txt (saves all posting history)
- clients.txt (you can use this numeric contractions instead of full group id)
- access_token.txt (contains your VK-api access token)

##Credits
Written by Maksim Shipitsin (2019)
[VK](https://vk.com/mshipits)