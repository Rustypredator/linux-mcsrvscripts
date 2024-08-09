#!/bin/python3
import os
import sys
import json
import requests
import zipfile
import shutil
import re
import time

baseurl = "https://api.modrinth.com/v2/"
useragent = "packload/0.0.1 (contact@rusty.info)"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    DEBUG = '\033[90m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_usage():
    print(f"Usage: packload {bcolors.OKGREEN}/path/to/mrpack/file/ {bcolors.OKCYAN}/path/to/outputfolder/ {bcolors.WARNING}mode{bcolors.ENDC}")
    print(f" ╰ Available Modes:")
    print(f"   ├ server  {bcolors.DEBUG}// Installs all mods that have server set to \"{bcolors.FAIL}required{bcolors.DEBUG}\" or \"{bcolors.FAIL}optional{bcolors.DEBUG}\"{bcolors.ENDC}")
    print(f"   ╰ client  {bcolors.DEBUG}// Installs all mods that have client set to \"{bcolors.FAIL}required{bcolors.DEBUG}\" or \"{bcolors.FAIL}optional{bcolors.DEBUG}\"{bcolors.ENDC}")

def download(url: str, file_path='', file_name=''):
    url = url.strip("\"'")  # Strip leading and trailing characters
    if not file_name:
        file_name = url.split('/')[-1]
    headers = {"User-Agent": useragent}
    try:
        response = requests.get(url, headers=headers, stream=True)
    except requests.exceptions.RequestException as e:
        print(f"{bcolors.FAIL} error {bcolors.ENDC} {e}")
        sys.exit(1)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar_width = 50

    with open(os.path.join(file_path, file_name), 'wb') as file:
        progress = 0
        for data in response.iter_content(block_size):
            progress += len(data)
            file.write(data)
            completed = int(progress / total_size * progress_bar_width)
            remaining = progress_bar_width - completed
            progress_bar = '[' + '=' * completed + '>' + '.' * remaining + ']'
            sys.stdout.write('\r' + progress_bar)
            sys.stdout.flush()

    sys.stdout.write('\n')
    sys.stdout.flush()

# start here

if len(sys.argv) < 3:
    print_usage()
    exit()

mrpackpath = sys.argv[1]
outputpath = sys.argv[2]
mode = sys.argv[3]


# check if outputpath exists:
if not os.path.exists(outputpath):
    os.makedirs(outputpath)

print(f"{bcolors.OKCYAN} info {bcolors.ENDC} unzipping mrpack file...")
with zipfile.ZipFile(mrpackpath, 'r') as zip_ref:
    zip_ref.extractall("tmp")

with open("tmp/modrinth.index.json", "r") as file:
    data = file.read()
    regex = r"\"https:\/\/cdn\.modrinth\.com\/data\/([a-zA-Z0-9-]+)\/.*\""
    matches = re.finditer(regex, data, re.MULTILINE)
    match_array = []
    for matchNum, match in enumerate(matches, start=1):
        match_dict = {}
        match_dict["url"] = match.group(0)
        match_dict["id"] = match.group(1)
        match_array.append(match_dict)
    for match in match_array:
        downloadUrl = match["url"]
        id = match["id"]
        #check if download is required for mode:
        #request modrinth api:
        try:
            response = requests.get(baseurl + "project/" + id, headers={"User-Agent": useragent})
        except requests.exceptions.RequestException as e:
            print(f"{bcolors.FAIL} error {bcolors.ENDC} {e}")
            sys.exit(1)
        headers = response.headers
        if headers["X-RateLimit-Remaining"] == "0":
            resetTimer = int(headers["X-RateLimit-Reset"])
            print(f"{bcolors.FAIL} error {bcolors.ENDC} Rate limit reached, waiting {resetTimer} seconds...")
            time.sleep(resetTimer)
            response = requests.get(baseurl + "project/" + id)
        project = response.json()
        if mode == "server":
            #get field "server_side":
            server_side = project["server_side"]
            if server_side == "required" or server_side == "optional":
                name = project["title"]
                print(f"{bcolors.OKGREEN} downloading {bcolors.ENDC} Mod {name} is required or optional on server.")
                download(downloadUrl, outputpath)
            else:
                name = project["title"]
                print(f"{bcolors.HEADER} skipping {bcolors.ENDC} Mod {name} is not required on server.")
        if mode == "client":
            #get field "client_side":
            client_side = project["client_side"]
            if client_side == "required" or client_side == "optional":
                name = project["title"]
                print(f"{bcolors.OKGREEN} downloading {bcolors.ENDC} Mod {name} is required or optional on client.")
                download(downloadUrl, outputpath)
            else:
                name = project["title"]
                print(f"{bcolors.HEADER} skipping {bcolors.ENDC} Mod {name} is not required on client.")
    # move all files from overrides/mods to outputpath
    for root, dirs, files in os.walk("tmp/overrides/mods"):
        for file in files:
            print(f"{bcolors.WARNING} OVERRIDE {bcolors.ENDC} {file}")
            shutil.move(os.path.join(root, file), outputpath)
print("cleanup")
shutil.rmtree("tmp")
