import csv
import MySQLdb
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from bisect import *


def export_csv_entry(filePath):
    db = MySQLdb.connect('localhost', 'root', '123456', 'dsmdb')
    cursor = db.cursor()
    outFilePath = '/home/yuguang/PycharmProjects/ygProj/DSM/data/csv/Stu_diff.csv'
    with open(filePath, 'rb') as infile, open(outFilePath, 'wb') as outfile:
        next(infile)
        writer = csv.writer(outfile)
        writer.writerow(['Stu', 'Step', 'Diff'])
        for line in infile:
            eles = line.strip().split('\t')
            step = eles[19].strip().split(' ')
            step = step[0].strip()
            stud = eles[3].strip()
            outcome = eles[22].strip()
            attempt = eles[20].strip()
            if step:
                row = [''] * 3
                sql = "select step_id from DSM_step where step_name = '%s'" % (
                    step)
                cursor.execute(sql)
                result = cursor.fetchall()
                step_id = result[0][0]
                row[0] = stud
                row[1] = step_id
                diff = 1.0
                if outcome == 'CORRECT':
                    d = float(attempt)
                    diff = round(1 - 1 / d, 6)
                row[2] = diff
                writer.writerow(row)
                print(row)
    cursor.close()


def export_matrix(infilePath, outfilePath):
    source_data = pd.read_csv(infilePath)
    rows = source_data.shape[0]
    studs = source_data['Stu']
    steps = source_data['Step']
    diff = source_data['Diff']
    studs_set = list(set(studs))
    steps_set = list(set(steps))
    studs_set.sort()
    steps_set.sort()

    stu_step_diff_mat = pd.DataFrame(columns=steps_set, index=studs_set)
    for i in source_data.index:
        line = source_data.ix[i, ].values
        stud_id = line[0]
        step_id = line[1]
        d = line[2]
        # stu_step_diff_mat.loc[stud_id, step_id] = float(d)
        stu_step_diff_mat.set_value(stud_id, step_id, float(d))
        # stud_index = bisect_left(studs_set, stud_id)
        # step_index = bisect_left(steps_set, step_id)
        if i % 1000 == 0:
            print(i, datetime.now())
            # print(stud_index, step_index, i, datetime.now())

    stu_step_diff_mat.to_csv(outfilePath, sep=',', encoding='utf-8')


def test(infilePath):
    source_data = pd.read_csv(infilePath)
    rows = source_data.shape[0]
    studs = source_data['Stu']
    steps = source_data['Step']
    diff = source_data['Diff']
    studs_set = list(set(studs))
    steps_set = list(set(steps))
    print(len(steps_set))


if __name__ == '__main__':
    # filePath = '/home/yuguang/PycharmProjects/ygProj/DSM/data/rawData/ds960_tx/transaction_All_Data.txt'
    # export_csv_entry(filePath)

    mat_infile = '/home/yuguang/PycharmProjects/ygProj/DSM/data/csv/Stu_diff.csv'
    mat_outfile = '/home/yuguang/PycharmProjects/ygProj/DSM/data/csv/Stu_diff_mat.csv'
    # export_matrix(mat_infile, mat_outfile)

    test(mat_infile)
