import requests
import sys
import os
import argparse
import threading

parser = argparse.ArgumentParser(description="Web App Fuzzer")
parser.add_argument("-u", "--url", help="Target URL starting with http(s)://")
parser.add_argument("-f", "--fuzzlist", help="The fuzzlist")
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
discovered_paths = []
paths_already_checked = []
fullUrl = ""

### Utils ###
def check_for_path(paths, url):
    discovered_at_least_one_path = True
    for path in paths:
        fullUrl = url.replace("FUZZ", path)
        # Do not scan again in paths that do not exist.
        if fullUrl not in paths_already_checked:
            #print("Checking URL " + fullUrl)
            try:
                request = requests.get(fullUrl)
                paths_already_checked.append(fullUrl)
            except requests.ConnectionError:
                print("discovered at least one path set to false")
                discovered_at_least_one_path = False
                pass
            else:
                if not request.status_code == 404:
                    print("[+] Discovered path:", fullUrl)
                    discovered_paths.append(fullUrl)
    return discovered_at_least_one_path

# Directory Enumeration related only!
def check_for_path_in_urls(paths, urls):
    discovered_at_least_one_path = True
    # split discovered_paths list in 2 (assuming everyone nowadays has at least 2 threats at hand :D)
    #half_length = len(discovered_paths) // 2
    #first_half, second_half = discovered_paths[:half_length], discovered_paths[half_length:]
    #print("First half is " + str(first_half))
    #print("Second half is " + str(second_half))
    for url in urls:
        if url not in paths_already_checked:
            discovered_at_least_one_path = check_for_path(paths, url)
    return discovered_at_least_one_path
### Utils ###

check_for_path(paths, initialUrl)
print("Discovered paths is ")
print(discovered_paths)

if direnum and len(discovered_paths) != 0:
    answer = input("Do you want to continue checking inside previously found paths? [Y/n]")
    continueCheckingForPaths = True
    if any(answer.lower() == a for a in ["no", 'n', "NO", 'N', '0']):
        continueCheckingForPaths = False
    if continueCheckingForPaths:
        discovered_at_least_one_path = True
        while discovered_at_least_one_path:
            # Add fuzz to end of each element in previously discovered paths
            url = ["{}/{}".format(i, "FUZZ") for i in discovered_paths]
            discovered_at_least_one_path = check_for_path_in_urls(paths, url)
            if not discovered_at_least_one_path:
                print("break")
                break
        print("Discovered paths is ")
        print(discovered_paths)

with open("discovered_paths.txt", "w") as file:
    for discoveredPath in discovered_paths:
        file.write(discoveredPath + "\n")

print("Finished.")
