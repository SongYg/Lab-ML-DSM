import csv


def readAndWrite(inPath, outPath):
    with open(inPath, 'r') as infile, open(outPath, 'wb') as outfile:
        writer = csv.writer(outfile)
        for line in infile:
            words = str.split(line, '\t')
            writer.writerow(words)


if __name__ == '__main__':
    infiles = ["../../Data/txt/ds960_tx_All_Data.txt"]
    outfiles = ["../../Data/csv/ds960_tx_All_Data.csv"]
    for i in range(0, len(infiles)):
        readAndWrite(infiles[i], outfiles[i])
