import requests
import re
import json
from pathlib import Path
import os
import time
import datetime

def download_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request fails
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading HTML: {e}")
        return None

def extract_json_variable(html_content):
    pattern = r"const json = (\'{.*?\}')"  # Regular expression to match the JSON variable
    match = re.search(pattern, html_content)
    if match:
        json_data = match.group(1)
        return json_data
    else:
        print("JSON variable not found.")
        return None

def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

if __name__ == "__main__":
    directories = [""]
    files = []
    timestamps = []
    url = "http://192.168.0.21:8089"  # Replace with the actual URL
    base_folder = "/Users/joscandreu/Desktop/supernote"
    for i, directory in enumerate(directories):
        html_content = download_html(url + directories[i])
        if html_content:
            json_variable = extract_json_variable(html_content)
            if json_variable:
                #print(f"JSON variable found:\n{json_variable}")
                json_dict = json.loads(json_variable[1:-1])
                #initial addition of directories to scrape
                for item in json_dict["fileList"]:
                    if item["isDirectory"] == True:
                        directories.append(item["uri"])
                    else:
                        if item["extension"] == "note":
                            files.append(item["uri"])
                            timestamps.append(item["date"])
            else:
                print("No JSON variable found in the script tag.")
    for i, file in enumerate(files):
        #dest_dir = Path(base_folder + files[i])
        destination_folder = os.path.dirname(base_folder + files[i])
        if os.path.exists(base_folder + files[i]):
            timestamp_web = time.mktime(datetime.datetime.strptime(timestamps[i], "%Y-%m-%d %H:%M").timetuple())
            #timestamp_disk = time.ctime(os.path.getmtime(base_folder + files[i]))
            #timestamp_disk = time.mktime(datetime.datetime.strptime(os.path.getmtime(base_folder + files[i]), "%a %b %d %H:%M:%S %Y").timetuple())
            timestamp_disk = os.path.getmtime(base_folder + files[i])
            if float(timestamp_web) > float(timestamp_disk):
                download(url + files[i], destination_folder)
                print("last modified: %s" % time.ctime(os.path.getmtime(base_folder + files[i])))
                print(files[i])
        else:
            download(url + files[i], destination_folder)
