from django.contrib import admin

from .models import Gruppe, Barn, Session

# Register your models here.

admin.site.register(Gruppe)
admin.site.register(Barn, list_display=['name', 'pri_1', 'pri_2', 'pri_3', 'gender', 'given_group'])
admin.site.register(Session, list_display=['date_created', 'active'])
