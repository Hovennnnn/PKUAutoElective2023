#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import tensorflow as tf
from tensorflow.python.keras.regularizers import l1_l2
from autoelective.captcha.model.config import RunMode, ModelConfig
from autoelective.captcha.model.network.utils import NetworkUtils


class FullConnectedRNN(object):
    """
    RNN的输出层
    """

    def __init__(self, model_conf: ModelConfig, outputs):
        self.model_conf = model_conf

        self.dense = tf.compat.v1.keras.layers.Dense(
            units=self.model_conf.category_num + 2,
            kernel_initializer=tf.compat.v1.keras.initializers.he_normal(seed=None),
            bias_initializer='zeros',
        )

        self.outputs = self.dense(outputs)
        self.predict = tf.compat.v1.transpose(self.outputs, perm=(1, 0, 2), name="predict")
        # self.predict = tf.keras.backend.permute_dimensions(self.outputs, pattern=(1, 0, 2))

    def build(self):
        return self.predict
