from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import debug_toolbar


admin.site.site_header = 'Store'
admin.site.index_title = 'Special Access'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),
]
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
