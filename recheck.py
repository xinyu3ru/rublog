#!/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rublog'

import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler('down_ach.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

def main():
    with open('achive.txt', 'r') as f1, open('html.txt', 'r') as fhtml, open('new.txt', 'w') as fnew:
        logger.debug("open files ok")
        archive_lines = f1.read()
        html_lines = fhtml.readlines()
        for line in html_lines:
            print(line)
            line = line.strip('[],\n')
            re_line = '"' + line + '.+]'
            line_temp = re.search(re_line, archive_lines).group()
            line_temp = line_temp.strip(']')
            line_dict = list(eval(line_temp))
            #print(line_dict)
            logger.debug("%s" % line_dict)
            if int(line_dict[2]) < int(line_dict[3]):
                pic_line = "http://web.archive.org/web/" + line_dict[2] + line_dict[0] + "\n"
                fnew.writelines(pic_line)
            else:
                pic_line = "http://web.archive.org/web/" + line_dict[3] + line_dict[0] + "\n"
                fnew.writelines(pic_line)


if __name__ == "__main__":
    main()
