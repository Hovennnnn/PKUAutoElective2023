#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import io
import random
import re
from collections import Counter

import cv2
import numpy as np
import PIL.Image
import tensorflow as tf
from autoelective.captcha.model.category import FULL_ANGLE_MAP, encode_maps
from autoelective.captcha.model.config import LabelFrom, LossFunction, ModelConfig
from autoelective.captcha.model.constants import RunMode
from autoelective.captcha.model.exception import *
from autoelective.captcha.model.pretreatment import preprocessing, preprocessing_by_func
from autoelective.captcha.model.tools.gif_frames import blend_frame, concat_frames


class Encoder(object):
    """
    编码层：用于将数据输入编码为可输入网络的数据
    """

    def __init__(self, model_conf: ModelConfig, mode: RunMode):
        self.model_conf = model_conf
        self.mode = mode
        self.category_param = self.model_conf.category_param

    @staticmethod
    def main_color_replace(im: np.ndarray, num=2, repl=(255, 255, 255)):

        red, green, blue = im.T

        colors = []
        for (r, g, b) in im[:, 1, :]:
            colors.append((r, g, b))

        most_common = [i[0] for i in Counter(colors).most_common(num)]

        areas = False

        for r, g, b in most_common:
            areas = areas | ((red == r) & (green == g) & (blue == b))

        im[:, :, :][areas.T] = repl
        return im

    def image(self, path_or_bytes):
        """针对图片类型的输入的编码"""
        # im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        # The OpenCV cannot handle gif format images, it will return None.
        # if im is None:

        path_or_stream = io.BytesIO(path_or_bytes) if isinstance(path_or_bytes, bytes) else path_or_bytes
        if not path_or_stream:
            return "Picture is corrupted: {}".format(path_or_bytes)
        try:
            pil_image = PIL.Image.open(path_or_stream)
        except OSError as e:
            return "{} - {}".format(e, path_or_bytes)

        use_compress = False

        gif_handle = self.model_conf.pre_concat_frames != -1 or self.model_conf.pre_blend_frames != -1

        if pil_image.mode == 'P' and not gif_handle:
            pil_image = pil_image.convert('RGB')

        rgb = pil_image.split()

        # if self.mode == RunMode.Trains and use_compress:
        #     img_compress = io.BytesIO()
        #
        #     pil_image.convert('RGB').save(img_compress, format='JPEG', quality=random.randint(75, 100))
        #     img_compress_bytes = img_compress.getvalue()
        #     img_compress.close()
        #     path_or_stream = io.BytesIO(img_compress_bytes)
        #     pil_image = PIL.Image.open(path_or_stream)

        if len(rgb) == 1 and self.model_conf.image_channel == 3:
            return "The number of image channels {} is inconsistent with the number of configured channels {}.".format(len(rgb), self.model_conf.image_channel)

        size = pil_image.size

        # if self.mode == RunMode.Trains and len(rgb) == 3 and use_compress:
        #     new_size = [size[0] + random.randint(5, 10), size[1] + random.randint(5, 10)]
        #     background = PIL.Image.new(
        #         'RGB', new_size, (255, 255, 255)
        #     )
        #     random_offset_w = random.randint(0, 5)
        #     random_offset_h = random.randint(0, 5)
        #     background.paste(
        #         pil_image,
        #         (
        #             random_offset_w,
        #             random_offset_h,
        #             size[0] + random_offset_w,
        #             size[1] + random_offset_h
        #         ),
        #         None
        #     )
        #     background.convert('RGB')
        #     pil_image = background

        if len(rgb) > 3 and self.model_conf.pre_replace_transparent and not gif_handle and not use_compress:
            background = PIL.Image.new('RGBA', pil_image.size, (255, 255, 255))
            try:
                background.paste(pil_image, (0, 0, size[0], size[1]), pil_image)
                background.convert('RGB')
                pil_image = background
            except:
                pil_image = pil_image.convert('RGB')

        if len(pil_image.split()) > 3 and self.model_conf.image_channel == 3:
            pil_image = pil_image.convert('RGB')

        if self.model_conf.pre_concat_frames != -1:
            im = concat_frames(pil_image, need_frame=self.model_conf.pre_concat_frames)
        elif self.model_conf.pre_blend_frames != -1:
            im = blend_frame(pil_image, need_frame=self.model_conf.pre_blend_frames)
        else:
            im = np.array(pil_image)

        if isinstance(im, list):
            return None

        im = preprocessing_by_func(exec_map=self.model_conf.pre_exec_map, src_arr=im)

        if self.model_conf.image_channel == 1 and len(im.shape) == 3:
            if self.mode == RunMode.Trains:
                im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY if bool(random.getrandbits(1)) else cv2.COLOR_BGR2GRAY)
            else:
                im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)

        im = preprocessing(
            image=im,
            binaryzation=self.model_conf.pre_binaryzation,
        )

        if self.model_conf.pre_horizontal_stitching:
            up_slice = im[0:int(size[1] / 2), 0:size[0]]
            down_slice = im[int(size[1] / 2):size[1], 0:size[0]]
            im = np.concatenate((up_slice, down_slice), axis=1)

        if self.mode == RunMode.Trains and bool(random.getrandbits(1)):
            im = preprocessing(
                image=im,
                binaryzation=self.model_conf.da_binaryzation,
                median_blur=self.model_conf.da_median_blur,
                gaussian_blur=self.model_conf.da_gaussian_blur,
                equalize_hist=self.model_conf.da_equalize_hist,
                laplacian=self.model_conf.da_laplace,
                rotate=self.model_conf.da_rotate,
                warp_perspective=self.model_conf.da_warp_perspective,
                sp_noise=self.model_conf.da_sp_noise,
                random_brightness=self.model_conf.da_brightness,
                random_saturation=self.model_conf.da_saturation,
                random_hue=self.model_conf.da_hue,
                random_gamma=self.model_conf.da_gamma,
                random_channel_swap=self.model_conf.da_channel_swap,
                random_blank=self.model_conf.da_random_blank,
                random_transition=self.model_conf.da_random_transition,
            ).astype(np.float32)

        else:
            im = im.astype(np.float32)
        if self.model_conf.resize[0] == -1:
            # random_ratio = random.choice([2.5, 3, 3.5, 3.2, 2.7, 2.75])
            ratio = self.model_conf.resize[1] / size[1]
            # random_width = int(random_ratio * RESIZE[1])
            resize_width = int(ratio * size[0])
            # resize_width = random_width if is_random else resize_width
            im = cv2.resize(im, (resize_width, self.model_conf.resize[1]))
        else:
            im = cv2.resize(im, (self.model_conf.resize[0], self.model_conf.resize[1]))
        im = im.swapaxes(0, 1)

        if self.model_conf.image_channel == 1:
            return np.array((im[:, :, np.newaxis]) / 255.)
        else:
            return np.array(im[:, :]) / 255.

    def text(self, content):
        """针对文本类型的输入的编码"""
        if isinstance(content, bytes):
            content = content.decode("utf8")

        found = content
        # 如果匹配内置的大小写规范，触发自动转换
        if isinstance(self.category_param, str) and '_LOWER' in self.category_param:
            found = found.lower()
        if isinstance(self.category_param, str) and '_UPPER' in self.category_param:
            found = found.upper()

        if self.model_conf.category_param == 'ARITHMETIC':
            found = found.replace("x", "×").replace('？', "?")

        # 标签是否包含分隔符
        if self.model_conf.label_split:
            labels = found.split(self.model_conf.label_split)
        elif '&' in found:
            labels = found.split('&')
        elif self.model_conf.max_label_num == 1:
            labels = [found]
        else:
            labels = [_ for _ in found]
        labels = self.filter_full_angle(labels)
        try:
            if not labels:
                return [0]
            # 根据类别集合找到对应映射编码为dense数组
            if self.model_conf.loss_func == LossFunction.CTC:
                label = self.split_continuous_char([encode_maps(self.model_conf.category)[i] for i in labels])
            else:
                label = self.auto_padding_char([encode_maps(self.model_conf.category)[i] for i in labels])
            return label

        except KeyError as e:
            return dict(e=e, label=content, char=e.args[0])
            # exception(
            #     'The sample label {} contains invalid charset: {}.'.format(
            #         content, e.args[0]
            #     ), ConfigException.SAMPLE_LABEL_ERROR
            # )

    def split_continuous_char(self, content):
        # 为连续的分类插入空白符
        store_list = []
        # blank_char = [self.model_conf.category_num] if bool(random.getrandbits(1)) else [0]
        blank_char = [self.model_conf.category_num]
        for i in range(len(content) - 1):
            store_list.append(content[i])
            if content[i] == content[i + 1]:
                store_list += blank_char
        store_list.append(content[-1])
        return store_list

    def auto_padding_char(self, content):
        if len(content) < self.model_conf.max_label_num and self.model_conf.auto_padding:
            remain_label_num = self.model_conf.max_label_num - len(content)
            return [0] * remain_label_num + content
            # return content + [0] * remain_label_num
        return content

    @staticmethod
    def filter_full_angle(content):
        return [FULL_ANGLE_MAP.get(i) if i in FULL_ANGLE_MAP.keys() else i for i in content if i != ' ']


if __name__ == '__main__':
    pass
