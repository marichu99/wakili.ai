from django.contrib import admin
from .models import Judge, CaseType, Case

admin.site.register(Judge)
admin.site.register(CaseType)
admin.site.register(Case)
