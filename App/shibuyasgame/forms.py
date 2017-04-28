from django import forms

from shibuyasgame.models import *
import re

MAX_UPLOAD_SIZE = 2500000

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=32, label="Username", required=True)
    first_name=forms.CharField(max_length=32, label="Display Name", required=True)
    password=forms.CharField(widget=forms.PasswordInput())
    confirm_pass=forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password']

    def clean_confirm_pass(self):
        password = self.cleaned_data.get("password")
        confirm_pass = self.cleaned_data.get("confirm_pass")
        if password != confirm_pass:
            raise forms.ValidationError("Password and Confirm Password do not match.")
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email):
            raise forms.ValidationError("This email is already in use.")
        return email

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'required':True, 'placeholder':"Title"}), max_length=160)
    text = forms.CharField(widget=forms.Textarea(attrs={'required':True, 'placeholder':"10,000 Character Limit. Ask webmaster to raise the cap."}), max_length=10000)
    class Meta:
        model = Post
        fields = ['title', 'text']

    def clean_title(self):
        t = self.cleaned_data['title']
        if t:
            return t
        return self.instance.title

    def clean_text(self):
        t = self.cleaned_data['text']
        if t:
            return t
        return self.instance.text

class CreateCharForm(forms.ModelForm):
    char_name = forms.CharField(label="Chat Name", required=True, widget=forms.TextInput(attrs={'placeholder':'Name used in chat'}), max_length=32)
    first_name = forms.CharField(label="First Name", required=True, max_length=32)
    last_name = forms.CharField(label="Last Name", required=False, widget=forms.TextInput(attrs={'placeholder':'Optional'}), max_length=32)
    color = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':"Hex code. Optional."}), max_length=7)
    class Meta:
        model = CharProfile
        fields = ['char_name', 'first_name', 'last_name', 'color']

    def clean_color(self):
        c = self.cleaned_data['color']
        if c:
            if c[0] == '#':
                c = c[1:]
            match = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', c)
            if not match:
                raise forms.ValidationError("Please input a valid hexcode.")
        return c


class CreateCharStatsForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'required':True, 'placeholder':"1,000 character limit"}), max_length=1000)
    appearance = forms.CharField(widget=forms.Textarea(attrs={'required':True, 'placeholder':"1,000 character limit"}), max_length=1000)
    fee = forms.CharField(required=True, label="Entry Fee")
    reason = forms.CharField(required=True, label="Reason for 2nd Chance")
    personality = forms.CharField(required=True)
    age = forms.CharField(required=True)
    class Meta:
        model = CharStats
        fields = ['pronouns', 'age', 'bio', 'fee', 'reason', 'appearance', 'personality']


class EditUserForm(forms.ModelForm):
    display_name = forms.CharField(max_length=32, required=False)
    bio = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)
    loc = forms.CharField(label="Location", max_length=100, required=False)
    skype = forms.CharField(max_length=100, required=False)
    blog = forms.CharField(max_length=100, required=False)
    timezone = forms.CharField(max_length=100, required=False)
    picture = forms.FileField(required=False)
    class Meta:
        model = UserProfile
        fields = ['display_name', 'bio', 'loc', 'skype', 'blog', 'timezone', 'picture']

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if picture:
            if not picture.content_type or not picture.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            if picture.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

    def clean_age(self):
        age = self.cleaned_data['age']
        if age:
            return age
        else:
            return self.instance.age

    def clean_bio(self):
        bio = self.cleaned_data['bio']
        if bio:
            return bio
        else:
            return self.instance.bio

    def clean_loc(self):
        loc = self.cleaned_data['loc']
        if loc:
            return loc
        else:
            return self.instance.loc

    def clean_skype(self):
        skype = self.cleaned_data['skype']
        if skype:
            return skype
        else:
            return self.instance.skype

    def clean_blog(self):
        blog = self.cleaned_data['blog']
        if blog:
            return blog
        else:
            return self.instance.blog

    def clean_timezone(self):
        timezone = self.cleaned_data['timezone']
        if timezone:
            return timezone
        else:
            return self.instance.timezone

class AdminUserForm(forms.ModelForm):
    CHOICES = (
        ('L', "No Change"),
        ('Y', "Yes"),
        ('N', "No")
    )
    ROLES = (
        ('L', "No Change"),
        ('N', "None"),
        ('R', "Reaper"),
        ('O', "Officer"),
        ('TR', "Tutorial Reaper"),
        ('GM', "Game Master"),
        ('CN', "Conductor"),
        ('CM', "Composer"),
        ('P', "Producer"),
        ('A', "Accompanist")
    )
    role = forms.ChoiceField(choices=ROLES)
    shopkeeper = forms.ChoiceField(initial='L', choices=CHOICES)
    class Meta:
        model = UserProfile
        fields = ['role', 'shopkeeper']

    def clean_role(self):
        r = self.cleaned_data['role']
        if r:
            return r
        return 'L'

    def clean_shopkeeper(self):
        shop = self.cleaned_data['shopkeeper']
        if shop:
            return shop
        return 'L'

class BanHammer(forms.Form):
    CHOICES = (
        ('L', "No Change"),
        ('Y', "Yes"),
        ('U', "Unban"),
    )
    ban = forms.ChoiceField(label="Ban?", initial='L', choices=CHOICES)

    def clean_ban(self):
        b = self.cleaned_data['ban']
        if b:
            return b
        return 'L'

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=True)

    def clean_search(self):
        return self.cleaned_data['search']


class EditCharBase(forms.ModelForm):
    char_name = forms.CharField(max_length=32, label="Chat Name", required=False)
    first_name = forms.CharField(max_length=32, label="First Name", required=False)
    last_name = forms.CharField(max_length=32, label="Last Name", required=False)
    color = forms.CharField(required=False, max_length=7)
    class Meta:
        model = CharProfile
        fields = ['char_name', 'first_name', 'last_name', 'color']

    def clean_char_name(self):
        n = self.cleaned_data['char_name']
        if n:
            return n
        return self.instance.char_name
    def clean_first_name(self):
        f = self.cleaned_data['first_name']
        if f:
            return f
        return self.instance.first_name
    def clean_last_name(self):
        l = self.cleaned_data['last_name']
        if l:
            return l
        return self.instance.last_name
    def clean_color(self):
        c = self.cleaned_data['color']
        if c:
            if c[0] == '#':
                c = c[1:]
            match = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', c)
            if not match:
                raise forms.ValidationError("Please input a valid hexcode.")
            return c
        return self.instance.color

class EditCharStats(forms.ModelForm):
    picture = forms.FileField(required=False)
    class Meta:
        model = CharStats
        fields = ['week', 'picture', 'pronouns', 'partner', 'role', 'age',
            'bio', 'fee', 'reason', 'personality', 'appearance']
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if picture:
            if not picture.content_type or not picture.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            if picture.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

class AdminEditCharStats(forms.ModelForm):
    class Meta:
        model = CharStats
        fields = ['yen', 'brv', 'pp', 'sync', 'curr_hp', 'base_hp', 'base_atk',
            'base_def', 'misc_hp', 'misc_atk', 'misc_def']



###### Items
class ItemFForm(forms.ModelForm):
    item =forms.ModelChoiceField(queryset=Food.objects.all())
    class Meta:
        model = Item
        fields = ['quantity']

class ItemPForm(forms.ModelForm):
    item =forms.ModelChoiceField(queryset=Pin.objects.all())
    class Meta:
        model = Item
        fields = ['is_equipped']

class ItemTForm(forms.ModelForm):
    item =forms.ModelChoiceField(queryset=Thread.objects.all())
    class Meta:
        model = Item
        fields = ['is_equipped']

class DeleteFForm(forms.ModelForm):
    item =forms.ModelChoiceField(queryset=Food.objects.all())
    class Meta:
        model = Item
        fields = ['quantity']

class DeletePForm(forms.ModelForm):
    item =forms.ModelChoiceField(queryset=Pin.objects.all())
    class Meta:
        model = Item
        fields = ['is_equipped']

class DeleteTForm(forms.ModelForm):
    item =forms.ModelChoiceField(queryset=Thread.objects.all())
    class Meta:
        model = Item
        fields = ['is_equipped']


class PinForm(forms.ModelForm):
    class Meta:
        model = Pin
        fields = ['code', 'name', 'atk', 'eff', 'req_mod']

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['code', 'name', 'thread_type', 'base_hp', 'base_atk', 'base_def',
            'eff', 'bonus_condition', 'bonus_hp', 'bonus_atk', 'bonus_def', 'brv', 'req_mod']

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'heal', 'bonus_hp', 'bonus_atk', 'bonus_def', 'req_mod']
