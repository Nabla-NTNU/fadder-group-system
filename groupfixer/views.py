from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.utils.html import escape
from django.db import IntegrityError
from django.conf import settings

import json
from urllib import parse, request
import csv
from math import ceil, floor

from cvxpy.error import SolverError

from .models import Gruppe, Barn, Session
from .utils import run_assign_groups, print_diagnostics, \
    DEFAULT_MINIMUM_SIZE, DEFAULT_MAXIMUM_SIZE, DEFAULT_MINIMUM_FEMALE_PROPORTION, DEFAULT_MAXIMUM_FEMALE_PROPORTION


def get_active_session(request):
    try:
        session = Session.objects.get(active=True)
        exists_active = True
    except Session.DoesNotExist:
        exists_active = False
        session = None
    return session, exists_active


class MainPage(TemplateView):

    template_name = 'mainpage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Gruppe.objects.all()
        context['genders'] = Barn.GENDERS
        return context


def post_choices(http_request):

    if http_request.method != 'POST':
        return HttpResponseRedirect(reverse('groupfixer:main'))

    try:
        ''' Begin reCAPTCHA validation '''
        recaptcha_response = http_request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = parse.urlencode(values).encode()
        req = request.Request(url, data=data)
        response = request.urlopen(req)
        result = json.loads(response.read().decode())
        if not result['success']:
            messages.error(http_request, 'Ugyldig reCAPTCHA. Prøv igjen.')
            return HttpResponseRedirect(reverse('groupfixer:main'))
        ''' End reCAPTCHA validation '''

        try:
            session, exists_active = get_active_session(http_request)
        except Session.MultipleObjectsReturned:
            messages.error(http_request, 'Flere påmeldinger er aktive! Ta kontakt med administrator.')
            return HttpResponseRedirect(reverse('groupfixer:main'))

        if not exists_active:
            messages.error(http_request, 'Ingen aktive påmeldinger.')
            return HttpResponseRedirect(reverse('groupfixer:main'))

        name = escape(http_request.POST['name'])
        if name == '':
            raise KeyError
        gender = escape(http_request.POST['gender'])
        pri_1 = Gruppe.objects.get(id=http_request.POST['pri_1'])
        pri_2 = Gruppe.objects.get(id=http_request.POST['pri_2'])
        pri_3 = Gruppe.objects.get(id=http_request.POST['pri_3'])
    except KeyError:
        messages.error(http_request, 'Ugyldig svar. Prøv igjen.')
        return HttpResponseRedirect(reverse('groupfixer:main'))
    except Gruppe.DoesNotExist:
        messages.error(http_request, 'Velg tre grupper.')
        return HttpResponseRedirect(reverse('groupfixer:main'))
    if pri_1 == pri_2 or pri_1 == pri_3 or pri_2 == pri_3:
        messages.error(http_request, 'Velg en gruppe kun én gang.')
        return HttpResponseRedirect(reverse('groupfixer:main'))
    if not (gender == 'male' or gender == 'female' or gender == 'other'):
        messages.error(http_request, 'Hvordan greide du dette? Du burde søke Webkom!')
        return HttpResponseRedirect(reverse('groupfixer:main'))

    new_fadderbarn = Barn(name=name, gender=gender,
                          pri_1=pri_1, pri_2=pri_2, pri_3=pri_3)
    try:
        new_fadderbarn.save()

        context = dict()
        context['name'] = new_fadderbarn.name
        context['gender'] = new_fadderbarn.get_gender_display()
        context['pri_1'] = new_fadderbarn.pri_1.name
        context['pri_2'] = new_fadderbarn.pri_2.name
        context['pri_3'] = new_fadderbarn.pri_3.name

        return render(http_request, 'success.html', context=context)
    except IntegrityError:
        messages.error(http_request, 'Navnet ditt er ikke unikt! Prøv igjen')
        return HttpResponseRedirect(reverse('groupfixer:main'))


@staff_member_required
def control_panel(http_request):
    context = dict()
    try:
        session, exists_active = get_active_session(http_request)
    except Session.MultipleObjectsReturned:
        messages.error(http_request, 'Mer enn en aktiv påmelding! Fiks dette først')
        return HttpResponseRedirect(reverse('admin:groupfixer_session_changelist'))
    context['session'] = session
    context['exists_active'] = exists_active
    context['number_of_users'] = Barn.objects.count()
    context['number_of_male_users'] = Barn.objects.filter(gender='male').count()
    context['number_of_female_users'] = Barn.objects.filter(gender='female').count()
    try:
        prop = context['number_of_female_users'] / (context['number_of_male_users'] + context['number_of_female_users'])
    except ZeroDivisionError:
        prop = 0
    context['female_prop'] = "{:.1f}".format(prop*100)

    context['not_placed'] = Barn.objects.filter(given_group=None)

    context['groups'] = Gruppe.objects.all().prefetch_related('members')

    group_members = []

    if context['not_placed'].exists():
        context['groups'] = Gruppe.objects.all().prefetch_related('pri_1s')
        for g in context['groups']:
            group_members.append(list(g.pri_1s.all()))
    else:
        context['groups'] = Gruppe.objects.all().prefetch_related('members')
        for g in context['groups']:
            group_members.append(list(g.members.all()))

    context['min_size'] = http_request.session.get('min_size', DEFAULT_MINIMUM_SIZE)
    context['max_size'] = http_request.session.get('max_size', DEFAULT_MAXIMUM_SIZE)
    context['min_female'] = http_request.session.get('min_female', DEFAULT_MINIMUM_FEMALE_PROPORTION)
    context['max_female'] = http_request.session.get('max_female', DEFAULT_MAXIMUM_FEMALE_PROPORTION)

    context['diag'] = print_diagnostics(context['groups'], group_members, http_request.session)

    context['female_prop_ratio'] = "{:.2f}".format(prop)
    context['average_per_group_floor'] = int(floor(context['number_of_users']/len(context['groups'])))
    context['average_per_group_ceil'] = int(ceil(context['number_of_users']/len(context['groups'])))

    return render(http_request, 'control_panel.html', context=context)


@staff_member_required
def deactivate_session(http_request):
    if http_request.method == 'POST':
        try:
            session, exists_active = get_active_session(http_request)
        except Session.MultipleObjectsReturned:
            messages.error(http_request, 'Mer enn en aktiv påmelding! Fiks dette først')
            return HttpResponseRedirect(reverse('admin:groupfixer_session_changelist'))

        if not exists_active:
            messages.error(http_request, 'Ingen aktive påmeldinger')
        else:
            session.active = False
            session.save()
            messages.success(http_request, 'Påmelding deaktivert')
    return HttpResponseRedirect(reverse('groupfixer:control_panel'))


@staff_member_required
def activate_session(http_request):
    if http_request.method == 'POST':
        session = Session()
        session.save()
        messages.success(http_request, 'Påmelding aktivert')
    return HttpResponseRedirect(reverse('groupfixer:control_panel'))


@staff_member_required
def assign_groups(http_request):
    if http_request.method == 'POST':
        try:
            http_request.session['min_size'] = int(escape(http_request.POST['min_size']))
            http_request.session['max_size'] = int(escape(http_request.POST['max_size']))
            http_request.session['min_female'] = float(escape(http_request.POST['min_female']))
            http_request.session['max_female'] = float(escape(http_request.POST['max_female']))
        except (KeyError, ValueError):
            messages.error(http_request, 'Ugyldige instilliger. Prøv igjen.')
            return HttpResponseRedirect(reverse('groupfixer:control_panel'))
        try:
            run_assign_groups(http_request.session)
        except SolverError:
            messages.error(http_request, 'Kunne ikke fordele med gitte betingelser innen gitt tid!')
    return HttpResponseRedirect(reverse('groupfixer:control_panel'))


@staff_member_required
def generate_csv(http_request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv', charset='latin-1')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response, dialect='excel')

    table = list()

    groups = Gruppe.objects.all().prefetch_related('members')
    maximum_size = max([g.members.count() for g in groups])

    for group in groups:
        row = list()
        row.append(group.name)
        row.append('')
        members = group.members.all()
        for i in range(maximum_size):
            try:
                row.append(members[i].name)
            except IndexError:
                row.append('')
        table.append(row)
        # Insert empty column between groups
        table.append(['']*(maximum_size + 2))

    # Transpose the table
    table = map(list, zip(*table))

    for row in table:
        writer.writerow(row)

    return response
