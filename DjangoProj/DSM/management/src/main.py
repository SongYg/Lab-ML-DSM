#-*- coding:utf-8 -*-
import csv
import MySQLdb
import sys
import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans


class DSM():
    """docstring for DSM"""

    def __init__(self, matPath, outPath, n_latent, n):
        super(DSM, self).__init__()
        self.matPath = matPath
        self.outPath = outPath
        self.n_latent = n_latent
        self.n = n

    def read_mat(self):
        stud_step_mat = pd.read_csv(self.matPath)
        return stud_step_mat


class mNMF():
    """"""

    def __init__(self, stud_step_mat, n_components=24):
        self.stud_step_mat = stud_step_mat.fillna(0).values
        self.n_components = n_components

    def run(self):
        model = NMF(self.n_components, init='nndsvdar', random_state=0)

        w = model.fit_transform(self.stud_step_mat)
        h = model.components_

        print('latent_skill, step' + str(h.shape))
        return h


if __name__ == '__main__':
