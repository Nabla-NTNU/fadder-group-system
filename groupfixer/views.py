from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.urls import reverse
from django.utils.html import escape
from django.db import IntegrityError
from django.conf import settings

import json
import urllib

from .models import Gruppe, Barn

# Create your views here.


class MainPage(TemplateView):

    template_name = 'mainpage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Gruppe.objects.all()
        context['genders'] = Barn.GENDERS
        return context


def post_choices(request):
    try:
        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        ''' End reCAPTCHA validation '''
        if not result['success']:
            messages.error(request, 'Ugyldig reCAPTCHA. Prøv igjen.')
            return HttpResponseRedirect(reverse('groupfixer:main'))

        name = escape(request.POST['name'])
        if name == '':
            raise KeyError
        gender = escape(request.POST['gender'])
        pri_1 = Gruppe.objects.get(id=request.POST['pri_1'])
        pri_2 = Gruppe.objects.get(id=request.POST['pri_2'])
        pri_3 = Gruppe.objects.get(id=request.POST['pri_3'])
    except KeyError:
        messages.error(request, 'Ugyldig svar. Prøv igjen.')
        return HttpResponseRedirect(reverse('groupfixer:main'))
    except Gruppe.DoesNotExist:
        messages.error(request, 'Velg tre grupper.')
        return HttpResponseRedirect(reverse('groupfixer:main'))
    if pri_1 == pri_2 or pri_1 == pri_3 or pri_2 == pri_3:
        messages.error(request, 'Velg en gruppe kun én gang.')
        return HttpResponseRedirect(reverse('groupfixer:main'))
    if not (gender == 'male' or gender == 'female' or gender == 'other'):
        messages.error(request, 'Hvordan greide du dette? Du burde søke Webkom!')
        return HttpResponseRedirect(reverse('groupfixer:main'))

    new_fadderbarn = Barn(name=name, gender=gender,
                          pri_1=pri_1, pri_2=pri_2, pri_3=pri_3)
    try:
        new_fadderbarn.save()
        return HttpResponseRedirect(reverse('groupfixer:success'))
    except IntegrityError:
        messages.error(request, 'Navnet ditt er ikke unikt! Prøv igjen')
        return HttpResponseRedirect(reverse('groupfixer:main'))


def success(request):
    return render(request, 'success.html')
