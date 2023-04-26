# PKUAutoElective2023

北大选课网 **补退选** 阶段自动选课小工具 v6.0.0.2 (2023.02.20)

更新了**验证码识别模型**，使用 CNN+GRU+CTC 的经典网络识别不定长验证码（4~5 个字符），训练过程使用了项目[captcha_trainer](https://github.com/kerlomz/captcha_trainer)

适配 2023 年春季学期北大选课网环境，目前支持 `本科生（含辅双）` 和 `研究生` 选课

本项目在 [zhongxinghong/PKUAutoElective](https://github.com/zhongxinghong/PKUAutoElective)上进行修改，仅将验证码识别模型进行替换，其余使用方法参照原项目

---

## 补充：

该项目的验证码识别模型在 Python3.8.16，TensorFlow-gpu2.12.0 环境下进行训练和测试，使用 40w 张图片进行训练，测试集上能达到 98%的准确率。使用 cpu 识别单张图片耗时 10-30ms，远远低于使用打码平台的耗时。

ps: 验证码训练集并非来自选课网，而是使用 Kaptcha 工具模仿生成（图片样例见[test/data](./test/data)），因此不保证在选课网上能达到较高的准确率，但该模型可以作为预训练模型或用于自举（参考项目：[https://github.com/SpiritedAwayCN/ElectiveCaptCha](https://github.com/SpiritedAwayCN/ElectiveCaptCha))

---

再次鸣谢各位前辈对该项目的贡献！
