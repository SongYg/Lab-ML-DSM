from django.test import TestCase
from DSM.models import *
# Create your tests here.


class testCase(TestCase):

    def test_Step(self):
        # test DB whether the data is all or not
        filePath = '/home/yuguang/PycharmProjects/ygProj/DSM/data/rawData/ds960_tx/transaction_All_Data.txt'

        with open(filePath, 'rb') as testFile:
            next(testFile)
            for line in testFile:
                words = line.strip().split('\t')

                sequName = words[12].strip()
                if Sequence.objects.get(sequence_name=sequName):
                    print(sequName)
