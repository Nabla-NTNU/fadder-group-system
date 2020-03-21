from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from ...models import Gruppe


class Command(BaseCommand):
    help = 'Lager faddergruppene fra 2018'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--silent', action='store_true')

    def handle(self, *args, **kwargs):
        if not settings.DEBUG and not kwargs['force']:
            self.stdout.write('You are not in DEBUG!')
            return

        if kwargs['silent']:
            self.stdout.write = lambda s: None

        self.stdout.write('Deleting existing groups\n')
        Gruppe.objects.all().delete()
        self.stdout.write('Success!\n\n')

        gruppenavn = ['Faddeterminant ',
                      'Alfa           ',
                      'Beta           ',
                      'Gamma          ',
                      'Fadder Freedman',
                      'Ehrenfest      ',
                      'ÆreNash        ',
                      'ForbiddenFadder']

        for navn in gruppenavn:
            Gruppe.objects.create(name=navn)
            self.stdout.write('Created {}\n'.format(navn))
        self.stdout.write('\nFinished!\n\n')
