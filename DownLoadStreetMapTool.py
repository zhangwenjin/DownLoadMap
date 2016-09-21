#!/usr/bin/evn python
# -*- coding:utf-8 -*-

from celery import Celery
import download
from DownLoadStreetMapToolConfig import *
import Tkinter
import time
import tkFileDialog
import globalmaptiles
import os
from Tkinter import StringVar
import urllib
import  urllib2
import thread
import sys
import random
reload(sys)
sys.setdefaultencoding("utf-8")
app = Celery('download', broker='redis://172.18.18.47:6379/0')
class GUI(Tkinter.Frame):
    def __init__(self, root):
        Tkinter.Frame.__init__(self, root)

        #设置多行框架存放组件
        self.frame = [Tkinter.Frame(padx=3, pady=3), Tkinter.Frame(padx=3, pady=3), Tkinter.Frame(padx=3, pady=3), Tkinter.Frame(padx=3, pady=3)]

        #第一行控件
        Tkinter.Label(self.frame[0], text='左上角经纬度：经').pack(side=Tkinter.LEFT)

        ltlo = StringVar()
        ltlo.set('109')#73.666667
        self.leftTopLon = Tkinter.Entry(self.frame[0], textvariable=ltlo)
        self.leftTopLon.pack(side=Tkinter.LEFT)

        Tkinter.Label(self.frame[0], text='维').pack(side=Tkinter.LEFT)

        ltla = StringVar()
        ltla.set('26')#53.550000
        self.leftTopLat = Tkinter.Entry(self.frame[0], textvariable=ltla)
        self.leftTopLat.pack(side=Tkinter.LEFT)

        Tkinter.Label(self.frame[0], text='右下角经纬度：经').pack(side=Tkinter.LEFT)

        rblo = StringVar()
        rblo.set('118')#135.041667
        self.rightBottomLon = Tkinter.Entry(self.frame[0], textvariable=rblo)
        self.rightBottomLon.pack(side=Tkinter.LEFT)

        Tkinter.Label(self.frame[0], text='维').pack(side=Tkinter.LEFT)

        rbla = StringVar()
        rbla.set('20')#3.866667
        self.rightBottomLat = Tkinter.Entry(self.frame[0], textvariable=rbla)
        self.rightBottomLat.pack(side=Tkinter.LEFT)

        self.frame[0].pack(expand=0, fill=Tkinter.X)
        Tkinter.Label(self.frame[0], text='线程').pack(side=Tkinter.LEFT)
        threadNum = StringVar()
        threadNum.set('20')#3.866667
        self.threadNumC = Tkinter.Entry(self.frame[0], textvariable=threadNum)
        self.threadNumC.pack(side=Tkinter.LEFT)
        #第二行控件
        #Tkinter.Label(self.frame[1], text='选择下载地图的服务器').pack(side=Tkinter.LEFT)

       # self.ss = Tkinter.StringVar()
        #self.ss.set(mapServers[0])
        #Tkinter.OptionMenu(self.frame[1], self.ss, *mapServers).pack(side=Tkinter.LEFT)

        self.mapLevelStart = Tkinter.StringVar()
        self.mapLevelStart.set(2)
        self.mapLevelEnd = Tkinter.StringVar()
        self.mapLevelEnd.set(18)

        Tkinter.Label(self.frame[1], text='地图下载起始级别').pack(side=Tkinter.LEFT)
        Tkinter.OptionMenu(self.frame[1], self.mapLevelStart, *range(0, 20)).pack(side=Tkinter.LEFT)
        Tkinter.Label(self.frame[1], text='地图下载终止级别').pack(side=Tkinter.LEFT)
        Tkinter.OptionMenu(self.frame[1], self.mapLevelEnd, *range(0, 20)).pack(side=Tkinter.LEFT)

        #存放目录
        self.btSaveFolder = Tkinter.Button(self.frame[1], text='选择存放目录', command=self.selectSaveFolder)
        self.btSaveFolder.pack(side=Tkinter.LEFT)

        self.btAction = Tkinter.Button(self.frame[1], text='开始下载', bg='red', fg='yellow', command=self.doDownload)
        self.btAction.pack(side=Tkinter.RIGHT, expand=1, fill=Tkinter.X)
        self.frame[1].pack(expand=0, fill=Tkinter.X)

        #第三行控件

        #文本框滚动条
        self.sl = Tkinter.Scrollbar(self.frame[2])
        self.sl.pack(side='right', fill='y')
        #显示结果的文本框
        self.message = Tkinter.Text(self.frame[2], yscrollcommand=self.sl.set)
        #将滚动条的值与文本框绑定，这样滚动条才有作用
        self.sl.config(command=self.message.yview)
        self.message.pack(expand=1, fill=Tkinter.BOTH)
        self.message.bind("<KeyPress>", lambda e : "break")

        self.frame[2].pack(expand=1, fill=Tkinter.BOTH)


        #第四行控件
        self.clAction = Tkinter.Button(self.frame[3], text='清空日志', command=self.clear)
        self.clAction.pack(side=Tkinter.LEFT)

        Tkinter.Label(self.frame[3], text='Status:').pack(side=Tkinter.LEFT)
        self.lbcount = Tkinter.Label(self.frame[3], text='')
        self.lbcount.pack(side=Tkinter.LEFT)

        self.frame[3].pack(expand=0, fill=Tkinter.X)

        self.gm = globalmaptiles.GlobalMercator()

    def clear(self):
        self.message.delete('1.0', Tkinter.END)

    def LatLon2GoogleTile(self, lat, lon, zoom):
        '''''坐标转换为GoogleMap瓦片编号'''
        mx, my = self.gm.LatLonToMeters(lat, lon)
        tx, ty = self.gm.MetersToTile(mx, my, zoom)
        return self.gm.GoogleTile(tx, ty, zoom)

    def selectSaveFolder(self):
        self.dir = tkFileDialog.askdirectory(initialdir='/')
        self.log('选择存放目录：' + self.dir)

    def doDownload(self):
        #多线程处理长时间方法避免UI无响应
        thread.start_new_thread(self.download, ())

    def download(self):
        ltlat = float(self.leftTopLat.get())
        ltlon = float(self.leftTopLon.get())
        rblat = float(self.rightBottomLat.get())
        rblon = float(self.rightBottomLon.get())
        ls = int(self.mapLevelStart.get())
        ln = int(self.mapLevelEnd.get())

        total = 0
        for i in range(ls, ln + 1):
            #计算这个级别的地图编号
            x, y = self.LatLon2GoogleTile(ltlat, ltlon, i)
            xe, ye = self.LatLon2GoogleTile(rblat, rblon, i)
            s = (xe - x + 1) * (ye - y + 1)
            total += s
            self.log('%s:%d x:%d y:%d ~ x:%d y:%d 瓦片数:%d' % ('下载地图级别', i, x, y, xe, ye, s))
        self.log('%s:%d' % ('下载瓦片数合计', total))

        #return True

        #下载
        froot = self.dir + '/map'# + str(time.time())
        #下载失败路径
        self.log('创建目录:' + froot)
        if os.path.exists(froot)==False:
            os.mkdir(froot);

        #已经下载计数
        count = 0

        #遍历层
        for i in range(ls, ln + 1):
            #创建层目录
            flev = froot + '/' + str(i)
            if os.path.exists(flev)==False:
                os.mkdir(flev)
            self.log('创建层级目录:' + flev)

            x, y = self.LatLon2GoogleTile(ltlat, ltlon, i)
            xe, ye = self.LatLon2GoogleTile(rblat, rblon, i)

            #遍历x
            for j in range(x, xe + 1):
                fx = flev + '/' + str(j)
                if os.path.exists(fx)==False:
                    os.mkdir(fx)
                self.log('创建X方向目录:' + fx)
                for k in range(y, ye + 1):
                    #下载地址
                    #url = DOWNURL % (self.ss.get(), j, k, i)
                    #判断是否存在
                    file_name= fx + '/' + str(k) + '.png'
                    if os.path.exists(file_name):
                        time.sleep(0.001)
                    else:
                        url = DOWNURL % (random.choice('abc'), i,j, k)
                        self.log("url:"+url)
                        download.download.delay(file_name,url)
                    count += 1
                    self.lbcount['text'] = '已完成:%d/%d 瓦片编号 x:%d y:%d z:%d' % (count, total, j, k, i)

        self.log('下载完成！')
        thread.exit_thread()



    def downloadCallback(self, a, b, c):
        '''''a,已下载的数据块  b,数据块的大小  c,远程文件的大小'''
        pass

    def log(self, msg):
        self.message.insert(Tkinter.END, time.strftime('%Y-%m-%d %H:%M:%S\t', time.localtime(time.time())) + msg + '\n')

if __name__ == '__main__':
    root = Tkinter.Tk()
    GUI(root).pack()
    root.title(TITLE)
    root.minsize(WIDTH, HEIGHT)
    #root.maxsize(WIDTH, HEIGHT)
    root.mainloop()
