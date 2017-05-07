import os
import configparser
import datetime
import django.utils.dateparse as dateparse
from shibuyasgame.models import *
from shibuyasgame.forms import *
from django.contrib.auth.models import User, Group, Permission

from webapps.settings import BASE_DIR
config = configparser.ConfigParser()

# Get information that might change
def getWebmaster():
    return config.get('WEEK', 'Webmaster')

def getWeek():
    config.read(os.path.join(BASE_DIR, 'config.ini'))
    return config.get('WEEK', 'Week')

# Time things
def formatTime(utc_time, user=None, timezone="US/Eastern"):
    d = utc_time.strftime('%Y-%m-%d<br>%H:%M:%S')
    return d

# Checks
def checkUser(request):
    return not request.user.is_anonymous() and request.user.is_authenticated()

# Letter > Term
def translatePronouns(char):
    if char == 'M':
        return "He/Him"
    if char == 'F':
        return "She/Her"
    if char == 'N':
        return "They/Them"

def translateGroup(groupCode):
    if groupCode == 'R':
        return "Reaper"
    if groupCode == 'CM':
        return "Composer"
    if groupCode == 'CN':
        return "Conductor"
    if groupCode == 'P':
        return "Producer"
    if groupCode == 'O':
        return "Officer"
    if groupCode == 'TR':
        return "Tutorial Reaper"
    if groupCode == 'GM':
        return "Game Master"
    if groupCode == 'A':
        return "Accompanist"
    if groupCode == 'S':
        return "Shopkeeper"
    return None

def translateGroupEX(groupCode):
    if groupCode == "L":
        return "No change"
    if groupCode =="N":
        return "None"
    return translateGroup(groupCode)

# Permission group shenanigans
def getGroup(groupCode):
    key = translateGroup(groupCode)
    if key:
        return Group.objects.get(name=key)
    return None

def addToGroup(user, groupCode):
    group = getGroup(groupCode)
    #user = User.objects.get(username=username)
    if group and user:
        user.groups.add(group)
        user.save()

def removeFromGroup(user, groupCode):
    group = getGroup(groupCode)
    #user = User.objects.get(username=username)
    if group and user:
        user.groups.remove(group)
        user.save()

def changeGroup(user, to_remove, to_add):
    if to_remove != to_add:
        removeFromGroup(user, to_remove)
        if to_add != 'N':
            addToGroup(user, to_add)
        return "Changed groups from " + translateGroupEX(to_remove) + " to " + translateGroupEX(to_add) + ". "
    return "User remained in same group. "

# Item helpers
def itemForms(item_type):
    if item_type == "pin":
        return PinForm()
    if item_type == "thread":
        return ThreadForm()
    if item_type == "food":
        return FoodForm()
    return None

def get_content_type(ct):
    return ContentType.objects.get_for_model(ct)

def can_equip_thread(equipped, thread, character):
    if character.brv < thread.item.brv or len(equipped) > 3:
        return False
    thread_type = thread.item.thread_type
    threads = Thread.objects.filter(thread_type = thread_type)
    if equipped.filter(item_id__in=threads):
        return False
    return True

def calculate_thread_stats(prn, threads):
    hp_val = 0
    atk_val = 0
    def_val = 0
    if threads:
        for thread in threads:
            hp_val = hp_val + thread.item.base_hp
            atk_val = atk_val + thread.item.base_atk
            def_val = def_val + thread.item.base_def
            if thread.item.bonus_condition == prn:
                hp_val = hp_val + thread.item.bonus_hp
                atk_val = atk_val + thread.item.bonus_atk
                def_val = def_val + thread.item.bonus_def
    return {'hp':hp_val, 'atk':atk_val, 'def':def_val}
