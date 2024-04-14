#!/usr/bin/env python3

import os
import requests
import sys

APIURL = "https://api.mclo.gs/1/log"
DCWebhook = "https://discord.com/api/webhooks/CHANGEME"

if len(sys.argv) < 2:
    print("Usage: python logpost.py <server>")
    exit(1)

server = sys.argv[1]
backupDir = f"/home/game/backups/logs/{server}"
crashReportsDir = f"/home/game/{server}/crash-reports"

# loop files in crashReportsDir
for file in os.listdir(crashReportsDir):
    if os.path.isfile(os.path.join(crashReportsDir, file)):
        print(f"Found crash log: {file}")
        # post log
        with open(os.path.join(crashReportsDir, file), "r") as f:
            content = f.read()
        response = requests.post(APIURL, data={"content": content})
        # Response is in json format.
        response_json = response.json()
        success = response_json.get("success")
        if success:
            # get urls
            url = response_json.get("url")
            raw = response_json.get("raw")
            id = url.split("/")[-1]
            insightsUrl = f"https://api.mclo.gs/1/insights/{id}"
            print(f" - Posted as {url}.")
            # try to get insights:
            insights = requests.get(insightsUrl).json()
            # get basic info from log:
            basicInfoText = ''
            for el in insights["analysis"]["information"]:
                message = el["message"]
                basicInfoText += f"- {message}"
                # add lines found:
                lines = el["entry"]["lines"]
                for line in lines:
                    number = line["number"]
                    basicInfoText += f" - Found on Line: {number}"
            # get problems from log:
            problemsText = ''
            problemsCounter = 0
            for el in insights["analysis"]["problems"]:
                problemsCounter += 1
                message = el["message"]
                problemsText += f"- {message}"
                # add lines found:
                lines = el["entry"]["lines"]
                for line in lines:
                    number = line["number"]
                    problemsText += f" - Found on Line: {number}"
            # format a discord message.
            messageJson = '{"embeds": [{"title": "CRASH!","description": "There was a crash on '+server+'. (click title)","color": 14680064,"fields": [{"name": "Basic Information","value": "'+basicInfoText+'"},{"name": "There were '+str(problemsCounter)+' Problems detected.","value": "'+problemsText+'"}],"url": "'+url+'","footer": {"text": "'+url+'"}}]}'
            # Send discord webhook
            dwhResponse = requests.post(DCWebhook, data={"embeds": [messageJson]}, headers={"Content-Type": "application/json"})
            if dwhResponse.status_code == 204:
                print(" - Sent to Discord!")
            else:
                print(" - Failed to send to Discord!")
                print(f" - Response: {dwhResponse.json()}")
                print(f" - This was sent: {messageJson}")
                print(" - Using simple message instead.")
                # Send simple message
                dwhResponse = requests.post(DCWebhook, data={"content": f"Crash on {server}: {url}"})
                if dwhResponse.status_code == 204:
                    print("   - Sent to Discord!")
                else:
                    print("   - Failed to send to Discord!")
                    print(f"   - Response: {dwhResponse.json()}")
            # Make sure the target directory exists:
            os.makedirs(os.path.join(backupDir, "crash"), exist_ok=True)
            # move sent file to archive
            os.rename(os.path.join(crashReportsDir, file), os.path.join(backupDir, "crash", os.path.basename(file)))
        else:
            print(" - Failed to upload!")
            print(f" - Response: {response_json}")
