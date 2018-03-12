from django.core.management.base import BaseCommand
import pandas as pd
from DSM.models import *


class Command(BaseCommand):
    def formatID(self, i):
        return "%04d" % (i)

    def handle(self, *args, **options):
        self.student2db()
        self.step2db()

    def student2db(self):
        studentFile = '../../Data/txt/ds960_tx_All_Data.txt'

        i = 0
        with open(studentFile, 'r') as infile:
            next(infile)
            for line in infile:
                i = i + 1
                elements = line.strip().split('\t')
                student = Student()
                student.student_id = elements[3].strip()
                student.save()
                print(i)

    def step2db(self):
        stepFile = '../../Data/txt/ds960_step_list.txt'

        with open(stepFile, 'r') as infile:
            next(infile)
            next(infile)
            for line in infile:
                elements = line.strip().split('\t')

                hierarchy = elements[1].strip().split(',', 2)

                sequTemp = hierarchy[0].strip().split(' ', 1)
                sn = sequTemp[1].strip()
                if not Sequence.objects.filter(sequence_name=sn).exists():
                    sequence = Sequence()
                    sequence.sequence_id = 'Sequ' + \
                        self.formatID((Sequence.objects.count() + 1))
                    sequence.sequence_name = sn
                    sequence.save()

                unitTemp = hierarchy[1].strip().split(' ', 1)
                un = unitTemp[1].strip()
                if not Unit.objects.filter(unit_name=un, sequence=Sequence.objects.get(sequence_name=sn)).exists():
                    unit = Unit()
                    unit.unit_id = 'Unit' + self.formatID((Unit.objects.count() + 1))
                    unit.unit_name = un
                    unit.sequence = Sequence.objects.get(sequence_name=sn)
                    unit.save()

                moduleTemp = hierarchy[2].strip().split(' ', 1)
                mn = moduleTemp[1].strip().split(', sec', 1)
                mn = mn[0].strip()

                if not Module.objects.filter(module_name=mn, unit=Unit.objects.get(unit_name=un)).exists():
                    module = Module()
                    module.module_id = 'Modu' + self.formatID((Module.objects.count() + 1))
                    module.module_name = mn
                    module.unit = Unit.objects.get(unit_name=un)
                    module.save()

                pn = elements[2].strip()
                if not Problem.objects.filter(problem_name=pn, module=Module.objects.get(module_name=mn)).exists():
                    problem = Problem()
                    problem.problem_id = "Prob" + \
                        self.formatID((Problem.objects.count() + 1))
                    problem.problem_name = pn
                    problem.module = Module.objects.get(module_name=mn)
                    problem.save()

                step = elements[3].strip().split(' ', 1)
                stepn = step[0].strip()
                stept = step[1].strip()
                stepTypes = {'UpdateRadioButton': '0', 'UpdateComboBox': '1', 'UpdateShortAnswer': '2',
                             'UpdateTextField': '3', 'UpdateCheckbox': '4', 'UpdateOrdering': '5', 'UpdateHotspotSingle': '6'}
                if not Step.objects.filter(step_name=stepn, problem=Problem.objects.get(problem_name=pn)).exists():
                    step = Step()
                    step.step_id = 'Step' + self.formatID((Step.objects.count() + 1))
                    step.step_name = stepn
                    step.step_type = stepTypes[stept]
                    step.problem = Problem.objects.get(problem_name=pn)
                    step.save()
