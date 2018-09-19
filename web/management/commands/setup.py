import sys
from datetime import datetime, timedelta
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--run', action='store_true', default=False, help='')
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        with open('users.txt', 'r') as f:
            for l in f:
                name = l.strip()
                User.objects.create_superuser(username=name, password=name, email='')
        pass

