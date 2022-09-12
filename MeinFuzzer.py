import requests
import sys
import os
import argparse
import threading

parser = argparse.ArgumentParser(description="Web App Fuzzer")
parser.add_argument("-u", "--url", help="Target URL starting with http(s)://")
parser.add_argument("-f", "--fuzzlist", help="The fuzzing payload list")
parser.add_argument("-d", "--direnum", action='store_true', help="Enumerate for directories")

args = parser.parse_args()
initialUrl = args.url
fuzzlist = args.fuzzlist
direnum = args.direnum

if "FUZZ" not in initialUrl:
    print("You have to add FUZZ in your URL where you want to fuzz.")
    print("Exiting..")
    sys.exit()
if os.stat(fuzzlist).st_size == 0:
    print("Fuzz list file is empty.")
    print("Exiting..")
    sys.exit()

fuzzFile = open(fuzzlist).read()
paths = fuzzFile.splitlines()
all_discovered_paths = []
paths_already_checked = []


### Utils ###
def check_for_paths_in_url(paths, url):
    discovered_paths = []
    for path in paths:
        fullUrl = url.replace("FUZZ", path)
        # Do not scan again in paths that do not exist.
        if fullUrl not in paths_already_checked:
            try:
                request = requests.get(fullUrl)
                paths_already_checked.append(fullUrl)
            except requests.ConnectionError:
                pass
            else:
                if not request.status_code == 404:
                    print("[+] Discovered path:", fullUrl)
                    discovered_paths.append(fullUrl)
    # Finally, if any urls found inside this function, append the list to all_discovered_paths
    if len(discovered_paths) != 0:
        all_discovered_paths.extend(discovered_paths)
    return discovered_paths


# Directory Enumeration related only!
def check_for_paths_in_urls(paths, urls):
    discovered_paths = []
    for url in urls:
        if url not in paths_already_checked:
            discovered_paths.extend(check_for_paths_in_url(paths, url))
    return discovered_paths


### Utils ###

check_for_paths_in_url(paths, initialUrl)

if direnum and len(all_discovered_paths) != 0:
    answer = input("Do you want to continue checking inside previously found paths? [Y/n]")
    continueCheckingForPaths = True
    if any(answer.lower() == a for a in ["no", 'n', "NO", 'N', '0']):
        continueCheckingForPaths = False

    if continueCheckingForPaths:
        # Add fuzz to end of each element in previously discovered paths
        fuzzDiscoveredPaths = ["{}/{}".format(i, "FUZZ") for i in all_discovered_paths]
        while True:
            discovered_paths = check_for_paths_in_urls(paths, fuzzDiscoveredPaths)
            if len(discovered_paths) != 0:
                fuzzDiscoveredPaths = ["{}/{}".format(i, "FUZZ") for i in discovered_paths]
            elif len(discovered_paths) == 0:
                break

with open("discovered_paths.txt", "w") as file:
    for discoveredPath in all_discovered_paths:
        file.write(discoveredPath + "\n")

print("Finished.")
