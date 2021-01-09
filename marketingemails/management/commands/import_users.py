import datetime
import time
import pytz
import csv

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as timezone_now

from marketingemails.models import User

class Command(BaseCommand):
    help = 'Import users from a .csv file to the Django Models. Format: name|email|city|link_to_send'

    def add_arguments(self, parser):
        parser.add_argument('file', help="path to .csv file")
        parser.add_argument('s', help="Start index to import from .csv", type=int)
        parser.add_argument('e', help="End index to import from .csv | -1=add till last row", type=int)

    def handle(self, *args, **options):
        path_to_file = options.get('file')
        start_idx = options.get('s')
        end_idx = options.get('e')
        count = end_idx - start_idx
        
        if end_idx == -1:
            count = 999999999999999999

        
        if end_idx != -1:
            if end_idx <= start_idx:
                raise ValueError('End index should be larger')
        
        with open(path_to_file) as csv_file:
            rows = csv.reader(csv_file, delimiter=',')
          
            s = start_idx
            while s != 0:
                next(rows)
                s -= 1

            c = count
            while c:
                user_csv = next(rows)
                user_to_save = User(
                    name = user_csv[0] +' ' + user_csv[1],
                    email_address = user_csv[-1],
                    city = user_csv[2],
                    marketing_link='https://yourownroom.com/',
                    join_date=timezone_now()
                )
                user_to_save.save()
                c -= 1
            
        print(f'Added {count} users')
            



            
