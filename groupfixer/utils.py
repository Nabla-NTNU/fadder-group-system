from .models import Gruppe, Barn

import random

MINIMUM_SIZE = 8
MAXIMUM_SIZE = 20
MINIMUM_FEMALE_PROPORTION = 0.3


def get_size_status(member_list):
    status = '\t\t'
    if len(member_list) > MAXIMUM_SIZE:
        status = '\tTOO BIG\t'
    elif len(member_list) < MINIMUM_SIZE:
        status = '\tTOO SMALL'
    return status


def get_female_proportion_status(member_list):
    m = 0
    f = 0
    for member in member_list:
        if member.gender == 'female':
            f += 1
        elif member.gender == 'male':
            m += 1
    prop = f / (m + f)
    status = "{:.2f} female".format(prop)
    if prop < MINIMUM_FEMALE_PROPORTION:
        status += " - TOO LOW"
    return status


def print_diagnostics(groups, members):
    for i in range(len(groups)):
        size_status = get_size_status(members[i])
        gender_status = get_female_proportion_status(members[i])
        print('{}:\t\t{} members{}\t{}'.format(groups[i].name, len(members[i]), size_status, gender_status))
    pass


def run_assign_groups():

    groups = Gruppe.objects.all().prefetch_related('pri_1s')

    #print(groups)

    members = []

    for g in groups:
        members.append(list(g.pri_1s.all()))

    #print(members)
    print_diagnostics(groups, members)
