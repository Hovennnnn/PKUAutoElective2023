#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
"""此脚本用于训练过程中检验训练效果的脚本，功能为：通过启动参数加载【工程名】中的网络进行预测"""
import os
import random
import sys
import numpy as np
import tensorflow as tf

from autoelective.captcha.model.config import *
from autoelective.captcha.model.constants import RunMode
from autoelective.captcha.model.core import NeuralNetwork
from autoelective.captcha.model.encoder import Encoder


class Predict:
    def __init__(self, project_name):
        self.model_conf = ModelConfig(project_name=project_name)
        self.encoder = Encoder(model_conf=self.model_conf, mode=RunMode.Predict)
        self.sess = None

    def get_image_batch(self, img_bytes):
        if not img_bytes:
            return []
        return [self.encoder.image(index) for index in [img_bytes]]

    @staticmethod
    def decode_maps(categories):
        """解码器"""
        return {index: category for index, category in enumerate(categories, 0)}

    def predict_func(self, image_batch, _sess, dense_decoded, op_input):
        """预测函数"""
        dense_decoded_code = _sess.run(dense_decoded, feed_dict={
            op_input: image_batch,
        })
        # print(dense_decoded_code)
        decoded_expression = []
        for item in dense_decoded_code:
            expression = ''
            # print(item)
            if isinstance(item, int) or isinstance(item, np.int64):
                item = [item]
            for class_index in item:
                if class_index == -1 or class_index == self.model_conf.category_num:
                    expression += ''
                else:
                    expression += self.decode_maps(self.model_conf.category)[class_index]
            decoded_expression.append(expression)
        return ''.join(decoded_expression) if len(decoded_expression) > 1 else decoded_expression[0]


    def startSession(self):
        '''
        因为构建网络图需要一定的时间，肯定不能等到要识别的时候才启动会话。
        应该在程序启动的时候就开启识别会话，请求到图片后立刻识别。
        '''
        graph = tf.Graph()
        self.sess = tf.compat.v1.Session(
            graph=graph,
            config=tf.compat.v1.ConfigProto(
                # allow_soft_placement=True,
                # log_device_placement=True,
                gpu_options=tf.compat.v1.GPUOptions(
                    allocator_type='BFC',
                    # allow_growth=True,  # it will cause fragmentation.
                    per_process_gpu_memory_fraction=0.1
                ))
        )

        with self.sess.graph.as_default():
 
            self.sess.run(tf.compat.v1.global_variables_initializer())
            # tf.keras.backend.set_session(session=sess)

            model = NeuralNetwork(
                self.model_conf,
                RunMode.Predict,
                self.model_conf.neu_cnn,
                self.model_conf.neu_recurrent
            )
            model.build_graph()
            model.build_train_op()

            saver = tf.compat.v1.train.Saver(var_list=tf.compat.v1.global_variables())

            """从项目中加载最后一次训练的网络参数"""
            saver.restore(self.sess, tf.train.latest_checkpoint(self.model_conf.model_root_path))
            # model.build_graph()
            # _ = tf.import_graph_def(graph_def, name="")

        """定义操作符"""
        self.dense_decoded_op = self.sess.graph.get_tensor_by_name("dense_decoded:0")
        self.x_op = self.sess.graph.get_tensor_by_name('input:0')
        """固定网络"""
        self.sess.graph.finalize()

    def closeSession(self):
        self.sess.close()

    def predictOneCaptcha(self, image_bytes):
        """
        以下为根据路径调用预测函数输出结果的demo
        """
        batch = self.get_image_batch(image_bytes)
        if not batch:
            return ""
        st = time.time()
        predict_text = self.predict_func(
            batch,
            self.sess,
            self.dense_decoded_op,
            self.x_op,
        )
        print(f"识别结果：{predict_text}，耗时：{time.time() - st}")
        return predict_text


if __name__ == '__main__':

    predict = Predict(project_name="recognizer_v9-CNN5-GRU-H128-CTC-C1")
    # if(len(sys.argv) > 2):
    #     predict.testing(image_dir=os.path.join("C:/Users/matebook14/Documents/codefield/java_code/figure_generator", sys.argv[2]) , limit=None)
    # else:
    #     predict.testing(image_dir=r"C:\Users\matebook14\Documents\codefield\java_code\figure_generator\figure", limit=None)
    predict.startSession()
    predict.predictOneCaptcha(r"C:\Users\matebook14\Documents\codefield\java_code\figure_generator\figure\2a2m_1675139076.jpg")
    predict.predictOneCaptcha(r"C:\Users\matebook14\Documents\codefield\java_code\figure_generator\figure\2fpg_1675139755.jpg")
    predict.closeSession()
