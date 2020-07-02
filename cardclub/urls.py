"""cardclub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path

from . import views as ajax
from .rest import router

urlpatterns = [
    path('admin/', admin.site.urls),
	path('api/auth/', include('djoser.urls')),
	path('api/auth/', include('djoser.urls.authtoken')),
	path('api/', include(router.urls)),

    path('api/ajax/relation/<str:username>', ajax.friend_relation, name = 'friend_relation'),
    path('api/ajax/add_friend/<str:username>', ajax.add_friend, name = 'add_friend'),
    path('api/ajax/del_friend/<str:username>', ajax.del_friend, name = 'del_friend')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns