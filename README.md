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
This script verifies that the server is actually started and responsive (by checking the response of the "list" command.)  
If it detects that there is no screen for the server, the server is started.  
If it detects a screen does exist, it checks the response of "list" to see if the server is responsive.  
If the server isnt responding, the server is killed and restarted.
This script takes one argument, the server and therefor the folder name.  
Example: 
`./watchdog survival`  
This will check the server in the "survival" folder and with the same screen name.  
For any action, the scripts inside the servers own folder are used, for example sending the stop command.  
This watchdog is intended to be automated with cronjobs.  
Example:
`* * * * * /home/game/watchdog survival >> /home/game/survival/cron.log`  
This will check the survival server every minute and output the watchdog results in a cron.log file inside the servers folder.

#### Backup
This script backs up the world of the specified server.  
I normally run this script every hour.  
This will create Hourly Backups and archive the last backup of the day (11pm) in a different folder while removing all other backups of the previous day.  
This way you get an daily Backup, while keeping 24 Hours of hourly Backups of your world.  
Keep in mind, that this will consume 24-48 times the space of one backup for just the hourly backups.  
How many daily backups are kept on the disk is not capped! (maybe i'll add another config option for that later if the need arises).  

#### Logpost
This script posts all crash-reports automatically to mclo.gs.  
It will alert you using a Discord Webhook as to where you can find the log.  
Also it can move logs to another folder, so you can manually review it too.  
##### Setup:
- Replace the Discord Webhook URL With your own!
- Use it. `./logpost survival`
- You can also use this with crontab.
    - Example: `* * * * * /home/game/logpost survival`
    - This Example would post any and all crash logs that appear in the configured folder.

#### Questions
Please open an issue or contact me on discord: rustypredator
