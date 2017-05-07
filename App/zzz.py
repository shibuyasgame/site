### Permissions script

from shibuyasgame import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

# Set up permissions
ct_post = ContentType.objects.get_for_model(models.Post)
ct_prof = ContentType.objects.get_for_model(models.UserProfile)
ct_char = ContentType.objects.get_for_model(models.CharProfile)

# Create permissions
mod, created = Permission.objects.get_or_create(codename="is_mod", name="Gets access to at least some subset of mod tools", content_type=ct_prof)
post_perms, created = Permission.objects.get_or_create(codename='can_post', name='Can make posts', content_type=ct_post)
prof_perms, created = Permission.objects.get_or_create(codename="can_edit_userprofiles", name="Can edit any user profile", content_type=ct_prof)
char_perms, created = Permission.objects.get_or_create(codename="can_edit_charprofiles", name="Can edit any character profile", content_type=ct_char)
perm_perms, created = Permission.objects.get_or_create(codename="can_promote", name="Can promote/demote", content_type=ct_char)
bann_perms, created = Permission.objects.get_or_create(codename="can_ban", name="Can ban/unban people", content_type=ct_prof)

# Get groups
reaper, created = Group.objects.get_or_create(name="Reaper")
accompanist, created = Group.objects.get_or_create(name="Accompanist")
shopkeeper, created = Group.objects.get_or_create(name="Shopkeeper")
composer, created = Group.objects.get_or_create(name="Composer")
conductor, created = Group.objects.get_or_create(name="Conductor")
producer, created = Group.objects.get_or_create(name="Producer")
officer, created = Group.objects.get_or_create(name="Officer")
gm, created = Group.objects.get_or_create(name="Game Master")
tut, created = Group.objects.get_or_create(name="Tutorial Reaper")

# Add permissions to correct groups
composer.permissions.add(mod)
conductor.permissions.add(mod)
producer.permissions.add(mod)
accompanist.permissions.add(mod)
gm.permissions.add(mod)
officer.permissions.add(mod)

accompanist.permissions.add(post_perms)
composer.permissions.add(post_perms)
conductor.permissions.add(post_perms)
producer.permissions.add(post_perms)
gm.permissions.add(post_perms)

accompanist.permissions.add(prof_perms)
composer.permissions.add(prof_perms)
conductor.permissions.add(prof_perms)
producer.permissions.add(prof_perms)
officer.permissions.add(prof_perms)
gm.permissions.add(prof_perms)

accompanist.permissions.add(char_perms)
composer.permissions.add(char_perms)
conductor.permissions.add(char_perms)
producer.permissions.add(char_perms)
officer.permissions.add(char_perms)
gm.permissions.add(char_perms)


composer.permissions.add(perm_perms)
conductor.permissions.add(perm_perms)
producer.permissions.add(perm_perms)

composer.permissions.add(bann_perms)
conductor.permissions.add(bann_perms)
producer.permissions.add(bann_perms)

'''
# Get users
xan = User.objects.get(username='test')

# Add users to groups
xan.groups.remove(gm)
xan.groups.remove(producer)
xan.groups.remove(officer)
xan.groups.add(composer)
'''
