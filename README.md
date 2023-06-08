# PKUAutoElective2023

北大选课网 **补退选** 阶段自动选课小工具 (2023.05.18)

- 更新了**验证码识别模型**，使用 CNN+GRU+CTC 的经典网络识别不定长验证码（4~5 个字符），训练过程使用了项目[captcha_trainer](https://github.com/kerlomz/captcha_trainer)

- 适配 2023 年春季学期北大选课网环境，目前支持 `本科生（含辅双）` 和 `研究生` 选课

本项目在 [zhongxinghong/PKUAutoElective](https://github.com/zhongxinghong/PKUAutoElective)上进行修改，仅将验证码识别模型进行替换，使用该工具需要安装 TensorFlow，而不必安装 Pytorch。其余使用方法参照原项目

---

如果不想用TensorFlow和Pytorch，还有一个使用ddddocr库的fork：[https://github.com/Hovennnnn/PKUAutoElective](https://github.com/Hovennnnn/PKUAutoElective) (使用dddd_trainer训练的模型，不是ddddocr的通用模型)

---

## 模型性能：

- 该项目的验证码识别模型在 Python3.8.16，TensorFlow-gpu2.12.0 环境下进行训练和测试
- 使用 60w 张图片进行训练，测试集上能达到 98%的准确率。
- 使用 cpu 识别单张图片平均耗时 10-30ms，准确率和耗时均优于打码平台。

ps: 验证码训练集使用 Kaptcha 工具模仿生成（图片样例见[test/data](./test/data)），在选课网上能达到较高的准确率（96%以上），该模型也可以作为预训练模型或用于自举（[bootstrap.py](./bootstrap.py)，参考项目：[https://github.com/zhongxinghong/PKUElectiveCaptcha2021Spring](https://github.com/zhongxinghong/PKUElectiveCaptcha2021Spring/blob/master/bootstrap.py))

---

## 注意事项

特地将一些重要的说明提前写在这里，希望能得到足够的重视

1. 不要使用过低的刷新间隔，以免对选课网服务器造成压力，建议时间间隔不小于 4 秒
2. 选课网存在 IP 级别的限流，访问过于频繁可能会导致 IP 被封禁

---

## 项目安装

（以下是对 zhongxinghong 大佬项目[https://github.com/zhongxinghong/PKUAutoElective](https://github.com/zhongxinghong/PKUAutoElective)使用说明的修改，主要是说明**安装过程**，更多细节请参照原项目）

### Python 3

该项目至少需要 Python 3，可以从 [Python 官网](https://www.python.org/) 下载并安装（项目开发环境为 Python 3.8.16）

例如在 Linux 下运行：

```console
$ apt-get install python3
```

### Repo

下载这个 repo 至本地。点击右上角的 `Code -> Download ZIP` 即可下载

（或）对于 git 命令行：

```console
$ git clone https://github.com/Hovennnnn/PKUAutoElective2023.git
```

### Packages

安装依赖包（该示例中使用清华镜像源以加快下载速度）

```console
$ pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

TensorFlow 安装时间可能比较长，需耐心等待

### 验证码识别模块测试

这个测试旨在检查与验证码识别模块相关的依赖包是否正确安装，尤其是 TensorFlow, OpenCV

```console
$ cd test/
$ python3 test_captcha_recognizer.py

识别结果：2a2m，耗时：0.12247776985168457
Captcha('2a2m') True
识别结果：2a3cx，耗时：0.013575553894042969
Captcha('2a3cx') True
识别结果：2a5c，耗时：0.016000032424926758
Captcha('2a5c') True
识别结果：2anwx，耗时：0.017246723175048828
Captcha('2anwx') True
识别结果：2ega，耗时：0.01694774627685547
Captcha('2ega') True
识别结果：cecc，耗时：0.016101598739624023
Captcha('cecc') True
识别结果：dnwp6，耗时：0.014996767044067383
Captcha('dnwp6') True
识别结果：dnynw，耗时：0.015755653381347656
Captcha('dnynw') True
识别结果：dp4y，耗时：0.015390634536743164
Captcha('dp4y') True
识别结果：mgmn，耗时：0.016569137573242188
Captcha('mgmn') True
识别结果：mgnd，耗时：0.015115499496459961
Captcha('mgnd') True
识别结果：n4efg，耗时：0.013999700546264648
Captcha('n4efg') True
识别结果：n5edf，耗时：0.01500082015991211
Captcha('n5edf') True
识别结果：n6ad，耗时：0.017334461212158203
Captcha('n6ad') True
识别结果：nnman，耗时：0.014373779296875
Captcha('nnman') True
识别结果：penn，耗时：0.014000177383422852
Captcha('penn') True
识别结果：pf32，耗时：0.01499795913696289
Captcha('pf32') True
识别结果：wd54，耗时：0.014998674392700195
Captcha('wd54') True
识别结果：wd55m，耗时：0.01399850845336914
Captcha('wd55m') True
识别结果：wda3，耗时：0.015000343322753906
Captcha('wda3') True
```

## 责任须知

- 你可以修改和使用这个项目，但请自行承担由此造成的一切后果
- 严禁在公共场合扩散这个项目，以免给你我都造成不必要的麻烦

---

再次鸣谢各位前辈对该项目的贡献！
