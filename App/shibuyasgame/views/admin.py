from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core import serializers
from django.http import HttpResponse, Http404, HttpResponseForbidden
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


# Admin things
@login_required
def viewLogs(request):
    if not request.user.has_perm('shibuyasgame.can_post'):
        raise PermissionDenied
    log = LogEntry.objects.get.all()  #TODO limit log to like 100 items or something
    return render(request, 'shibuyasgame/log.html', {'you':UserProfile.objects.get(user=request.user), 'log':log})

@login_required
def post(request):
    context = {'you':UserProfile.objects.get(user=request.user),
        'action':str(reverse('post')), 'button':'Post'}
    if not request.user.has_perm('shibuyasgame.can_post'): # Don't let unauthorized people post
        raise PermissionDenied
    form = PostForm()
    if request.method != 'GET':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = Post(title=form.cleaned_data['title'],
                            text=form.cleaned_data['text'],
                            author=UserProfile.objects.get(user=request.user))
            new_post.save()
            return redirect('home')
    context['forms'] = {form}
    return render(request, 'shibuyasgame/form.html', context)

@login_required
@transaction.atomic
def editPost(request, pid):
    context = {'you':UserProfile.objects.get(user=request.user), 'button':"Save",
        'action':str(reverse("editPost", kwargs={"pid":pid}))}
    if not request.user.has_perm("shibuyasgame.can_post"):
        raise PermissionDenied
    post = Post.objects.get_object_or_404(id=pid)
    if request.method == 'GET':
        context['forms'] = {PostForm(initial={'title':post.title, 'text':post.text})}
        return render(request, 'shibuyasgame/form.html', context)
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
    return redirect(reverse('viewPost', kwargs={'pid':pid}))

@login_required
@transaction.atomic
def approve(request, charname, suffix):
    context = {'you':UserProfile.objects.get(user=request.user)}
    if not request.user.has_perm('shibuyasgame.is_mod'):
        raise PermissionDenied
    char = get_object_or_404(CharProfile, char_name=charname, suffix=suffix)
    charstats = get_object_or_404(CharStats, character=char)
    charstats.is_visible = True
    charstats.is_active = True
    charstats.is_approved = True
    charstats.save();
    context['success'] = '<a href="'+str(reverse("cprofile", kwargs={'charname':charname, 'suffix':suffix}))+ '">' + charname + "</a> approved."
    return render(request, 'shibuyasgame/message.html', context)

@login_required
@transaction.atomic
def adminEditChar(request, charname, suffix):
    context = {'you': UserProfile.objects.get(user=request.user),'button':"Save",
        'action':str(reverse('adminEditChar', kwargs={'charname':charname, 'suffix':suffix}))}
    if not request.user.has_perm('shibuyasgame.can_edit_charprofiles'):
        raise PermissionDenied
    char = get_object_or_404(CharProfile, char_name=charname, suffix=suffix)
    charstats = get_object_or_404(CharStats, character=char)
    context['forms'] = [EditCharBase(instance=char), EditCharStats(instance=charstats),
        AdminEditCharStats(instance=charstats)]
    if request.method == 'GET':
        return render(request, 'shibuyasgame/form.html', context)
    form1 = EditCharBase(request.POST, instance=char)
    form2 = EditCharStats(request.POST, request.FILES, instance=charstats)
    form3 = AdminEditCharStats(request.POST, instance=charstats)
    if form1.is_valid() and form2.is_valid() and form3.is_valid():
        if request.FILES:
            url = s3.s3_upload(form2.cleaned_data['picture'], char.char_name + charstats.id)
            form2.pic = url
        form1.save()
        form2.save()
        form3.save()
    context['forms'] = [form1, form2, form3]
    context['success'] = 'Changes made to <a href="'+ str(reverse("cprofile", kwargs={'charname':charname, 'suffix':suffix})) + '">' + charname + "</a> saved."
    return render(request, 'shibuyasgame/message.html', context)

@login_required
@transaction.atomic
def adminEditUser(request, username):
    you = UserProfile.objects.get(user=request.user)
    promote = request.user.has_perm('shibuyasgame.can_promote')
    ban = request.user.has_perm('shibuyasgame.can_ban')
    if not request.user.has_perm('shibuyasgame.can_edit_userprofiles'):
        raise PermissionDenied
    user = User.objects.get_object_or_404(username=username)
    profile = UserProfile.objects.get_object_or_404(user=user)
    context = {'you':you, 'button':"Save", 'forms':[EditUserForm()],
        'action':str(reverse('adminEditUser', kwargs={'username':username})),
        'contentTitle':'Editing <a href="%s">%s</a>\'s Profile'%(str(reverse('uprofile', kwargs={'username':username})), user.first_name)}
    if promote:
        context['forms'].append(AdminUserForm())
    if ban:
        context['forms'].append(BanHammer())

    if request.method != 'GET':
        old_role = profile.role
        form = EditUserForm(request.POST, request.FILES, instance=profile)
        form1 = AdminUserForm(request.POST, instance=profile)
        form2 = BanHammer(request.POST)
        if not form.is_valid() or not form1.is_valid() or not form2.is_valid():
            forms = [form]
            if promote:
                forms.append(form1)
            if ban:
                forms.append(form2)
            context['forms'] = forms
        else:
            context['success'] = ""
            context['error'] = ""
            if request.FILES:
                url = s3.s3_upload(form.cleaned_data['picture'], profile.id, True)
                profile.pic = url
            if form.cleaned_data['display_name']:
                user.first_name = form.cleaned_data['display_name']
                user.save()
            if promote:
                if form1.cleaned_data['role'] != 'L':
                    role = form1.cleaned_data['role']
                    context['success'] = context['success'] + changeGroup(user, old_role, role)
                if form1.cleaned_data['shopkeeper'] == 'Y':
                    profile.is_shopkeep = True
                    context['success'] = context['success'] + user.username + ' is now shopkeeper. '
                elif form1.cleaned_data['shopkeeper'] == 'N':
                    profile.is_shopkeep = False
                    context['error'] = context['error'] + user.username + ' is no longer shopkeeper. '
                form1.save()

            if ban:
                if form2.cleaned_data['ban'] == 'Y':
                    user.is_active = False
                    context['error'] = context['error'] + "Banned " + user.username
                elif form2.cleaned_data['ban'] == 'U':
                    user.is_active = True
                    context['success'] = context['success'] + "Unbanned " + user.username
            user.save()
            form.save()
            context['success'] = context['success'] + "Saved!"
            return render(request, 'shibuyasgame/message.html', context)
    return render(request, 'shibuyasgame/form.html', context)

@login_required
def adminEditHome(request):
    context = {'you': UserProfile.objects.get(user=request.user),
        'message': "Not yet implemented, oops!"}
    return render(request, 'shibuyasgame/form.html', context)

@login_required
@transaction.atomic
def createItem(request, item_type):
    context = {'you':UserProfile.objects.get(user=request.user), 'button':"Create",
        'contentTitle':item_type, 'action':str(reverse('createItem', kwargs={'item_type':item_type}))}
    if not request.user.has_perm("shibuyasgame.is_mod"):
        raise PermissionDenied
    form = itemForms(item_type)
    if not form:
        raise Http404
    if request.method == 'GET':
        context['forms'] = {form}
        return render(request, 'shibuyasgame/form.html', context)
    item = None
    if item_type == "pin":
        item = Pin()
        form = PinForm(request.POST, instance=item)
    elif item_type == "thread":
        item = Thread()
        form = ThreadForm(request.POST, instance=item)
    elif item_type == "food":
        item = Food()
        form = FoodForm(request.POST, instance=item)
    else:
        raise Http404
    if form.is_valid():
        item.save()
        context['message'] = "Created " + form.cleaned_data['name']
        return render(request, 'shibuyasgame/message.html', context)
    context['forms'] = {form}
    return render(request, 'shibuyasgame/form.html', context)

@login_required
@transaction.atomic
def addToInventory(request, charname, suffix, itemtype):
    if not request.user.has_perm('shibuyasgame.can_edit_charprofiles'):
        return HttpResponseForbidden()
    you = UserProfile.get(user=request.user)
    context = {'you':you, 'button':"Add",'action':str(reverse('addItem',
        kwargs={'charname':charname, 'suffix':suffix, 'itemtype':itemtype}))}
    char = get_object_or_404(CharProfile, char_name=charname, suffix=suffix)
    charstats = get_object_or_404(CharStats, character=char)
    form = None
    itype = None
    if itemtype == "f":
        context['contentTitle'] = "Add Food"
        form = ItemFForm()
        itype = ContentType.objects.get_for_model(Food)
    elif itemtype == "p":
        context['contentTitle'] = "Add Pin"
        form = ItemPForm()
        itype = ContentType.objects.get_for_model(Pin)
    elif itemtype == "t":
        context['contentTitle'] = "Add Thread"
        form = ItemTForm()
        itype = ContentType.objects.get_for_model(Thread)
    else:
        raise Http404
    if request.method != 'GET':
        if itemtype == "f":
            form = ItemFForm(request.POST)
        elif itemtype == "p":
            form = ItemPForm(request.POST)
        elif itemtype == "t":
            form = ItemTForm(request.POST)
        if form.is_valid():
            q = 1
            if 'quantity' in form.cleaned_data:
                q = form.cleaned_data['quantity']
            equipped = False
            if 'is_equipped' in form.cleaned_data:
                equipped = form.cleaned_data['is_equipped']

            newitem = True
            itemname = form.cleaned_data['item']
            log = LogEntry(perp=you, action="AddItemAttempt", details="Attempted to add %s to <a href=\"%s\">%s</a>'s inventory." % (itemname, charname, str(reverse('cprofile', kwargs={'char_name':charname, 'suffix':suffix}))))
            if itemtype == 'f':
                f = Item.objects.filter(owner=charstats, item_type=itype, item_id=int(form.cleaned_data['item'].id))
                item = f.first()
                if item:
                    item.quantity = item.quantity + q
                    item.save()
                    newitem = False
            if newitem: #check to see if an entry is already there
                item = Item(item_type = itype,
                            item_id = form.cleaned_data['item'].id,
                            item = form.cleaned_data['item'],
                            owner = charstats,
                            quantity = q,
                            is_equipped = equipped)
                item.save()
            log.save()
            return redirect(reverse('cprofile', kwargs={'charname':charname, 'suffix':suffix}))
    context['forms'] = {form}
    return render(request, 'shibuyasgame/form.html', context)

@login_required
@transaction.atomic
def deleteFromInventory(request, charname, suffix, itemtype):
    if not request.user.has_perm('shibuyasgame.can_edit_charprofiles'):
        return HttpResponseForbidden()
    context = {'you':UserProfile.objects.get(user=request.user), 'button':"Add",
    'action':str(reverse('removeItem', kwargs={'charname':charname, 'suffix':suffix, 'itemtype':itemtype}))}
    char = get_object_or_404(CharProfile, char_name=charname, suffix=suffix)
    charstats = get_object_or_404(CharStats, character=char)
    form = DeleteItemForm(charstats, itemtype)
    if request.method != 'GET':
        form = DeleteItemForm(request.POST)
        if form.is_valid():
            if 'item' in form.cleaned_data:
                form.cleaned_data['item'].delete()
            return redirect(reverse('cprofile', kwargs={'charname':charname, 'suffix':suffix}))
    context['forms'] = {form}
    return render(request, 'shibuyasgame/form.html', context)
