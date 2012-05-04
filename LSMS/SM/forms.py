from django import forms
from django.forms.formsets import formset_factory
from django.contrib import auth
from django.core.exceptions import ValidationError
from LSMS.SM.models import *

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36

class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput())
    
    def login(self):
        self.username

class RegisterForm(forms.ModelForm):
    username=forms.CharField(label=_("username"))
    password=forms.CharField(label=_("Password"), widget=forms.PasswordInput())
    password_confirm=forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput())
    email=forms.EmailField()
    user_type=forms.ChoiceField(choices=(('S', 'Student'), ('T', 'Teacher'), ('M', 'Class Manager')))
    internal_id=forms.CharField(required=True)
    
    data_obj={'S':Student, 'T':Teacher, 'M':ClassManager}
    
    class Meta:
        model = User
        fields = ("username","email")
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password_confirm(self):
        password1 = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password_confirm"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("A user with that email already exists."))
    
    def clean_user_type(self):
        usertype=self.cleaned_data["user_type"]
        if usertype not in ('S', 'M', 'T'):
            raise forms.ValidationError(_("Invalid user type."))
        return usertype
    
    def clean_internal_id(self):
        internalid=self.cleaned_data["internal_id"]
        try:
            obj=self.data_obj[self.cleaned_data["user_type"]].objects.get(id=internalid, user__isnull=True)
        except self.data_obj[self.cleaned_data["user_type"]].DoesNotExist:
            raise forms.ValidationError(_("Invalid internal id, or the internal is has been used."))
        return internalid
        
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        profile=Profile()
        data_obj=self.data_obj[self.cleaned_data["user_type"]].objects.get(id=self.cleaned_data["internal_id"])
        user.set_password(self.cleaned_data["password"])
        profile.user_type=self.cleaned_data["user_type"]
        if commit:
            user.save()
            user.groups.add(Group.objects.get(name={'S':'Student', 'T':'Teacher', 'M':'ClassManager'}[self.cleaned_data["user_type"]]))
            profile.user=user
            data_obj.user=user
            profile.save()
            data_obj.save()
        return user

class ClassForm(forms.Form):
    class_name=forms.CharField()
    class_grade=forms.IntegerField()

class StudentForm(forms.Form):
    student_name=forms.CharField()
    gender=forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')))
    birthday=forms.DateField()
    native=forms.CharField()
    student_class=forms.ChoiceField()
    
class EventForm(forms.Form):
    event_description=forms.CharField()
    event_type=forms.ChoiceField()
    event_point=forms.CharField()
    event_date=forms.DateField()
    effect_term=forms.ChoiceField()
    
class NotificationForm(forms.Form):
    notification_title=forms.CharField()
    notification_body=forms.Textarea()
    notification_class=forms.ChoiceField()
    expire_date=forms.DateField()
    
    def bind_classlist(self, ClassList):
        self.fields['notification_class'].choices=ClassList

class GradeForm(forms.Form):
    student_id=forms.CharField()
    student_name=forms.CharField()
    exam_score=forms.IntegerField()
    nonexam_score=forms.IntegerField()
    final_score=forms.IntegerField()
    
    def __init__(self, *args, **kwargs):
        super(GradeForm, self).__init__(*args, **kwargs)
        self.fields['student_id'].widget.attrs['readonly'] = True
        self.fields['student_name'].widget.attrs['disabled'] = True
        self.fields['final_score'].widget.attrs['disabled'] = True

    def clean_student_id(self):
        return self.student_id
    def clean_student_name(self):
        return None
    def clean_final_score(self):
        return None
    

