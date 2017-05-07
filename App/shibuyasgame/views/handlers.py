from django.shortcuts import render
from django.urls import reverse
from shibuyasgame.helpers import *

def handle404(request, **kwargs):
    context = {'error':"This page doesn't exist."}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    return render(request, 'shibuyasgame/message.html', context, status=404)

def handle403(request, **kwargs):
    context = {'error':"You don't have permission to be here. If you think you should, go poke an officer."}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    return render(request, 'shibuyasgame/message.html', context, status=403)

def handle500(request, **kwargs):
    context = {'error':"SERVER ERROR. Poke the <a href=\"%s\">webmaster</a> if you think you should be able to do something here."%(str(reverse('uprofile',kwargs={'username':getWebmaster()})))}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    return render(request, 'shibuyasgame/message.html', context, status=500)
