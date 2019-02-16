#!/bin/env python
# -*- coding: utf-8 -*-
"""
需要单独安装的库tqdm， requests
跟踪 https://www.appcgn.com/high-mark-hd-movies 电影更新来下载电影，网页更新很慢，2个月一两部的样子
网页有密码，需要提供密码访问真实页面
根据提供的链接类型，调用aria2或者本机的迅雷下载

"""
__author__ = 'rublog'

import logging
import requests
import os
import re
import json
import base64
from tqdm import tqdm

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
    for url in tqdm(urls):
        if url.startswith('magnet') or url.startswith('ftp:'):
            send2aria2(url)
        elif url.startswith('ed2k:'):
            shell2thunder(url)
        elif url.startswith('thunder:'):
            cmd2thunder(url)
        elif url.enndwith('.txt'):
            resp = requests.get(url)
            txt_content = resp.content.decode('gbk')
            download_url = parse_txt(txt_content)
            for url_a in download_url:
                urls.append(url_a)
        else:
            pass


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
        herf = re.findall('href="(.+?)"', content_real)
        return herf


# 磁力链和ftp直接调用aria2下载
def send2aria2(download_url):
    aria2_server = 'http://127.0.0.1:6800/jsonrpc'
    json_rpc = json.dumps({
        'id': '',
        'jsonrpc': '2.0',
        'method': 'aria2.addUri',
        'params': download_url
    })
    response = requests.post(aria2_server, data=json_rpc)
    print(response)


# 转换格式后下载
def shell2thunder(url):
    thunder_url = get_thunder_url(url)
    os.system("Thunder.exe -StartType:DesktopIcon \"%s\"" % thunder_url)


# 迅雷专有格式直接调用下载
def cmd2thunder(url):
    os.system("Thunder.exe -StartType:DesktopIcon \"%s\"" % url)


# 转换ed2k 为thunder://
def get_thunder_url(url):
    return ("thunder://".encode("utf-8")+base64.b64encode(('AA'+url+'ZZ').encode("utf-8"))).decode("utf-8")


def parse_txt(txt):
    string_list = txt.split('\n')
    need_list = []
    for line in string_list:
        if line.startswith('ed2k:') or line.startswith('thunder:') or line.startswith('http:'):
            need_list.append(line)
    return need_list


def save2sql(url):
    pass


def mkdir(path):
    if not os.path.isdir(path):
        mkdir(os.path.split(path)[0])
    else:
        return
    os.mkdir(path)


if __name__ == "__main__":
    main()
