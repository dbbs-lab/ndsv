"""vault URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from ndsv.views import RedshiftQuasarGalaxyBeamRecepticle
from ndsv.views import BeltramiPseudosphereEmitter

urlpatterns = [
    path('admin/', admin.site.urls),
    path("o/", include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('beam/receive', RedshiftQuasarGalaxyBeamRecepticle.as_view()),
    path(r'beam/emit/<slug:beam_id>/<int:artifact_id>/<path:file>/', BeltramiPseudosphereEmitter.as_view()),
]
