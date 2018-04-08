#-*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import types
import math
import pickle
import sys
import random
import datetime
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from hdfs.client import Client
import os
import importlib

appName = "testsp"  # 你的应用程序名称
master = "yarn-cluster"  # 设置单机
conf = SparkConf().setAppName(appName).setMaster(master)  # 配置SparkContext
sc = SparkContext(conf=conf)
importlib.reload(sys)


def map1(x, results, attempts, students):
    a = x.pop('flag')
    return (a, [x, results[a], attempts[a], students[a]])


def computezk(x):
    pi = 1.0
    pq = 0.0
    skill_name = x[0]
    skill_value = x[1]
    results = x[2]
    attempts = x[3]
    students = x[4]
    student_able = x[5]
    skill_able = x[6]
    skill_rate = x[7]
    base_result = {}
    if skill_value == 1:
        zk = student_able + skill_able + skill_rate * attempts
        pi = 1 / (1 + pow(math.e, -zk))
        pq = 1 / (1 + pow(math.e, zk))
        base_result[skill_name] = pq
        # 计算student_able 梯度,计算skill_able和rate的梯度

    return (results, students, pi, pq, base_result, attempts)


def computeline(x, y):
    results = x[0]
    students = x[1]
    pi = x[2] * y[2]
    pq = x[3] + y[3]
    base_result = dict(list(x[4].items()) + list(y[4].items()))
    attempts = x[5]
    return (results, students, pi, pq, base_result, attempts)


def computedown(x):
    yi = x[0]
    students = x[1]
    pi = x[2]
    pq = x[3]
    base_result = x[4]
    attempts = x[5]
    down_skill_rate = {}
    down_skill_able = {}
    down_student_able = {}
    down_student_able[students] = (pi - yi) * pq / (pi - 1)
    for i in list(base_result.keys()):
        down_skill_able[i] = (pi - yi) * base_result[i] / (pi - 1)
        down_skill_rate[i] = attempts * (pi - yi) * base_result[i] / (pi - 1)
    loglike = (yi * math.log(pi) + (1 - yi) * (math.log(1 - pi)))
    return (loglike, down_student_able, down_skill_able, down_skill_rate)


def computeloglike(x, y):
    loglike = x + y
    return loglike


class CFM():
    def __init__(self, file_path):
        hdfs_address = 'cfm/'
        client = Client("http://10.2.14.88:50070")
        with client.read(hdfs_address + file_path, encoding='utf-8') as reader:
            df = pd.read_csv(reader)
        self.filename = file_path
        self.rows = (df.count())[0]
        self.columns = len(df.columns)
        self.step = 0.00002
        self.discount = 0.0
        self.diff = float("inf")
        self.loglike = 0
        self.parameternum = 0
        print('rows:' + str(self.rows))
        print('columns:' + str(self.columns))
        results = df['result']
        attempts = df['trynum']
        students = df['student']
        self.student_set = set(students)
        self.parameternum += len(self.student_set)
        self.student_able = {}
        self.skill_able = {}
        self.skill_rate = {}
        self.pre_student_able = {}
        self.pre_skill_able = {}
        self.pre_skill_rate = {}
        for i in self.student_set:
            self.student_able[i] = 0.1
            self.pre_student_able[i] = 0.0
        self.skill_interception = pd.get_dummies(df.ix[:, 4:self.columns])
        self.skill_interception['flag'] = self.skill_interception.index
        sqlContext = SQLContext(sc)
        sparkdf = sqlContext.createDataFrame(self.skill_interception)
        dfrdd = sparkdf.rdd
        normalrdd = dfrdd.map(lambda x: x.asDict())
        self.normalrdd = normalrdd.map(lambda x: map1(x, results, attempts, students))
        self.skill_set = set(self.skill_interception.columns)
        self.parameternum += 2 * len(self.skill_set)
        for i in self.skill_set:
            self.skill_able[i] = 0.1
            self.skill_rate[i] = 0.1
            self.pre_skill_able[i] = 0.0
            self.pre_skill_rate[i] = 0.0

    def parallel(self):
        skill_able = self.skill_able
        skill_rate = self.skill_rate
        student_able = self.student_able
        pre_skill_able = self.pre_skill_able
        pre_skill_rate = self.pre_skill_rate
        pre_student_able = self.pre_student_able
        step = self.step
        discount = self.discount
        print("parallel:step:", step)
        rdd0 = self.normalrdd
        rdd1 = rdd0.flatMap(lambda x: [(x[0], (y, x[1][0][y], x[1][1], x[1][2], x[1][3], student_able[x[1][3]], skill_able[y], skill_rate[y])) for y in x[1][0].keys()])
        rdd2 = rdd1.mapValues(computezk)
        rdd3 = rdd2.reduceByKey(computeline)
        rdd4 = rdd3.mapValues(computedown)
        rdd5 = rdd4.map(lambda x: x[1])
        rddlogike = rdd5.map(lambda x: x[0])
        rdd_down_student = rdd5.map(lambda x: x[1])
        rdd_down_skill = rdd5.map(lambda x: (x[2], x[3]))
        resloglike = rddlogike.reduce(computeloglike)
        pre_student_able = dict(rdd_down_student.flatMap(lambda x: [(i, x[i]) for i in x.keys()]).reduceByKey(lambda x, y: x + y).map(lambda x: (x[0], x[1] * step + discount * pre_student_able[x[0]])).collect())
        student_able = dict(rdd_down_student.flatMap(lambda x: [(i, x[i]) for i in x.keys()]).reduceByKey(lambda x, y: x + y).map(lambda x: (x[0], pre_student_able[x[0]] + student_able[x[0]])).collect())

        rdddown_result = rdd_down_skill.flatMap(lambda x: [(i, (x[0][i], x[1][i])) for i in x[0].keys()]).reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1]))
        pre_skill_able = dict(rdddown_result.map(lambda x: (x[0], x[1][0] * step + discount * pre_skill_able[x[0]])).collect())
        pre_skill_rate = dict(rdddown_result.map(lambda x: (x[0], x[1][1] * step + discount * pre_skill_rate[x[0]])).collect())
        skill_able = dict(rdddown_result.map(lambda x: (x[0], pre_skill_able[x[0]] + skill_able[x[0]])).collect())
        skill_rate = dict(rdddown_result.map(lambda x: (x[0], pre_skill_rate[x[0]] + skill_rate[x[0]])).collect())
        self.skill_able = skill_able
        self.skill_rate = skill_rate
        self.student_able = student_able
        self.pre_skill_able = pre_skill_able
        self.pre_skill_rate = pre_skill_rate
        self.pre_student_able = pre_student_able
        loglike = resloglike
        return loglike

    def run(self):
        self.loglike = -99999999.
        count = 0
        loglike = self.parallel()
        count += 1
        loglike_new = loglike
        loglike_old = 0
        print("calcul_flag:loglike:" + str(loglike_new))
        print("count:" + str(count))
        while(self.diff > 1):
            print("step:", self.step)
            loglike = self.parallel()
            count += 1
            loglike_old = loglike_new
            loglike_new = loglike
            self.diff = loglike_new - loglike_old
            print("calcul_flag:loglike:" + str(loglike_new))
            print("sub:" + str(self.diff))
            print("count:" + str(count))
        if self.diff > 0:
            self.loglike = loglike_new
        else:
            self.loglike = loglike_old
        aic = -2 * self.loglike + 2 * self.parameternum
        bic = -2 * self.loglike + math.log(self.rows) * self.parameternum

        print("==================================================")
        print("convergence condition: sub<" + str(1))
        print("sub:" + str(self.diff))
        print("end_flag:loglike:" + str(self.loglike))
        print("aic:" + str(aic))
        print("bic:" + str(bic))
        print("totaliteration:" + str(count))
        print("student_able:", self.student_able)
        print("skill_able:", self.skill_able)
        print("skill_rate:", self.skill_rate)

        print("==================================================")

# file_path = 'jtr_test01_biology_30_kmeans_8.csv'
# starttime = datetime.datetime.now()
# cfm = CFM(file_path)
# cfm.run()
# endtime = datetime.datetime.now()


# file_path = sys.argv[1]
# # flag_loop=sys.argv[2]
# # print "loop:",flag_loop
# starttime = datetime.datetime.now()
# cfm = CFM(file_path)
# cfm.run()
# endtime = datetime.datetime.now()
# print ("time: ",(endtime - starttime).seconds)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        # flag_loop=sys.argv[2]
        # print "loop:",flag_loop
        starttime = datetime.datetime.now()
        cfm = CFM(file_path)
        cfm.run()
        endtime = datetime.datetime.now()
        print("time: ", (endtime - starttime).seconds)
    else:
        print('error in argvs')
