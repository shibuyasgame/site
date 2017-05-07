"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from shibuyasgame.views import *

urlpatterns = [
    # Basic urls
    url(r'^$', basic.home, name="home"),
    url(r'^login$', auth_views.login, {'template_name':'shibuyasgame/login.html', 'redirect_field_name':'home'}, name='login'),
    url(r'^logout$', auth_views.logout_then_login, name="logout"),
    url(r'^register$', basic.register, name="register"),
    url(r'^confirm/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', basic.confirm, name="confirm"),
    url(r'^u$', basic.allUsers, name="allUsers"),
    url(r'^c$', basic.allCharacters, name="allChars"),
    url(r'^u/(?P<username>[a-zA-Z0-9_@\+\-]+)$', basic.viewUser, name="uprofile"),
    #url(r'^/w(?P<week>[0-9]+)/characters$', views.week, name="week"),
    url(r'^c/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)$', basic.viewChar, name="cprofile"),
    url(r'^search$', basic.searchLanding, name="searchLanding"),
    url(r'^items$', basic.listItems, name="items"),
    url(r'^p/(?P<pid>[a-zA-Z0-9_@\+\-]+)$', basic.viewPost, name="viewPost"),
    # User views
    url(r'^settings$', user.userSettings, name="settings"),
    url(r'^create$', user.createCharacter, name="createChar"),
    url(r'^edit/c/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)$', user.editChar, name="editChar"),
    url(r'^consume/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)/(?P<itemid>[0-9]+)/(?P<quantity>[0-9]+)$', user.consumeItem, name="consume"),
    url(r'^equip/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)/(?P<itemid>[0-9]+)$', user.equip, name="equip"),
    url(r'^dequip/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)/(?P<itemid>[0-9]+)$', user.dequip, name="dequip"),
    # Admin views
    url(r'^admin/approve/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)$', admin.approve, name="approve"),
    url(r'^admin/post$', admin.post, name="post"),
    url(r'^admin/edit$', admin.adminEditHome, name="adminEditHome"),
    url(r'^admin/create/(?P<item_type>[a-zA-Z0-9_@\+\-]+)$', admin.createItem, name="createItem"),
    url(r'^admin/edit/p/(?P<pid>[a-zA-Z0-9_@\+\-]+)$', admin.editPost, name="editPost"),
    url(r'^admin/edit/c/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)$', admin.adminEditChar, name="adminEditChar"),
    url(r'^admin/edit/u/(?P<username>[a-zA-Z0-9_@\+\-]+)$', admin.adminEditUser, name="adminEditUser"),
    url(r'^admin/add/c/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)/(?P<itemtype>[a-z])$', admin.addToInventory, name="addItem"),
    url(r'^admin/remove/c/(?P<charname>[a-zA-Z0-9_@\+\-]+)(?P<suffix>[Wek0-9\)\(_]*)/(?P<itemtype>[a-z])$', admin.deleteFromInventory, name="removeItem"),
    # Queries
    url(r'^serverTime', query.getServerTime, name="getTime"),
]
