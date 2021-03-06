from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError, transaction

from ...models import Barn, Gruppe

from faker import Faker
import random


def get_random_gender(female_proportion):
    other_gender_prob = 0.02
    if random.random() < other_gender_prob:
        return 'other'
    if random.random() < female_proportion:
        return 'female'
    else:
        return 'male'


def get_random_popularity(n):
    weights = []
    for i in range(n):
        weights.append(random.random())
    total_weight = sum(weights)
    for i in range(n):
        weights[i] = weights[i]/total_weight
    return weights


def get_weighted_pick(choices, weights):
    x = random.random()
    cum_sum = 0.0
    i = -1
    while x > cum_sum:
        i = i + 1
        cum_sum = cum_sum + weights[i]
    return choices[i]


class Command(BaseCommand):
    help = 'Lager N fadderbarn'

    def add_arguments(self, parser):
        parser.add_argument('-n', type=int, default=120, required=False, dest='kull_size')
        parser.add_argument('-p', type=float, default=0.4, required=False, dest='female_proportion')
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--silent', action='store_true')

    def handle(self, *args, **kwargs):
        total_number = kwargs['kull_size']
        female_proportion = kwargs['female_proportion']

        if not settings.DEBUG and not kwargs['force']:
            self.stdout.write('You are not in DEBUG!')
            return

        if kwargs['silent']:
            self.stdout.write = lambda s: None

        self.stdout.write('Deleting existing fadderbarn\n')
        Barn.objects.all().delete()
        self.stdout.write('Success!\n\n')

        fake = Faker('sv_SE')

        #total_number = 120

        groups = list(Gruppe.objects.all())
        popularity = get_random_popularity(len(groups))
        for i in range(len(groups)):
            self.stdout.write("{} has popularity {:.2f}".format(groups[i].name, popularity[i]))

        self.stdout.write('\n')

        for i in range(total_number):
            gender = get_random_gender(female_proportion)
            if gender == 'male':
                name = fake.name_male()
            elif gender == 'female':
                name = fake.name_female()
            else:
                name = fake.name()

            pri_1 = get_weighted_pick(groups, popularity)

            pri_2 = pri_1
            while pri_2 == pri_1:
                pri_2 = get_weighted_pick(groups, popularity)

            pri_3 = pri_1
            while pri_3 == pri_1 or pri_3 == pri_2:
                pri_3 = get_weighted_pick(groups, popularity)

            while True:
                try:
                    with transaction.atomic():
                        Barn.objects.create(name=name, gender=gender,
                                            pri_1=pri_1, pri_2=pri_2, pri_3=pri_3)
                    break
                except IntegrityError:
                    name = name + ' jr.'
            self.stdout.write('Created {}\n'.format(name))

        self.stdout.write('\n\n')

        for i in range(len(groups)):
            self.stdout.write("{} 1st picks for {}".format(Barn.objects.filter(pri_1=groups[i]).count(),
                                                           groups[i].name))

        self.stdout.write('\nFinished!\n\n')
