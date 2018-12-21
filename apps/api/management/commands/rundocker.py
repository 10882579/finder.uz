from django.core.management.base import BaseCommand

import os

class Command(BaseCommand):
    help = 'Runs docker server'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        os.system('docker run -p 6379:6379 -d redis:2.8')
