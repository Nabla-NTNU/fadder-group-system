from django.shortcuts import render
from django.views.generic.base import TemplateView

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
    pass