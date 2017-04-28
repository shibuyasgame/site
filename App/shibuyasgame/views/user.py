from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse, Http404, JsonResponse
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

# Editing
@login_required
@transaction.atomic
def createCharacter(request):
    context = {'you':UserProfile.objects.get(user=request.user), 'button':"Create",
        'forms':[CreateCharForm(), CreateCharStatsForm()],
        'action': str(reverse('createChar')), 'contentTitle':"Create Character"}
    if request.method == 'GET':
        return render(request, 'shibuyasgame/form.html', context)
    form = CreateCharForm(request.POST)
    form2 = CreateCharStatsForm(request.POST)
    if not form.is_valid() or not form2.is_valid():
        context['forms'] = [form, form2]
        return render(request, 'shibuyasgame/form.html', context)
    else:
        suffix = ""
        charprof = CharProfile.objects.filter(char_name=form.cleaned_data['char_name'])
        if CharProfile.objects.filter(char_name=form.cleaned_data['char_name']):
            if CharProfile.objects.filter(char_name=form.cleaned_data['char_name'], mun=context['you']):
                context['message'] = '''
                You already have a character with this chat name. If you want to create
                another character with this name, please contact a moderator.
                '''
                return render(request, 'shibuyasgame/message.html', context)
            if CharProfile.objects.filter(suffix="_(Week_%s)"%(getWeek()), char_name=form.cleaned_data['char_name']):
                context['error'] = '''
                There's already a character with that chat name this week! Please
                contact a moderator if you want to make a character with this name.
                '''
                return render(request, 'shibuyasgame/message.html', context)
            suffix = "_(Week_%s)"%(getWeek())
        try:
            with transaction.atomic():
                new_char = form.save(commit=False)
                new_char.mun = context['you']
                new_char.suffix = suffix
                new_char.week = getWeek()
                new_char.save()

                new_stat = form2.save(commit=False)
                new_stat.character = new_char
                new_stat.week = getWeek()
                new_stat.save()
            context['message'] = '''
            Character created! Please wait for a mod to approve your character.
            You can still view your character's page in the meantime by visiting the link below:
            <a href="http://%s%s">Click here!</a>''' % (request.get_host(), reverse('cprofile',
                kwargs={'charname':form.cleaned_data['char_name'], 'suffix':suffix}))
        except IntegrityError as e:
            context['error'] = "Something went wrong. Try again, or ask a moderator to help you."
            context['error'] = e
    return render(request, 'shibuyasgame/message.html', context)

@login_required
@transaction.atomic
def editChar(request, charname, suffix):
    context = {'you': UserProfile.objects.get(user=request.user),'button':"Save",
        'action':str(reverse('editChar', kwargs={'charname':charname, 'suffix':suffix}))}
    try:
        char = CharProfile.objects.get(char_name=charname, suffix=suffix)
        charstats = CharStats.objects.get(character=char)
        if char.mun != context['you'] :
            context['error']="You don't have permission to access this area."
            return render(request, 'shibuyasgame/message.html', context)
        context['forms'] = [EditCharBase(instance=char), EditCharStats(instance=charstats)]
        if request.method == 'GET':
            return render(request, 'shibuyasgame/form.html', context)
        form1 = EditCharBase(request.POST, instance=char)
        form2 = EditCharStats(request.POST, request.FILES, instance=charstats)
        if form1.is_valid() and form2.is_valid():
            if request.FILES:
                url = s3.s3_upload(form2.cleaned_data['picture'], char.char_name + str(charstats.id))
                form2.pic = url
            form1.save()
            form2.save()
        context['forms'] = [form1, form2]
    except (CharProfile.DoesNotExist or CharStats.DoesNotExist):
        context['error'] = "No such character."
        return render(request, 'shibuyasgame/message.html', context)
    context['success'] = 'Changes made to <a href="'+ str(reverse("cprofile", kwargs={'charname':charname, 'suffix':suffix})) + '">' + charname + "</a> saved."
    return render(request, 'shibuyasgame/message.html', context)

@login_required
@transaction.atomic
def userSettings(request):
    you = UserProfile.objects.get(user=request.user)
    context = {'you':you, 'button':"Save", 'forms':{EditUserForm()},
        'action':str(reverse('settings')), 'contentTitle':"Settings"}
    if request.method != 'GET':
        form = EditUserForm(request.POST, request.FILES, instance=you)
        if not form.is_valid():
            context['forms'] = {form}
        else:
            if request.FILES:
                url = s3.s3_upload(form.cleaned_data['picture'], you.id, True)
                you.pic = url
            if form.cleaned_data['display_name']:
                you.user.first_name = form.cleaned_data['display_name']
                you.user.save()
            you.save()
            context['success'] = "Saved!"
            return render(request, 'shibuyasgame/message.html', context)
    return render(request, 'shibuyasgame/form.html', context)

@login_required
@transaction.atomic
def equip(request, charname, suffix, itemid):
    you = UserProfile.objects.get(user=request.user)
    try:
        char = CharProfile.objects.get(char_name=charname, suffix=suffix)
        charstats = CharStats.objects.get(character=char)
        if char.mun == you or request.user.has_perm('shibuyasgame.is_mod'):
            item = charstats.inventory.filter(id=itemid)[0]
            if item: # Verify you have the goods
                if item.item_type == get_content_type(Pin):
                    pinventory = charstats.inventory.filter(item_type=ContentType.objects.get_for_model(Pin))
                    p_equipped = pinventory.filter(is_equipped=True)
                    if len(p_equipped) < 6:
                        item.is_equipped = True
                        item.save()
                        return JsonResponse({'message':"success"})
                    return JsonResponse({'error':"Can't equip more than 6 pins!"}, status=403)
                elif item.item_type == get_content_type(Thread):
                    tinventory = charstats.inventory.filter(item_type=ContentType.objects.get_for_model(Thread))
                    t_equipped = tinventory.filter(is_equipped=True)
                    if can_equip_thread(t_equipped, item, charstats):
                        item.is_equipped = True
                        item.save()
                        return JsonResponse({'message':"success"})
                    return JsonResponse({'error':"Can't equip more than 4 threads!"}, status=403)
            return JsonResponse({'error':"You don't have this stuff!"}, status=404)
        return JsonResponse({'error':"You don't have permission to do this!"}, status=403)
    except (CharProfile.DoesNotExist or CharStats.DoesNotExist):
        return JsonResponse({'error':"User does not exist!"}, status=404)
    return JsonResponse({'error':"Something went wrong."}, status=500)


@login_required
@transaction.atomic
def dequip(request, charname, suffix, itemid):
    you = UserProfile.objects.get(user=request.user)
    try:
        char = CharProfile.objects.get(char_name=charname, suffix=suffix)
        charstats = CharStats.objects.get(character=char)
        if char.mun == you or request.user.has_perm('shibuyasgame.is_mod'):
            item = charstats.inventory.filter(id=itemid)[0]
            if item: # Verify you have the goods
                if item.is_equipped:
                    item.is_equipped = False
                    item.save()
                    return JsonResponse({'message':"success"})
            return JsonResponse({'error':"You don't have this stuff!"}, status=404)
        return JsonResponse({'error':"You don't have permission to do this!"}, status=403)
    except (CharProfile.DoesNotExist or CharStats.DoesNotExist):
        return JsonResponse({'error':"Character does not exist!"}, status=404)
    return JsonResponse({'error':"Something went wrong."}, status=500)


@login_required
@transaction.atomic
def consumeItem(request, charname, suffix, itemid, quantity):
    you = UserProfile.objects.get(user=request.user)
    quantity = int(quantity)
    try:
        char = CharProfile.objects.get(char_name=charname, suffix=suffix)
        charstats = CharStats.objects.get(character=char)
        if char.mun == you or request.user.has_perm('shibuyasgame.is_mod'):
            item = charstats.inventory.filter(id=itemid)[0]
            if item:
                food = item.item
                if item.item_type == get_content_type(Food) and int(quantity) > 0 and int(quantity) <= item.quantity:
                    charstats.base_hp = charstats.base_hp + food.bonus_hp*quantity
                    charstats.base_atk = charstats.base_atk + food.bonus_atk*quantity
                    charstats.base_def = charstats.base_def + food.bonus_def*quantity
                    thread_stats = calculate_thread_stats(charstats.pronouns, charstats.inventory.filter(item_type=get_content_type(Thread), is_equipped=True))
                    total_hp = thread_stats['hp'] + charstats.base_hp + charstats.misc_hp + food.bonus_hp*quantity
                    if food.heal == -1:
                        charstats.curr_hp = total_hp
                    else:
                        charstats.curr_hp = min(total_hp, charstats.curr_hp + food.heal*quantity)
                    q = item.quantity - quantity
                    if q > 0:
                        item.quantity = q
                        item.save()
                    else: # Destroy object
                        item.delete()
                    charstats.save()
                    return JsonResponse({'success':"success"})
            return JsonResponse({'error':"You don't have a food by this name!"}, status=404)
        return JsonResponse({'error':"You don't have permission to do this!"}, status=403)
    except (CharProfile.DoesNotExist or CharStats.DoesNotExist):
        return JsonResponse({'error':"Character does not exist!"}, status=404)
    return JsonResponse({'error':"Something went wrong."}, status=500)
