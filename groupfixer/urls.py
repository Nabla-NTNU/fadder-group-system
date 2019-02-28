from django.urls import path
from groupfixer.views import MainPage, post_choices, success, control_panel, deactivate_session, activate_session, \
                             assign_groups, generate_csv

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
         name='success'),
    path(r'control',
         control_panel,
         name='control_panel'),
    path('control/deactivate',
         deactivate_session,
         name='deactivate_session'),
    path('control/activate',
         activate_session,
         name='activate_session'),
    path('control/assign',
         assign_groups,
         name='assign_groups'),
    path('control/export.csv',
         generate_csv,
         name='csv'),
]
