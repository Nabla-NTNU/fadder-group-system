from .models import Gruppe, Barn

import numpy as np
import cvxpy

MINIMUM_SIZE = 10
MAXIMUM_SIZE = 20
MINIMUM_FEMALE_PROPORTION = 0.35
MAXIMUM_FEMALE_PROPORTION = 0.65

FIRST_PRI_REWARD = 10
SECOND_PRI_REWARD = 8
THIRD_PRI_REWARD = 5


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
    try:
        prop = f / (m + f)
    except ZeroDivisionError:
        prop = 0
    status = "{:.2f} female".format(prop)
    if prop < MINIMUM_FEMALE_PROPORTION:
        status += " - TOO LOW"
    elif prop > MAXIMUM_FEMALE_PROPORTION:
        status += " - TOO HIGH"
    return status


def print_diagnostics(groups, members):
    diag = ''
    for i in range(len(groups)):
        size_status = get_size_status(members[i])
        gender_status = get_female_proportion_status(members[i])
        diag += ('{}:\t\t{} members{}\t{}\n'.format(groups[i].name, len(members[i]), size_status, gender_status))
    return diag


def run_assign_groups():

    groups = Gruppe.objects.all().prefetch_related('pri_1s')
    number_of_groups = len(groups)

    group_members = []

    for g in groups:
        group_members.append(list(g.pri_1s.all()))

    print(print_diagnostics(groups, group_members))

    users = list(Barn.objects.all().order_by('pk'))
    np.random.shuffle(users)
    number_of_users = len(users)

    #number_of_groups = 2
    #number_of_users = 3

    placement_vector = cvxpy.Variable(number_of_groups*number_of_users, boolean=True)

    # Making reward vector

    reward_vector = np.zeros(number_of_users*number_of_groups)

    for i in range(number_of_users):
        for j in range(number_of_groups):
            if users[i].pri_1 == groups[j]:
                reward_vector[i * number_of_groups + j] = FIRST_PRI_REWARD
            elif users[i].pri_2 == groups[j]:
                reward_vector[i * number_of_groups + j] = SECOND_PRI_REWARD
            elif users[i].pri_3 == groups[j]:
                reward_vector[i * number_of_groups + j] = THIRD_PRI_REWARD

    # Making matrix for "only one group per user" constraint

    count_groups_matrix = np.repeat(np.identity(number_of_users), number_of_groups, axis=1)

    # Making matrix for "number of users in group" constraint

    count_users_matrix = np.tile(np.identity(number_of_groups), number_of_users)

    # Making matrix for "number of female users in group" constraint

    count_female_matrix = np.copy(count_users_matrix)
    count_male_and_female_matrix = np.copy(count_users_matrix)

    zeroing_matrix = np.zeros((number_of_groups, number_of_groups))

    for i in range(number_of_users):
        if users[i].gender == 'other':
            count_female_matrix[:, i*number_of_groups:(i+1)*number_of_groups] = zeroing_matrix
            count_male_and_female_matrix[:, i*number_of_groups:(i+1)*number_of_groups] = zeroing_matrix
        elif users[i].gender == 'male':
            count_female_matrix[:, i*number_of_groups:(i+1)*number_of_groups] = zeroing_matrix

    # Creating constraint equations

    one_group_constraint = count_groups_matrix * placement_vector == np.ones(number_of_users)

    max_users_in_group_constraint = count_users_matrix * placement_vector <= np.full(number_of_groups, MAXIMUM_SIZE)
    min_users_in_group_constraint = count_users_matrix * placement_vector >= np.full(number_of_groups, MINIMUM_SIZE)

    count_male_and_female_matrix = count_male_and_female_matrix

    min_female_proportion_constraint = count_female_matrix * placement_vector >= MINIMUM_FEMALE_PROPORTION * count_male_and_female_matrix * placement_vector

    max_female_proportion_constraint = count_female_matrix * placement_vector <= MAXIMUM_FEMALE_PROPORTION * count_male_and_female_matrix * placement_vector

    objective = cvxpy.Maximize(reward_vector*placement_vector)

    problem = cvxpy.Problem(objective, [one_group_constraint, max_users_in_group_constraint,
                                        min_users_in_group_constraint, min_female_proportion_constraint,
                                        max_female_proportion_constraint])

    problem.solve(verbose=True, solver=cvxpy.GLPK_MI, tm_lim=30000)

    for i in range(number_of_users):
        for j in range(number_of_groups):
            if placement_vector.value[i*number_of_groups + j] == 1.0:
                users[i].given_group = groups[j]
                users[i].save()
                break

    group_members = []

    for g in groups:
        group_members.append(list(g.members.all()))

    print(print_diagnostics(groups, group_members))
