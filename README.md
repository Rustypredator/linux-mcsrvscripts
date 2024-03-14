# Linux MC Server Scripts
  
This Repository contains a few scripts i use to control my Minecraft Servers.  
The Scripts are intended to be cloned with each server and modified according to each servers settings.  

## Prerequisites:
- mcrcon
- screen
- java (duh)

#### Start
This Script starts the Server Process in a screen.  
Update "CHANGEME" to be your servers name. this should be unique among your servers.  
Also replace the "-jar server.jar -nogui" part with your own start command if needed.

#### Stop
This Script sends an rcon command to stop the server.  
Here you only need to update the path to the rcon script corresponding to the server.  
If your server doesnt support rcon, idk if there is a mc server that doesnt but i dont know everything, you can replace the rcon command line with the following:  
```bash
screen -X -S CHANGEME stop
```
This sends the "stop" command to the screen (Change the name "CHANGEME" here again.)

#### rcon
This script contains the settings for the server its associated with:
- rcon port
- rcon password
For this to work, the server obviously needs to have rcon enabled and SET A PASSWORD!!!!  

#### Watchdog
Finally, this script verifies that the server is actually started and responsive (by checking the response of the "list" command.)  
If it detects that there is no screen for the server, it is started.  
If it detects a screen does exist, it checks the response of "list" to see if the server is responsive.  
If the server isnt responding, the server is killed and restarted.