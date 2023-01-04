from django.contrib import admin
from apps.whatsapp.models import Whatsapp


@admin.register(Whatsapp)
class WhatsAppAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'is_active')
