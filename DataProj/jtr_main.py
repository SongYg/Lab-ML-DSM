#-*- coding:utf-8 -*-
import sys
import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from datetime import datetime


class DSM:

    def __init__(self, in_file, diff_file, out_file_dir, out_file_name, n_latent_skills, n_skills):

        self.in_file = in_file
        self.diff_file = diff_file
        self.out_file_dir = out_file_dir
        self.n_latent_skills = n_latent_skills
        self.n_skills = n_skills
        self.out_file_name = out_file_name

    """
    基于学生答题数据的skill discovery model
    包括NMF，K-means
    输入格式为csv，列名包括['result', 'student', 'step', 'trynum']
    输出文件为CFM可运行的数据csv格式['result', 'student', 'step', 'trynum', 'skill']
    """

    # def handle_result(self, step_ids, latent_skills_steps, skill_labels):
    #     """
    #     结果处理
    #     n_skills:聚类后的skill数量
    #     steps_ids:step的id列表
    #     latent_skills_steps:矩阵分解后的潜在skill与step的相关矩阵
    #     skills_labels:聚类后每个latent_skill对应的label标签

    #     return: skill与step的关系矩阵
    #     """
    #     skills_steps = np.zeros((n_skills, len(step_ids)))

    #     # 相同label的skill行求和
    #     for i in range(self.n_skills):
    #         for j in range(len(skill_labels)):
    #             if skill_labels[j] == i:
    #                 skills_steps[i,] += latent_skills_steps[j,]

    #     # 求平均
    #     average = skills_steps.mean(axis=1)
    #     average.shape = (n_skills, 1)
    #     # 求和后减去平均值
    #     average = skills_steps - average

    #     # 大于等于均值则取1，否则取0
    #     res = np.where(average >= 0, 1, 0)

    #     # 转成dataframe格式
    #     res = pd.DataFrame(res)
    #     # 添加列名——step_ids
    #     res.columns = step_ids
    #     # 添加行名——skill标签
    #     indexs = ['skill_'+str(i) for i in range(n_skills)]
    #     res.index = indexs

    #     return res

    def handle_result(self, step_ids, latent_skills_steps, skill_labels):
        res = np.zeros((n_skills, len(step_ids)))
        skills = latent_skills_steps.argmax(axis=0)
        for j in range(len(skills)):
            res[skill_labels[skills[j]], j] = 1

        # 转成dataframe格式
        res = pd.DataFrame(res)
        # 添加列名——step_ids
        res.columns = step_ids
        # 添加行名——skill标签
        indexs = ['skill_' + str(i) for i in range(n_skills)]
        res.index = indexs
        return res

        # 读取原始数据
    def get_stud_step_diff(self):
        """
        处理不包含skill的原始数据
        根据attempt次数计算difficulty矩阵

        return: 原始数据矩阵，difficulty矩阵
        """

        source_data = pd.read_csv(self.in_file)
        rows = source_data.shape[0]
        students = source_data['student']
        steps = source_data['step']
        attempts = source_data['trynum']
        steps_set = list(set(steps))
        steps_set.sort()
        students_set = list(set(students))
        students_set.sort()
        stud_step_diff = pd.DataFrame(columns=steps_set, index=students_set)

        # print(datetime.now())
        # print('\treading difficulty matirx...')
        # for index in source_data.index:
        #    line = source_data.ix[index,].values
        #    student_id = line[1]
        #    step_id = line[2]
        #    attempt = line[3]
        #    stud_step_diff.loc[student_id, step_id] = 1 - 1.0 / float(attempt)

        stud_step_diff = pd.read_csv(self.diff_file, index_col=0)
        return source_data, stud_step_diff

    def output(self, source_data, skill_step_corr):
        """
        根据skill与step相关矩阵
        """
        # base_dir = '/home/liuliping/major/myProject/dsm/static/data/cfm/input/'

        out_file = self.out_file_dir + self.out_file_name

        # 列数
        ncols = skill_step_corr.shape[1]
        # 每个step最多的skill数
        max_skill_num = 1
        for i in range(ncols):
            col = list(skill_step_corr.ix[:, i])
            if max_skill_num <= col.count(1):
                max_skill_num = col.count(1)
        # 按照skill多少重构原始数据的列
        for i in range(max_skill_num):
            source_data['skill' + str(i)] = None
        # source_data.columns = source_data.columns + ['skill' + i for i in range(max_skill_num)]

        for index in source_data.index:
            if index % 1000 == 0:
                print(datetime.now())
                print('\tprocess: ' + str(index))
            step_id = source_data.ix[index, 2]

            skills = skill_step_corr[step_id]
            step_skill_num = -1
            for skill_index in range(len(skills)):
                if skills[skill_index] == 1:
                    step_skill_num += 1
                    source_data.ix[index, 4 + step_skill_num] = 'skill_' + str(skill_index)

        source_data.to_csv(out_file, index=False)

        print('~~Successful~~')
        print('\toutput: ' + out_file)

    def run(self):

        # 读取数据
        print(datetime.now())
        print('\treading data...')
        source_data, stud_step_diff = self.get_stud_step_diff()

        step_ids = stud_step_diff.columns
        stud_ids = stud_step_diff.index

        # step 长度
        n_steps = len(step_ids)
        # 矩阵分解
        print(datetime.now())
        print('\tNMFing...')
        nmf = my_NMF(stud_step_diff, self.n_latent_skills)

        latent_skills_steps = nmf.run()

        # k-means聚类
        print(datetime.now())
        print('\tK-meansing...')
        kmeans = my_Kmeans(latent_skills_steps, self.n_skills)
        skill_labels = kmeans.run()

        # 结果处理
        print(datetime.now())
        print('\thanding result...')
        skill_step_corr = self.handle_result(step_ids, latent_skills_steps, skill_labels)

        # 输出结果
        print(datetime.now())
        print('\toutputing result...')
        self.output(source_data, skill_step_corr)


class my_NMF():
    """
    非负矩阵分解
    """

    def __init__(self, stud_step_diff, n_components):
        # 空值缺省为0, student * step
        self.stud_step_diff = stud_step_diff.fillna(0).values
        # 矩阵分解后 潜在skill的个数
        self.n_components = n_components

    def run(self):

        # print ('student, step: ' + str(self.stud_step_diff.shape))
        # 初始化模型
        model = NMF(self.n_components, init='nndsvdar', random_state=0)
        # 分解后的第一个因子, student * latent_skill
        w = model.fit_transform(self.stud_step_diff)
        # 分解后的第二个因子, latent_skill * step
        h = model.components_

        # print ('latent_skill, step: ' + str(h.shape))
        return h


class my_Kmeans():
    """
    k-means聚类
    """

    def __init__(self, kmeans_data, n_clusters):
        self.kmeans_data = kmeans_data
        self.n_clusters = n_clusters

    def run(self):
        kmeans = KMeans(self.n_clusters, random_state=0).fit(self.kmeans_data)
        m = kmeans.labels_
        return m


if __name__ == '__main__':
    if len(sys.argv) == 7:
        [in_file, diff_file, out_file_dir, out_file_name, n_latent_skills, n_skills] = sys.argv[1:]
        # n_latent_skills=int(n_latent_skills,10)
        # n_skills=int(n_skills,10)
        n_latent_skills = int(round(float(n_latent_skills)))
        n_skills = int(round(float(n_skills)))
        dsm = DSM(in_file, diff_file, out_file_dir, out_file_name, n_latent_skills, n_skills)
        dsm.run()
    else:
        print('error in argvs')
