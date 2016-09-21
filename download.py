#-*-coding:utf-8-*-
#download.py

from celery import Celery
import  urllib2

app = Celery('download', broker='redis://172.18.18.47:6379/0')

@app.task
def download(file_name,url):
     req = urllib2.Request(url);
     resp = urllib2.urlopen(req);
     respHtml = resp.read();
     binfile = open(file_name, "wb");
     binfile.write(respHtml);
     binfile.close();
