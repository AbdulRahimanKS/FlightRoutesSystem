from django.contrib import admin
from .models import Airport, Route


# Register models
admin.site.register([Airport, Route])
