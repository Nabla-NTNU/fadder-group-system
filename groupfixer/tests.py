from django.test import TestCase
from django.core.management import call_command
from django.conf import settings

from cvxpy import SolverError

from .utils import run_assign_groups, DEFAULT_MINIMUM_SIZE, DEFAULT_MAXIMUM_SIZE, DEFAULT_MAXIMUM_FEMALE_PROPORTION
from .models import Barn, Gruppe


class SeedCommandsTest(TestCase):
    def test_safe_make_faddergrupper(self):
        print('(test)')
        call_command('make_faddergrupper')
        self.assertEqual(Gruppe.objects.count(), 0)

    def test_safe_make_fadderbarn(self):
        print('(test)')
        call_command('make_fadderbarn')
        self.assertEqual(Barn.objects.count(), 0)

    def test_make_faddergrupper(self):
        call_command('make_faddergrupper', '--force')
        self.assertEqual(Gruppe.objects.count(), 8)

    def test_make_fadderbarn(self):
        call_command('make_faddergrupper', '--force', '--silent')
        call_command('make_fadderbarn', '--force', kull_size=120, female_proportion=0.4)
        self.assertEqual(Barn.objects.count(), 120)


class AssignGroupTest(TestCase):
    def setUp(self):
        call_command('make_faddergrupper', '--force', '--silent')
        call_command('make_fadderbarn', '--force', '--silent', kull_size=120, female_proportion=0.4)

    def test_assign_group(self):
        constraints = {'min_female': 0.25}
        run_assign_groups(constraints)
        self.assertFalse(Barn.objects.filter(given_group=None).exists())
        self.assertLessEqual(max([g.members.count() for g in Gruppe.objects.all()]), DEFAULT_MAXIMUM_SIZE)
        self.assertGreaterEqual(min([g.members.count() for g in Gruppe.objects.all()]), DEFAULT_MINIMUM_SIZE)
        self.assertLessEqual(max([g.members.filter(gender='female').count() / g.members.count() for g in Gruppe.objects.all()]), DEFAULT_MAXIMUM_FEMALE_PROPORTION)
        self.assertGreaterEqual(max([g.members.filter(gender='female').count() / g.members.count() for g in Gruppe.objects.all()]), constraints['min_female'])

    def test_bad_constraint(self):
        bad_constraints = {'min_size': 16}
        self.assertRaises(SolverError, lambda: run_assign_groups(bad_constraints))
