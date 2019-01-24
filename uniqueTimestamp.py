#!/bin/env python
# -*- coding: utf-8 -*-

"""
生成人人网登陆使用的uniqueTimestamp
"""

__author__ = 'rublog'
import time
import random

localtime = time.localtime()
print(localtime)
today = int(time.strftime("%w"))
millisec = random.randint(0, 999)
print(millisec)
uniqueTimestamp = str(localtime[0])+str(localtime[1]-1)+str(today)+str(localtime[3])+str(localtime[4])+str(millisec)
print(uniqueTimestamp)
