#!/bin/env python
# -*- coding: utf-8 -*-
"""
需要单独安装的库tqdm， requests
跟踪 https://www.appcgn.com/high-mark-hd-movies 电影更新来下载电影，网页更新很慢，2个月一两部的样子
网页有密码，需要提供密码访问真实页面
根据提供的链接类型，调用aria2或者本机的迅雷下载(建议先设置迅雷静默下载)

"""
__author__ = 'rublog'

import logging
import requests
import os
import re
import json
import base64
from tqdm import tqdm
import sqlite3
from win32com.client import Dispatch


# 添加logging调试方法，记录到down_archive.log和控制台
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler('down_archive.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


def main():
    # url = 'https://www.appcgn.com/high-mark-hd-movies'
    login_url = 'https://www.appcgn.com/wp-login.php?action=postpass'
    login_data = {'post_password': '16300838', 'Submit': '提交'}
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
               'Proxy-Connection': 'keep-alive',
               'Pragma': 'no-cache',
               'Cache-Control': 'no-cache',
               'Upgrade-Insecure-Requests': '1',
               'DNT': '1',
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
               'Accept-Encoding': "gzip, deflate",
               'Accept-Language': "zh-CN,zh;q=0.9",
               'Referer': 'https://www.appcgn.com/high-mark-hd-movies'
               }
    s = requests.Session()
    s.headers.update(headers)
    page = s.post(login_url, login_data)
    # content = s.get(url)
    urls = parse_href(page)
    print(urls)
    # 连接到 SQLite 数据库 数据库文件是 test.db 如果文件不存在，会自动在当前目录创建:
    conn = sqlite3.connect('movie.db')
    # 创建一个 Cursor:
    cursor = conn.cursor()
    thunder = Dispatch('ThunderAgent.Agent64.1')
    for url in tqdm(urls):
        cursor.execute('select * from movie where movie_url=?', [url])
        values = cursor.fetchall()
        print(len(values))
        if len(values):
            continue
        else:
            if url.startswith('magnet') or url.startswith('ftp:'):
                send2aria2(url)
                sql = "insert into movie (movie_url, be_download) values (\'" + url +"\', 1)"
                cursor.execute(sql)
            elif url.startswith('ed2k:') or url.startswith('thunder:'):
                thunder.AddTask(url)
                thunder.CommitTasks()
                sql = "insert into movie (movie_url, be_download) values (\'" + url +"\', 1)"
                cursor.execute(sql)
            elif url.endswith('.txt'):
                resp = requests.get(url)
                txt_content = resp.content.decode('gbk')
                download_url = parse_txt(txt_content)
                for url_a in download_url:
                    urls.append(url_a)
            else:
                pass
    # 关闭 Cursor:
    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭 Connection:
    conn.close()


def parse_href(content):
    r = content
    if int(r.status_code) != 200:
        logger.debug('# status_code' + str(r.status_code) + '\n')
    else:
        if r.headers['Content-Type']:
            char_code_temp = r.headers['Content-Type']
            print(r.headers['Content-Type'])
            char_code = char_code_temp.split('=')[-1]
        else:
            char_code = 'utf-8'
        content_real = r.content.decode(char_code)
        href = re.findall('href="(.+?)"', content_real)
        return href


# 磁力链和ftp直接调用aria2下载
def send2aria2(download_url):
    aria2_server = 'http://192.168.1.99:6800/jsonrpc'
    json_rpc = json.dumps({
        'id': '0',
        'jsonrpc': '2.0',
        'method': 'aria2.addUri',
        'params': [[download_url],{}]
    }).encode()
    response = requests.post(aria2_server, data=json_rpc, verify=False)
    print(response)


def parse_txt(txt):
    string_list = txt.split('\n')
    need_list = []
    for line in string_list:
        if line.startswith('ed2k:') or line.startswith('thunder:') or line.startswith('http:'):
            need_list.append(line)
    return need_list


def mkdir(path):
    if not os.path.isdir(path):
        mkdir(os.path.split(path)[0])
    else:
        return
    os.mkdir(path)


if __name__ == "__main__":
    main()
