from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core import serializers
from django.http import HttpResponse, Http404
# Decorator to use built-in authentication system
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.serializers.json import DjangoJSONEncoder

from shibuyasgame.models import *
from shibuyasgame.forms import *
from shibuyasgame.helpers import *
import shibuyasgame.s3 as s3
import time
import datetime
import json


def getServerTime(request):
    response_text = json.dumps(formatTime(datetime.datetime.now()), cls=DjangoJSONEncoder)
    return HttpResponse(response_text, content_type='application/json')

def getInventory(request, charname, suffix):
    char = get_object_or_404(CharProfile, char_name=charname, suffix=suffix)
    charstats = get_object_or_404(CharStats, character=char)
    items = charstats.inventory
    response_text = serializers.serialize('json', items)
    return HttpResponse(response_text, content_type='application/json')
