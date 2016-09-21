#!/usr/bin/evn python
# -*- coding:utf-8 -*-

#下载服务器mt0~mt3

#绘制地图  #http://mt0.google.cn/vt/lyrs=m@187000000&hl=zh-CN&gl=cn&src=app&x=104&y=52&z=7&s=Galil

#卫星地图
#http://mt0.google.cn/vt/lyrs=s@118&hl=zh-CN&gl=cn&src=app&x=104&y=52&z=7&s=Gali

#下载模板 需要传入4个参数使用
#DOWNURL='http://%s/vt/lyrs=m@187000000&hl=zh-CN&gl=cn&src=app&x=%d&y=%d&z=%d&s=Galil'
DOWNURL='http://%s.tile.thunderforest.com/transport/%d/%d/%d.png'
#DOWNURL='http://otile3.mqcdn.com/tiles/1.0.0/osm/%d/%d/%d.png'
TITLE = 'OpenStreetMap 瓦片下载工具 v1.0'
WIDTH = 900
HEIGHT = 600

#图片大小
#IMGSIZE = 256

#标签文字
mapServers = ['mt0.google.cn', 'mt1.google.cn', 'mt2.google.cn', 'mt3.google.cn']

#地图级别 0~19
