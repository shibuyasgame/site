from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse, Http404
from django.contrib import messages
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction, IntegrityError

from django.db.models import Q

# Email shenanigans
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from shibuyasgame.models import *
from shibuyasgame.forms import *
from shibuyasgame.helpers import *
import shibuyasgame.s3 as s3
import django.utils.dateparse as dateparse
import time


# Basics
def home(request):
    context = {'posts':Post.objects.order_by('time').reverse()}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    return render(request, 'shibuyasgame/index.html', context)

@transaction.atomic
def register(request):
    if request.user.is_authenticated():
        return render(request, 'shibuyasgame/message.html',
            {'you':UserProfile.objects.get(user=request.user), 'error':"Please logout to register."})
    form = RegistrationForm()
    context = {'forms': {form}, 'button': "Register", 'action': str(reverse('register'))}
    if request.method == 'GET':
        return render(request, 'shibuyasgame/form.html', context)
    form = RegistrationForm(request.POST)
    if not form.is_valid():
        context['forms'] = {form}
        return render(request, 'shibuyasgame/form.html', context)
    else:
        try:
            new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                                password=form.cleaned_data['password'],
                                                first_name=form.cleaned_data['first_name'],
                                                email=form.cleaned_data['email'])
            new_user.is_active = False
            new_user.save()
        except IntegrityError as e:
            messages.add_message(request, messages.INFO, e)
            return render(request, 'shibuyasgame/form.html', context)
        new_userprofile = UserProfile(user=new_user)
        new_userprofile.save()

        token = default_token_generator.make_token(new_user)
        email_body = '''
        Thanks for signing up! Please click the link below to
        verify your email address and complete your registration!

        http://%s%s
        ''' % (request.get_host(), reverse('confirm', args=(new_user.username, token)))
        send_mail(subject="Verify your email address",
                  message=email_body,
                  from_email="xankuroi+donotreply@gmail.com",
                  recipient_list=[new_user.email])
        return render(request, 'shibuyasgame/message.html', {'message': "Thank you for registering! A confirmation message should be reaching you soon."})

@transaction.atomic
def confirm(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    # TODO everyone currently has moderator permissions
    composer = Group.objects.get(name="Composer")
    user.groups.add(composer)
    user.save()
    return render(request, 'shibuyasgame/message.html',
        {'message': "Your account has been activated! Please login to continue."})


# Lookups
def searchLanding(request):
    context = {'forms':{SearchForm()}, 'button': "Search", 'action': str(reverse("searchLanding"))}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    if request.method == 'GET':
        return render(request, 'shibuyasgame/form.html', context)
    form = SearchForm(request.POST)
    context['forms'] = {form}
    if form.is_valid():
        query = form.cleaned_data['search']
        users = User.objects.filter(Q(first_name__contains=query) | Q(username__contains=query))
        userresults = UserProfile.objects.filter(user__in=users)
        chars = CharProfile.objects.filter(char_name__contains=query)
        context['userresults'] = userresults
        context['charresults'] = chars
        context["POST"] = 'POST'
    return render(request, 'shibuyasgame/form.html', context)

def viewUser(request, username):
    context = {}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        context['chars'] = profile.charprofile_set.all()
        context['profile'] = profile;
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        context['error'] = "No such user."
        return render(request, 'shibuyasgame/message.html', context)
    return render(request, 'shibuyasgame/uprofile.html', context)

def viewChar(request, charname, suffix):
    context = {}
    template = 'shibuyasgame/cprofile.html'
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
        check = True
    try:
        char = CharProfile.objects.get(char_name=charname, suffix=suffix)
        context['char'] = char;
        info = CharStats.objects.get(character=char, week=char.week)
        thread = {'hp': 0, 'atk':0, 'def':0}
        if info.inventory:
            context['finventory'] = info.inventory.filter(item_type=ContentType.objects.get_for_model(Food))
            pinventory = info.inventory.filter(item_type=ContentType.objects.get_for_model(Pin))
            tinventory = info.inventory.filter(item_type=ContentType.objects.get_for_model(Thread))
            context['pinventory_e'] = pinventory.filter(is_equipped=True)
            context['tinventory_e'] = tinventory.filter(is_equipped=True)
            context['pinventory'] = pinventory.filter(is_equipped=False)
            context['tinventory'] = tinventory.filter(is_equipped=False)
            boosters = Pin.objects.filter(booster=True)
            context['boosted'] = pinventory.filter(item_id__in=boosters)
            thread=calculate_thread_stats(info.pronouns, context['tinventory_e'])
        context['info'] = info
        context['pronouns'] = translatePronouns(info.pronouns)
        total ={'hp':info.base_hp + thread['hp'] + info.misc_hp,
                'atk':info.base_atk + thread['atk'] + info.misc_atk,
                'def':info.base_def + thread['def'] + info.misc_def}
        context['total'] = total;
        context['thread'] = thread;
    except (CharProfile.DoesNotExist):
        context['error'] = "No such character."
        return render(request, 'shibuyasgame/message.html', context)
    return render(request, template, context)

def viewPost(request, pid):
    context = {}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    try:
        post = Post.objects.filter(id=pid)
        context['posts'] = post
    except Post.DoesNotExist:
        context['error'] = "Post not found."
        return render(request, 'shibuyasgame/message.html', context)
    return render(request, 'shibuyasgame/index.html', context)

def listItems(request):
    context = {'contentTitle':"All Items",'foods':Food.objects.all(),
        'threads':Thread.objects.all(), 'pins':Pin.objects.all()}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    return render(request, 'shibuyasgame/list.html', context)

def allUsers(request):
    context = {'contentTitle':"All Users"}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    context['list'] = UserProfile.objects.all()
    context['userList'] = True
    return render(request, 'shibuyasgame/userlist.html', context)

def allCharacters(request):
    context = {'contentTitle':"All Characters"}
    if checkUser(request):
        context['you'] = UserProfile.objects.get(user=request.user)
    context['list'] = CharProfile.objects.all()
    return render(request, 'shibuyasgame/userlist.html', context)

### JSON
def getInventory(request, charname, suffix):
    char = get_object_or_404(CharProfile, char_name=charname, suffix=suffix)
    charstats = get_object_or_404(CharStats, character=char)
    items = charstats.inventory
    response_text = serializers.serialize('json', items)
    return HttpResponse(response_text, content_type='application/json')
