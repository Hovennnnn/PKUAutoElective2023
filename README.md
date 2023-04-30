# PKUAutoElective2023

北大选课网 **补退选** 阶段自动选课小工具（2023）

适配 2023 年春季学期北大选课网环境，目前支持 `本科生（含辅双）` 和 `研究生` 选课

本项目在 [zhongxinghong/PKUAutoElective](https://github.com/zhongxinghong/PKUAutoElective)上进行修改，仅将验证码识别模型进行替换，不需要安装Pytorch，安装TensorFlow即可。其余使用方法参照原项目

---

## 补充：


更新了**验证码识别模型**，使用 CNN+GRU+CTC 的经典网络识别不定长验证码（4~5 个字符），训练过程使用了项目[captcha_trainer](https://github.com/kerlomz/captcha_trainer)

- 该项目的验证码识别模型在 Python3.8.16，TensorFlow-gpu2.12.0 环境下进行训练和测试，使用 60w 张图片进行训练，并采用数据增广的方式提高泛化能力，在测试集上能达到 98%的准确率。
- 使用 cpu 识别单张图片耗时 10-30ms，远远低于使用打码平台的耗时。

ps: 验证码训练集并非来自选课网，而是使用 Kaptcha 工具模仿生成（图片样例见[test/data](./test/data)）。由于训练过程中使用了数据增广的方式，模型具有较好的泛化能力。同时，该模型可以作为预训练模型或用于自举（参考项目：[https://github.com/SpiritedAwayCN/ElectiveCaptCha](https://github.com/SpiritedAwayCN/ElectiveCaptCha))，以进一步进行训练。

再次鸣谢各位前辈对该项目的贡献！
---
