from django.contrib import admin

from .models import Gruppe, Barn, Session

# Register your models here.

admin.site.register(Gruppe)
admin.site.register(Barn)
admin.site.register(Session, list_display=['date_created', 'active'])
