from django.core.management.base import BaseCommand
from DSM.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        # self.student2db()
        self.student2db()

    def student2db(self):
        