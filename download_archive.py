#!/bin/env python
# -*- coding: utf-8 -*-
"""
需要单独安装的库tqdm， fake_useragent, requests
在html.txt文件中，每个链接一行，运行本程序，下载或者保存相关archive.org网页到/html文件夹下
运行日志保存到down_archive.log, 未下载的文件保存到bad_html.log
https://web.archive.org/web/20060512133352if_/http://www.para2000.org:80/base/overlib.js  要求每一行都是真实地址，
特别是js文件，jpg文件

"""
__author__ = 'rublog'

import logging
import requests
import os
import re
import time
import random
from tqdm import tqdm
from fake_useragent import UserAgent

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
    with open('html.txt', 'r') as f_html:
        logger.debug("open files ok")
        lines = f_html.readlines()
        split1 = ':80/'
        bas_dir = os.path.dirname(os.path.abspath("__file__"))
        logger.debug(bas_dir)
        for line in tqdm(lines):
            line.strip('\n\r')
            if len(line) > 10:
                if split1 in line:
                    str_name = line.split(':80/')[-1]
                else:
                    str_name = line.split('0.org/')[-1]
                file_name = '/html/' + str_name.strip()
                file_name = bas_dir + file_name
                if file_name[-1:] in ['l', 'm']:
                    if os.path.isfile(file_name):
                        if os.path.getsize(file_name) > 20:
                            print("文件存在")
                        else:
                            save_html(file_name, line)
                    else:
                        save_html(file_name, line)
                    # 是html文件或者htm文件就调用相应的方法保存页面
                else:
                    if os.path.isfile(file_name):
                        if os.path.getsize(file_name) > 20:
                            print("文件存在")
                        else:
                            save_file(file_name, line)
                    else:
                        save_file(file_name, line)


def get_resp(line):
    ua = UserAgent()
    headers = {'user-agent': ua.firefox,
               'Host': 'web.archive.org',
               'Proxy-Connection': 'keep-alive',
               'Pragma': 'no-cache',
               'Cache-Control': 'no-cache',
               'Upgrade-Insecure-Requests': '1',
               'DNT': '1',
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
               'Accept-Encoding': "gzip, deflate",
               'Accept-Language': "zh-CN,zh;q=0.9"
               }
    s = requests.Session()
    s.headers.update(headers)
    logger.debug(line)
    r = s.get(line, timeout=15)
    return r


def save_html(file_name, line):
    (file_path, temp_file_name) = os.path.split(file_name)
    logger.debug(file_name)
    r = get_resp(line)
    print(r.status_code)
    # print(r.content.decode())
    with open('bad_html.log', 'w') as log:
        if int(r.status_code) != 200:
            log.write(line + '# status_code' + str(r.status_code) + '\n')
        else:
            if r.headers['Content-Type']:
                char_code_temp = r.headers['Content-Type']
                print(r.headers['Content-Type'])
                char_code = char_code_temp.split('=')[-1]
            else:
                char_code = 'utf-8'
            content_real = r.content.decode(char_code)
            title = re.search('<title>[\S\s]+</title>', content_real)
            if title:
                title = title.group()
                title = title.strip('<title>')
                title = title.strip('</title>')
                title = title.strip('\n\r\b')
                first_line = '<title>' + title + '</title>\n'
            else:
                logger.debug("没有检索到title")
                log.write(line + "      achive    没有检索到title\n")
            logger.debug(file_name)
            mkdir(file_path)
            content_temp = re.search('<!--\sEND\sWAYBACK\sTOOLBAR[\s\S]+?</body>',
                                     content_real)
            if content_temp:
                content_n = re.sub('http://web.archive.org/web/[\d]+[im_/js*]*', '', content_temp.group())
                # print(content_n)
                content_need = re.sub("/web/[\d]+[im_/js*]*", "", content_n)
                # print(content_need)
                mkdir(file_path)
                with open(file_name, 'wb') as f:
                    try:
                        f.write(first_line.encode())
                    except:
                        logger.debug("本文件发现没有title")
                    finally:
                        f.write(content_need.encode())
                        print(file_name + "        写入完毕")
                        time.sleep(random.randint(2, 10))
            elif not title:
                logger.debug("没有检索到content")
                log.write(line + "      achive    没有检索到content和title\n")
            else:
                logger.debug("没有检索到content")
                log.write(line + "      achive    没有检索到content\n")


def save_file(file_name, line):
    (file_path, temp_file_name) = os.path.split(file_name)
    logger.debug(file_name)
    r = get_resp(line)
    print(r.status_code)
    # print(r.content.decode())
    with open('bad_html.log', 'w') as log:
        if int(r.status_code) != 200:
            log.write(line + '# status_code' + str(r.status_code) + '\n')
        else:
            if (int(r.headers['content-length' if (
                    'content-length' in r.headers) else 'X-Archive-Orig-content-length']) < 30):
                log.write(line + '#请求文件太小' + '\n')
            else:
                mkdir(file_path)
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                    print(file_name + "写入完毕")
                    time.sleep(random.randint(2, 10))


def mkdir(path):
    if not os.path.isdir(path):
        mkdir(os.path.split(path)[0])
    else:
        return
    os.mkdir(path)


if __name__ == "__main__":
    main()
