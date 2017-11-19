import os, tempfile
import shutil
import requests

def download_file(url):
    try:
        res = requests.get(url,stream=True)
        res.raw.decode_content = True
        return res.raw
    except Exception as e:
        print("Error on download file : %s" % e)
        raise e

def download_files(urls):
    try:
        return list(map(lambda x:download_file(x),urls))
    except Exception as e:
        raise e