"""
URL configuration for locallibrary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

# перенаправляем запрос на патерн папки catalog.urls

urlpatterns += [ 
    path('catalog/', include('catalog.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

# Подключаем статику 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.views.generic import RedirectView

# переименовываем старый адрес на новый с классом Redirectview() по схеме
# path('старый адрес',RedirectView.as_view(url='новый адрес',permanent='перенаправлением навсегда?'),
# с этого момента базовый адрес не http://127.0.0.1:8000/ а http://127.0.0.1:8000/catalog/

urlpatterns += [ 
    path('', RedirectView.as_view(url='/catalog/', permanent=True)),
]

urlpatterns += [ 
    path('accounts/', include('django.contrib.auth.urls'))
 ]

