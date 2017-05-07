import pytz
from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from timezone_field import TimeZoneField

'''
req_mod is a flag that when set, adds requests involving this item to the
mod queue so that the mods can deal with them
'''

class UserProfile(models.Model):
    ROLES = (
        ('N', "None"),
        ('R', "Reaper"),
        ('O', "Officer"),
        ('TR', "Tutorial Reaper"),
        ('GM', "Game Master"),
        ('CN', "Conductor"),
        ('CM', "Conmposer"),
        ('P', "Producer"),
        ('A', "Accompanist")
    )
    user = models.OneToOneField(User)
    role = models.CharField(max_length=2, default='N', choices=ROLES)
    age = models.CharField(max_length=30, blank=True, null=True)
    bio = models.CharField(max_length=1000, blank=True, null=True)
    loc = models.CharField(max_length=100, blank=True, null=True)
    skype = models.CharField(max_length=100, blank=True, null=True)
    blog = models.CharField(max_length=100, blank=True, null=True)
    timezone = TimeZoneField(default='US/Eastern')
    pic = models.CharField(blank=True, max_length=256)

    is_shopkeep = models.BooleanField(default=False)


class LogEntry(models.Model):
    perp = models.ForeignKey(UserProfile, related_name="log_entries")
    action = models.CharField(max_length=100)
    details = models.CharField(max_length=10000)
    time = models.DateTimeField(auto_now_add=True)

class CharProfile(models.Model):
    mun = models.ForeignKey(UserProfile, related_name="characters")
    suffix = models.CharField(max_length=32, blank=True, null=True) # In case char_name isn't unique
    char_name = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32, blank=True, null=True)
    color = models.CharField(max_length=6, blank=True, null=True)
    week = models.SmallIntegerField()

    def __str__(self):
        return str(self.char_name)


class CharStats(models.Model):
    PRONOUNS = (
        ('M', "He/Him"),
        ('F', 'She/Her'),
        ('N', 'They/Them'),
    )
    character = models.ForeignKey(CharProfile, related_name="stats")
    week = models.SmallIntegerField()
    pic = models.CharField(blank=True, max_length=256)
    pronouns = models.CharField(max_length=1, choices=PRONOUNS)
    partner = models.OneToOneField(CharProfile, related_name="partner", blank=True, null=True)
    role = models.CharField(max_length=32, default="")
    age = models.CharField(max_length=10, blank=True, null=True)
    bio = models.CharField(max_length=1000, blank=True, null=True)
    fee = models.CharField(max_length=1000, blank=True, null=True)
    reason = models.CharField(max_length=1000, blank=True, null=True)
    personality = models.CharField(max_length=1000, blank=True, null=True)
    appearance = models.CharField(max_length=1000, blank=True, null=True)
    yen = models.IntegerField(default=0)
    brv = models.SmallIntegerField(default=10)
    pp = models.SmallIntegerField(default=0)
    sync = models.SmallIntegerField(default=75)
    curr_hp = models.SmallIntegerField(default=500)
    base_hp = models.SmallIntegerField(default=500)
    base_atk = models.SmallIntegerField(default=10)
    base_def = models.SmallIntegerField(default=0)
    misc_hp = models.SmallIntegerField(default=0)
    misc_atk = models.SmallIntegerField(default=0)
    misc_def = models.SmallIntegerField(default=0)

    is_visible = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)



class Pin(models.Model): # Pin is the in-universe name for weapons/spells
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=128)
    atk = models.SmallIntegerField()
    eff = models.CharField(max_length=128)
    brand = models.CharField(max_length=32)
    booster = models.BooleanField(default=False)
    evo = models.ManyToManyField("Pin", blank=True, related_name="evo_from")
    req_mod = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class Thread(models.Model): # Thread is the in-universe name for armor
    CONDITIONS = (
        ('M', "Male"),
        ('F', 'Female'),
        ('N', 'Non-Binary'),
        ('0', 'None'),
    )
    THREAD_TYPES = (
        ('A', "Accessory"),
        ('T', "Top"),
        ('TB', "Top & Bottom"),
        ('B', "Bottom"),
        ('H', "Headwear"),
        ('F', "Footwear"),
        ('M', "Misc")
    )
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=128)
    thread_type = models.CharField(max_length=2, choices=THREAD_TYPES)
    base_hp = models.SmallIntegerField(default=0)
    base_atk = models.SmallIntegerField(default=0)
    base_def = models.SmallIntegerField(default=0)
    eff = models.CharField(max_length=128)
    bonus_condition = models.CharField(max_length=1, choices=CONDITIONS, default='0')
    bonus_hp = models.SmallIntegerField(default=0)
    bonus_atk = models.SmallIntegerField(default=0)
    bonus_def = models.SmallIntegerField(default=0)
    brv = models.PositiveIntegerField(default=10)
    req_mod = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

class Food(models.Model):
    name = models.CharField(max_length=128)
    heal = models.SmallIntegerField(default=0) # Use -1 for a full heal
    bonus_hp = models.SmallIntegerField(default=0)
    bonus_atk = models.SmallIntegerField(default=0)
    bonus_def = models.SmallIntegerField(default=0)
    req_mod = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class Item(models.Model): # Used to keep track of things in inventory
    ITEM_TYPES = (
        ('P', "Pin"),
        ('T', "Thread"),
        ('F', "Food"),
    )
    item_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = GenericForeignKey('item_type', 'item_id')
    quantity = models.IntegerField(default=1)
    is_equipped = models.BooleanField(default=False)
    owner = models.ForeignKey(CharStats, related_name="inventory")

    def __str__(self):
        return str(item_type.get_object_for_this_type(pk=item_id).name)

class TradeRequest(models.Model):
    requester = models.ForeignKey(CharProfile, related_name="trade_giver")
    recipient = models.ForeignKey(CharProfile, related_name="trade_recipient")
    yen = models.PositiveIntegerField(default=0)
    item = models.ForeignKey(Item, null=True, blank=True, related_name="trades")
    request_time = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    text = models.TextField()
    title = models.CharField(max_length=128, blank=True, null=True)
    author = models.ForeignKey(UserProfile, related_name="posts")
    time = models.DateTimeField(auto_now_add=True)

class Shop(models.Model):
    name = models.CharField(max_length=32)
    owners = models.ManyToManyField(UserProfile, related_name="shops")
    max_stock = models.ForeignKey(Item, related_name="where_stock")
    curr_stock = models.ForeignKey(Item, related_name="in_stock")

class ModRequest(models.Model):
    user = models.ForeignKey(UserProfile, related_name="requests")
    text = models.CharField(max_length=128)
    time = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)
    handler = models.ForeignKey(UserProfile, related_name="handled")
