"""zhugeApi URL Configuration

The `urlpatterns` list routes URLs to views_dir. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views_dir
    1. Add an import:  from my_app import views_dir
    2. Add a URL to urlpatterns:  url(r'^$', views_dir.home, name='home')
Class-based views_dir
    1. Add an import:  from other_app.views_dir import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^', include('zhugedanao.urls')),
    url(r'^wendaku/', include('wendaku.urls')),
    url(r'^ribao/', include('ribao.urls')),
    url(r'^zhugeproject/', include('zhugeproject.urls',namespace='zhugeproject')),


]
