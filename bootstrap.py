import os
import re
import time
import random
from io import BytesIO
import numpy as np
from PIL import Image
import cv2
from requests import Session
from autoelective.captcha.model.predict import Predict

re_sida_sttp = re.compile(r'\?sida=(\S+?)&sttp=(?:bzx|bfx)')
id = "" #学号
password= "" #密码

def elective_login(s):
    s.cookies.clear()

    ## elective homepage

    r = s.get(
        url="https://elective.pku.edu.cn/"
    )
    r.raise_for_status()

    ## iaaa oauthlogin

    time.sleep(0.5)

    r = s.post(
        url="https://iaaa.pku.edu.cn/iaaa/oauthlogin.do",
        data={
            "appid": "syllabus",
            "userName": id,
            "password": password,
            "randCode": "",
            "smsCode": "",
            "otpCode": "",
            "redirUrl": "http://elective.pku.edu.cn:80/elective2008/ssoLogin.do",
        }
    )
    r.raise_for_status()

    token = r.json()["token"]

    ## elective ssologin

    r = s.get(
        url="https://elective.pku.edu.cn/elective2008/ssoLogin.do",
        params={
            "_rand": str(random.random()),
            "token": token,
        }
    )
    r.raise_for_status()

    sida = re_sida_sttp.search(r.text).group(1)

    ## elective ssologin (dual degree)

    time.sleep(0.5)

    r = s.get(
        url="https://elective.pku.edu.cn/elective2008/ssoLogin.do",
        params={
            "sida": sida,
            "sttp": "bzx",
        }
    )
    r.raise_for_status()

    ## elective HelpController

    r = s.get(
        url="https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/help/HelpController.jpf"
    )
    r.raise_for_status()

    ## elective SupplyCancel

    time.sleep(0.5)

    r = s.get(
        url="https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/supplement/SupplyCancel.do",
        headers={
            "Referer": "https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/help/HelpController.jpf"
        }
    )
    r.raise_for_status()


def predict_captcha(im_data, model):
    code = model.predictOneCaptcha(im_data)
    return code


def main():
    model = Predict(project_name="recognizer_v11-CNN5-GRU-H128-CTC-C1")
    model.startSession()

    right_cnt = 0
    wrong_cnt = 0
    error_cnt = 0

    s = Session()
    s.headers.update({
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "Upgrade-Insecure-Requests": "1"
    })

    elective_login(s)

    i = 0

    while i < 200:
        i += 1

        ## elective DrawServlet

        r = s.get(
            url="https://elective.pku.edu.cn/elective2008/DrawServlet",
            params={
                "Rand": str(random.random() * 10000),
            },
            headers={
                "Referer": "https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/supplement/SupplyCancel.do"
            }
        )
        r.raise_for_status()

        im_data = r.content

        if not im_data.startswith(b'\xff\xd8\xff'):
            error_cnt += 1
            print("Bad Captcha")
            time.sleep(0.5)
            elective_login(s)
            continue

        code = predict_captcha(im_data, model)

        r = s.post(
            url="https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/supplement/validate.do",
            data={
                "xh": id,
                "validCode": code,
            },
            headers={
                "Referer": "https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/supplement/SupplyCancel.do"
            }
        )
        r.raise_for_status()

        try:
            rjson = r.json()
        except Exception as e:
            if "异常刷新" in r.text or "请重新登录" in r.text:
                error_cnt += 1
                time.sleep(0.5)
                elective_login(s)
                continue
            else:
                print(r.text)
            raise e

        if rjson.get('valid') != '2':
            wrong_cnt += 1
            valid_res = 'wrong'
        else:
            right_cnt += 1
            valid_res = 'right'

        print("%s %s, %d / %d, accuracy: %.4f, error count: %d" % (
            code,
            valid_res,
            right_cnt,
            right_cnt + wrong_cnt,
            right_cnt / (right_cnt + wrong_cnt),
            error_cnt
        ))

        serial = '%d-%d' % (time.time() * 1000, random.random() * 1000)
        filename = '%s_%s_%s.jpg' % (code, valid_res, serial)
        if valid_res == 'right':
            filepath = os.path.join("./figure/true", filename)
        else:
            filepath = os.path.join("./figure/false", filename)

        with open(filepath, 'wb') as fp:
            fp.write(im_data)

        time.sleep(2.0 + 2.0 * random.random())
    model.closeSession()


if __name__ == "__main__":
    if not os.path.exists("./figure"):
        os.mkdir("./figure")
    if not os.path.exists("./figure/true"):
        os.mkdir("./figure/true")
    if not os.path.exists("./figure/false"):
        os.mkdir("./figure/false")

    main()