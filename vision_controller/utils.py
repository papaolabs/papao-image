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