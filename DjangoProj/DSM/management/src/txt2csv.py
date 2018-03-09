import csv


def readAndWrite(inPath, outPath):
    with open(inPath, 'r') as infile, open(outPath, 'wb') as outfile:
        writer = csv.writer(outfile)
        for line in infile:
            words = str.split(line, '\t')
            writer.writerow(words)


if __name__ == '__main__':
    infiles = ['../../data/rawData/ds960_kcm.txt', '../../data/rawData/ds960_step_list.txt',
               '../../data/rawData/ds960_student_step/student_step_All_Data.txt', '../../data/rawData/ds960_student_problem/student_problem_All_Data.txt', '../../data/rawData/ds960_tx/transaction_All_Data.txt']
    outfiles = ['../../data/csv/ds960_kcm.csv', '../../data/csv/ds960_step_list.csv',
                '../../data/csv/student_step_All_Data.csv', '../../data/csv/student_problem_All_Data.csv', '../../data/csv/transaction_All_Data.csv']
    for i in range(0, len(infiles)):
        readAndWrite(infiles[i], outfiles[i])
