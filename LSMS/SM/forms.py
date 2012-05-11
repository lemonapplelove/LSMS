#coding: utf-8
from django import forms
from django.forms.models import modelformset_factory, inlineformset_factory
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

#class LoginForm(forms.Form):
#    username=forms.CharField()
#    password=forms.CharField(widget=forms.PasswordInput())
#    
#    def login(self):
#        self.username

class RegisterForm(forms.ModelForm):
    username=forms.CharField(label=_("username"))
    password=forms.CharField(label=_("Password"), widget=forms.PasswordInput())
    password_confirm=forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput())
    email=forms.EmailField()
    user_type=forms.ChoiceField(label='用户类型', choices=(('S', 'Student'), ('T', 'Teacher'), ('M', 'Class Manager')))
    internal_id=forms.CharField(label='学号/教师号', required=True)
    
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
            data_obj_map[self.cleaned_data["user_type"]].objects.get(id=internalid, user__isnull=True)
        except data_obj_map[self.cleaned_data["user_type"]].DoesNotExist:
            raise forms.ValidationError(_("Invalid internal id, or the internal is has been used."))
        return internalid
        
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        profile=Profile()
        data_obj=data_obj_map[self.cleaned_data["user_type"]].objects.get(id=self.cleaned_data["internal_id"])
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

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
    
    def __init__(self, user=None, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        self.fields['class_manager'].initial=ClassManager.objects.get(user=user)
    
    def clean(self):
        c=self.cleaned_data["class_name"]
        g=self.cleaned_data["grade"]
        try:
            Class.objects.get(class_name=c, grade=g)
        except Class.DoesNotExist:
            return self.cleaned_data
        raise forms.ValidationError(_("The class already exists."))

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ('user',)
        
    def __init__(self, user=None, cid=None, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['class_obj'].queryset=Class.objects.filter(class_manager__user=user)
        self.fields['class_obj'].initial=cid
    
    
class EventForm(forms.ModelForm):
    class Meta:
        model = StudentEvent
    
    def __init__(self, user=None, sid=None, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['student'].queryset=Student.objects.filter(class_obj__class_manager__user=user, id=sid)
        self.fields['student'].initial=sid
    
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        exclude = ('release_date',)
    
    def __init__(self, user=None, cid=None, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields['notification_title'].widget.attrs={'size':'91'}
        self.fields['notification_body'].widget=forms.Textarea(attrs={'rows':'20', 'cols':'70'})
        self.fields['class_obj'].queryset=Class.objects.filter(class_manager__user=user)
        self.fields['class_obj'].initial=cid


class GradeForm(forms.ModelForm):
    #student=forms.CharField(widget=forms.HiddenInput())
#    student_display_name=forms.CharField()
    class Meta:
        model=CourseOnStudent
        fields=['exam_score', 'non_exam_score']
        widgets={
            'student':forms.HiddenInput()
        }
    
GradeFormSet = modelformset_factory(CourseOnStudent, form=GradeForm, extra=0)
