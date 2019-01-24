#!/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rublog'

import logging
import requests
import os
import time
import random
from tqdm import tqdm
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler('pdf.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


def main():
    with open('pdf.txt', 'r') as f_pic, open('bad_pdf.log', 'w') as log:
        logger.debug("open files ok")
        lines = f_pic.readlines()
        split1 = ':80/'
        bas_dir = os.path.dirname(os.path.abspath("__file__"))
        logger.debug(bas_dir)
        for line in tqdm(lines):
            line.strip('\n\r')
            if split1 in line:
                str_name = line.split(':80/')[-1]
            else:
                str_name = line.split('0.org/')[-1]
            file_name = '/img1/' + str_name.strip()
            file_name = bas_dir + file_name
            (file_path, temp_file_name) = os.path.split(file_name)
            ua = UserAgent()
            headers = {'user-agent': ua.random,
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
            logger.debug(file_name)
            if os.path.isfile(file_name):
                print("文件存在")
                pass
            else:
                mkdir(file_path)
                s = requests.Session()
                s.headers.update(headers)
                logger.debug(line)
                r = s.get(line, timeout=15)
                print(r.status_code)
                # print(type(r.status_code))
                if int(r.status_code) != 200:
                    log.write(line + '# status_code' + str(r.status_code) + '\n')
                else:
                    # print(r.headers['content-length'])
                    print(r.headers['X-Archive-Orig-content-length'])
                    if int(r.headers['content-length' if ('content-length' in r.headers) else 'X-Archive-Orig-content-length']) < 30:
                        log.write(line + '#请求文件太小' + '\n')
                    else:
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
