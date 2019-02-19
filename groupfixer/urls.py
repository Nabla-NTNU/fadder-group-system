from django.urls import path
from groupfixer.views import MainPage, post_choices, success

app_name = 'groupfixer'

urlpatterns = [
    path('',
         MainPage.as_view(),
         name='main'),
    path('post',
         post_choices,
         name='post'),
    path('success',
         success,
         name='success')
]
