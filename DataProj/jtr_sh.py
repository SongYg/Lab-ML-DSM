# coding=utf-8
#!/bin/sh
# import stable_momentum_spark_cfm_jtr

import pandas as pd
import numpy as np
import types
import math
import os
import pickle
import sys
import datetime
import time
from bayes_opt import BayesianOptimization
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from hdfs.client import Client
import subprocess

# 设置聚类数和skill数上下限
n_skills_a = 1
n_skills_b = 50
n_latent_skills_a = 1
n_latent_skills_b = 70


class begin():
    def __init__(self):
        self.in_file_dir = "../source_data/"
        self.file_name = "output_biology_03.csv"
        self.diff_file_name = "attempts_transaction_biology.csv"
        self.out_file_dir = "../result/"
        self.bayes_record = []
        self.bayes_dict = {}

    def bayes_calcul(self, n_latent_skills, n_skills):
        variable_1 = int(round(float(n_latent_skills)))  # 此处用int(round(float))为了避免贝叶斯函数生成的小数
        variable_2 = int(round(float(n_skills)))
        if variable_1 < variable_2:  # 聚类数不能多于skill数
            variable_1 = variable_2

        self.out_file_name = "jtr_test01_biology_" + str(variable_1) + "_kmeans_" + str(variable_2) + ".csv"

        in_file_dir = self.in_file_dir
        file_name = self.file_name
        diff_file_name = self.diff_file_name
        out_file_dir = self.out_file_dir
        out_file_name = self.out_file_name
        bayes_record = self.bayes_record
        bayes_dict = self.bayes_dict

        record = str(variable_1) + "flag" + str(variable_2)  # 记录之前出现过的参数组合，如果贝叶斯再次生成该对参数，直接从字典中获取输出值
        if record in bayes_record:
            return bayes_dict[record]
        else:
            bayes_record.append(record)

        os.environ['variable_1'] = str(variable_1)  # shell的环境变量设置
        os.environ['variable_2'] = str(variable_2)  # environ的键值必须是字符串
        os.environ['in_file_dir'] = str(in_file_dir)
        os.environ['file_name'] = str(file_name)
        os.environ['diff_file_name'] = str(diff_file_name)
        os.environ['out_file_dir'] = str(out_file_dir)
        os.environ['out_file_name'] = str(out_file_name)

        # 提交spark任务
        os.system('python jtr_main.py ${in_file_dir}${file_name} ${in_file_dir}${diff_file_name} $out_file_dir $out_file_name $variable_1 $variable_2')

        os.system('hadoop fs -put ${out_file_dir}${out_file_name} cfm/')
        spark_log = os.popen('spark-submit --master yarn-cluster  --driver-memory 20G --num-executors 50 --executor-memory 8G stable_momentum_spark_cfm_jtr.py ${out_file_name}')

        # 获取本次spark_id
        time.sleep(20)  # 延时防止刚提交spark任务后，尚未开始运行，无法获取spark_id
        spark_app_id = os.popen('yarn application -list')  # 获取运行中的spark_id
        app_id = spark_app_id.read()
        flag = "application_"
        id_num = app_id.find(flag)
        applicationId = app_id[id_num + 12:id_num + 30]
        os.environ['applicationId'] = 'application_' + applicationId
        state_find = str('yarn applicationattempt -status appattempt_' + applicationId + '_000001')
        # print("applicationId:",applicationId)

        # 监控spark是否运行完毕
        temporary_variable = True

        while(temporary_variable == True):
            time.sleep(10)  # 监控间隔时间
            state = os.popen(state_find)
            state_1 = state.read()
            break_button = False
            for line in state_1.splitlines():
                if 'FINISHED' in line:
                    temporary_variable = False
                    #print('spark finished')
                    # 获取spark计算结果
                    result = os.popen('yarn logs -applicationId $applicationId')
                    res = result.read()
                    end_flag = "end_flag:loglike:"
                    calcul_flag = "calcul_flag:loglike:"
                    temporary_variable = True
                    break_button = True
                    output_result = "FINISHED"
                    for line in res.splitlines():
                        if end_flag in line:
                            length = len(end_flag)
                            loglike = line[length:]
                            # print("loglike:",loglike)
                            temporary_variable = False
                            break
                    break
                if 'FAILED' in line:
                    loglike = -99999999.9
                    result = os.popen('yarn logs -applicationId $applicationId')
                    res = result.read()
                    end_flag = "end_flag:loglike:"
                    calcul_flag = "calcul_flag:loglike:"
                    temporary_variable = True
                    break_button = True
                    for line in res.splitlines():
                        if calcul_flag in line:
                            length = len(calcul_flag)
                            loglike_i = line[length:]
                            loglike_i = float(loglike_i)
                            # print("loglike:",loglike)
                            temporary_variable = False
                            loglike = max(loglike, loglike_i)
                    print('resultout:spark failed')
                    output_result = "FAILED"
                    break
                if 'KILLED' in line:
                    loglike = -99999999.9
                    result = os.popen('yarn logs -applicationId $applicationId')
                    res = result.read()
                    end_flag = "end_flag:loglike:"
                    calcul_flag = "calcul_flag:loglike:"
                    temporary_variable = True
                    break_button = True
                    output_result = "KILLED"
                    for line in res.splitlines():
                        if calcul_flag in line:
                            length = len(calcul_flag)
                            loglike_i = line[length:]
                            loglike_i = float(loglike_i)
                            # print("loglike:",loglike)
                            temporary_variable = False
                            loglike = max(loglike, loglike_i)
                    break
                if break_button == True:
                    print('cannot find the result of spark')
                    loglike = -9999999.9
                    output_result = "ERROR"
                    break

        loglike = float(loglike)
        bayes_dict[record] = loglike
        f = open("../source_data/jtr_Bayesian_output_biology.txt", 'a')
        f.write("loglike:" + str(loglike) + "   n_latent_skills:" + str(n_latent_skills) + "   n_skills:" + str(n_skills) + "  " + output_result + "\r\n")
        f.close()
        return loglike


start = begin()
bo = BayesianOptimization(lambda n_latent_skills, n_skills: start.bayes_calcul(n_latent_skills, n_skills), {'n_latent_skills': (n_latent_skills_a, n_latent_skills_b), 'n_skills': (n_skills_a, n_skills_b)})
# bo.explore({'discount': [0.85], 'step_5e': [10]})
bo.maximize(init_points=18, n_iter=8, kappa=2)
print(bo.res['max'])
print(bo.res['all'])
#!/bin/sh

f = open("../source_data/jtr_Bayesian_output_biology.txt", 'a')
f.write("final result" + "\r\n")
f.write(str(bo.res['all']))
f.close()
