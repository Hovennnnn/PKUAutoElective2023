#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: test_cnn.py
# Created Date: 2021-03-10
# Edited Date: 2023-04-26
# Author: Rabbit
# --------------------------------
# Copyright (c) 2021 Rabbit

import sys
import re
sys.path.append("../")

import os
from autoelective.captcha import CaptchaRecognizer
from autoelective.const import CNN_MODEL_FILE

def test_captcha(r, code=None):
    # 遍历data目录下的所有验证码图片
    if(code is None):
        for root, dirs, files in os.walk('./data'):
            for file in files:
                if file.endswith(".jpg"):
                    code = file.split("_")[0]
                    filepath = os.path.join(root, file)
                    with open(filepath, 'rb') as fp:
                        im_data = fp.read()

                    c = r.recognize(im_data)
                    print(c, c.code == code)
    else:
        for root, dirs, files in os.walk('./data'):
            for file in files:
                if file.endswith(".jpg") and file.startswith(code):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'rb') as fp:
                        im_data = fp.read()

                    c = r.recognize(im_data)
                    print(c, c.code == code)
                    break

def main():
    r = CaptchaRecognizer(CNN_MODEL_FILE)
    test_captcha(r)

if __name__ == "__main__":
    main()
