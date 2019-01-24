#!/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rublog'

import logging
import requests
import os
import re
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
fh = logging.FileHandler('read_log.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


def main():
    with open('log_html.txt', 'w') as f_html, open('bad_html.log', 'r') as log:
        logger.debug("open files ok")
        lines = log.read()
        bas_dir = os.path.dirname(os.path.abspath("__file__"))
        logger.debug(bas_dir)
        urls = re.findall('http://web.archive.org/web/[\d]+[im_/js*]*.+html', lines)
        for url in urls:
            f_html.write(url + '\n')
        print("        写入完毕")


def mkdir(path):
    if not os.path.isdir(path):
        mkdir(os.path.split(path)[0])
    else:
        return
    os.mkdir(path)


if __name__ == "__main__":
    main()
