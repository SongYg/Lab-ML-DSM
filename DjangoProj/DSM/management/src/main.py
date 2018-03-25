#-*- coding:utf-8 -*-
import csv
import MySQLdb
import sys
import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from datetime import datetime


class DSM():
    """docstring for DSM"""

    def __init__(self, sourcePath, matPath, outPath, n_latent_skills, n_skills):
        self.sourcePath = sourcePath
        self.matPath = matPath
        self.outPath = outPath
        self.n_latent_skills = n_latent_skills
        self.n_skills = n_skills

    def read_data(self):
        source_data = pd.read_csv(self.sourcePath)
        stud_step_mat = pd.read_csv(self.matPath, index_col=0)
        return source_data, stud_step_mat

    def handle_result(self, step_ids, latent_skills_steps, skill_labels):
        """
        结果处理
        n_skills:聚类后的skill数量
        steps_ids:step的id列表
        latent_skills_steps:矩阵分解后的潜在skill与step的相关矩阵
        skills_labels:聚类后每个latent_skill对应的label标签

        return: skill与step的关系矩阵
        """
        skills_steps = np.zeros((self.n_skills, len(step_ids)))

        # 相同label的skill行求和
        for i in range(self.n_skills):
            for j in range(len(skill_labels)):
                if skill_labels[j] == i:
                    skills_steps[i, ] += latent_skills_steps[j, ]
        print(skills_steps)
        # 求平均
        average = skills_steps.mean(axis=1)
        average.shape = (self.n_skills, 1)
        # 求和后减去平均值
        average = skills_steps - average
        print(average)
        # 大于等于均值则取1，否则取0
        res = np.where(average >= 0, 1, 0)

        # 转成dataframe格式
        res = pd.DataFrame(res)
        # 添加列名——step_ids
        res.columns = step_ids
        # 添加行名——skill标签
        indexs = ['skill_' + str(i) for i in range(self.n_skills)]
        res.index = indexs

        res.to_csv('../../../../../Data/csv/handle.csv')
        return res

    def output(self, source_data, skills_mat):
        ncols = skills_mat.shape[1]
        max_skills_num = 0
        for i in range(0, ncols):
            col = list(skills_mat.ix[:, i])
            if max_skills_num < col.count(1):
                max_skills_num = col.count(1)

        for i in range(0, max_skills_num):
            source_data['skill' + str(i)] = None

        for i in source_data.index:
            step_id = source_data.iloc[i, 2]
            skills = skills_mat[step_id]
            skills_num = -1
            # print(skills)
            for j in skills:
                if j == 1:
                    skills_num += 1
                    # source_data.iloc[
                    #     i, 4 + skills_num] = 'skill' + str(skills_num)
                    source_data.set_value(
                        i, 'skill' + str(skills_num), 'skill' + str(skills_num))
            if i % 1000 == 0:
                print(datetime.now(), i, source_data.iloc[i])

        outFile = self.outPath + \
            ('latent_skills%dkmeans_skills%d' %
             (self.n_latent_skills, self.n_skills)) + '.csv'
        source_data.to_csv(outFile, index=False)
        print('OK')

    def run(self):
        source_data, stud_step_mat = self.read_data()
        step_ids = stud_step_mat.columns
        stud_ids = stud_step_mat.index
        mn = mNMF(stud_step_mat, self.n_latent_skills)
        v_mat = mn.getUVMat()
        mk = mKmeans(v_mat, self.n_skills)
        labels_mat = mk.getLabelsMat()
        print(labels_mat)
        skills_mat = self.handle_result(step_ids, v_mat, labels_mat)
        self.output(source_data, skills_mat)


class mNMF():
    """"""

    def __init__(self, stud_step_mat, n_components=24):
        self.stud_step_mat = stud_step_mat.fillna(0).values
        self.n_components = n_components

    def getUVMat(self):
        model = NMF(self.n_components, init='nndsvdar', random_state=0)

        w = model.fit_transform(self.stud_step_mat)
        h = model.components_

        print('latent_skill, step' + str(h.shape))
        return h


class mKmeans():
    """
    k-means聚类
    """

    def __init__(self, kmeans_data, n_clusters):
        self.kmeans_data = kmeans_data
        self.n_clusters = n_clusters

    def getLabelsMat(self):
        kmeans = KMeans(self.n_clusters, random_state=0).fit(self.kmeans_data)
        m = kmeans.labels_
        return m

if __name__ == '__main__':
    sourcePath = "../../../../../Data/csv/Stu_step.csv"
    matPath = "../../../../../Data/csv/Stu_diff_mat.csv"
    outPath = "../../../../../Data/result/"
    dsm = DSM(sourcePath=sourcePath, matPath=matPath,
              outPath=outPath, n_latent_skills=20, n_skills=7)
    dsm.run()
