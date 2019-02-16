#!/bin/env python
# -*- coding: utf-8 -*-
"""
需要单独安装的库tqdm， fake_useragent, requests
在wechat.txt文件中，每个链接一行（需用保存的页面链接需手动搜集,调试中使用的是sogou朋友圈搜索结果
注意，腾.讯的链接是有实效的），
运行本程序，下载或者保存相关公众号网页到/wechat文件夹下
运行日志保存到down_wechat.log, 未下载的文件保存到bad_wechat.log
要求每一行都是真实地址

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
    with open('wechat.txt', 'r') as f_wechat:
        logger.debug("open files ok")
        lines = f_wechat.readlines()
        for line in tqdm(lines):
            line.strip('\n\r')
            save_html(line)
            # 是html文件或者htm文件就调用相应的方法保存页面


def get_resp(line):
    ua = UserAgent()
    headers = {'user-agent': ua.firefox,
               'Connection': 'keep-alive',
               'Pragma': 'no-cache',
               'Cache-Control': 'no-cache',
               'Upgrade-Insecure-Requests': '1',
               'DNT': '1',
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
               'Accept-Encoding': "gzip, deflate, br",
               'Accept-Language': "zh-CN,zh;q=0.9"
               }
    s = requests.Session()
    s.headers.update(headers)
    logger.debug(line)
    r = s.get(line, timeout=15)
    return r


def save_html(line):
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
            content_temp = re.search('<div\sclass="rich_media_content[\s\S]+?</div>',
                                     content_real)
            if title and content_temp:
                title = title.group()
                title = title.strip('<title>')
                title = title.strip('</title>')
                title = title.strip('\n\r\b')
                k = ['?', '\\', '|', ':', '*', '"', '<', '>']
                for i in k:
                    title1 = title.replace(i, '')
                file_name1 = './wechat/' + title1 + '.html'
                bas_dir = os.path.dirname(os.path.abspath("__file__"))
                file_name = bas_dir + file_name1
                logger.debug(file_name)
                (file_path, temp_file_name) = os.path.split(file_name)
                mkdir(file_path)
                first_line = '<title>' + title + '</title>\n'
                content_need = solve_pic(content_temp.group())
                # print(content_need)
                with open(file_name, 'wb') as f:
                    f.write(first_line.encode('GBK'))
                    f.write(content_need.encode('GBK'))
                    print(file_name + "        写入完毕")
                    time.sleep(random.randint(2, 10))
                    return file_name1
            elif not title and content_temp:
                logger.debug("没有检索到title但是有content")
                file_name1 = str(random.randint(1000000000, 9999999999)) + '.html'
                bas_dir = os.path.dirname(os.path.abspath("__file__"))
                file_name = bas_dir + file_name1
                logger.debug(file_name)
                (file_path, temp_file_name) = os.path.split(file_name)
                mkdir(file_path)
                content_need = solve_pic(content_temp.group())
                with open(file_name, 'wb') as f:
                    f.write(content_need.encode('utf-8'))
                    print(file_name + "        写入完毕")
                    time.sleep(random.randint(2, 10))
                    return file_name1
            else:
                logger.debug("没有检索到content")
                log.write(line + "      没有检索到content\n")


def solve_pic(content_ne):
    all_need_download = re.findall('<img\s.+?>', content_ne)
    for pic in all_need_download:
        url = re.search('(https?:.+?)"', pic)
        if url:
            url = url.group()
            url = url.strip('"')
            file_name = re.search('/mmbiz\S+/\S+/\d', url)
            if file_name:
                # print(file_name.group())
                # print("文件的名字是" + file_name.group().split('/')[-2])
                file_name = './wechat/pic/' + file_name.group().split('/')[-2] + '.' + url.split('=')[-1]
                save_file(file_name, url)
    kk = re.findall('<img\s.+?/mmbiz\S+/(\S+)/\d.+?=([a-z]+)".+?/>',content_ne)
    print(kk)
    content_need = re.sub('<img\s.+?/mmbiz\S+/(\S+)/\d.+?=([a-z]+)".+?/>', '<img src="/wechat/pic/\g<1>.\g<2>"/>', content_ne)
    return content_need


def save_file(file_name, line):
    if os.path.isfile(file_name):
        if os.path.getsize(file_name) > 20:
            print("文件存在")
        else:
            write_file(file_name, line)
    else:
        write_file(file_name, line)


def write_file(file_name, line):
    (file_path, temp_file_name) = os.path.split(file_name)
    logger.debug(file_name)
    mkdir(file_path)
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
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                    print(file_name + "写入完毕")


def mkdir(path):
    if not os.path.isdir(path):
        mkdir(os.path.split(path)[0])
    else:
        return
    os.mkdir(path)


if __name__ == "__main__":
    main()
