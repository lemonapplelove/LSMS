#coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg,Sum
from django.utils import crypto
from datetime import *
from LSMS.SM.msg import msg
from django.utils.safestring import mark_safe
# Create your models here.

class Profile(models.Model):
    USER_TYPE=(
                ('S', 'Student'),
                ('T', 'Teacher'),
                ('M', 'Class Manager')
    )
    user_type=models.CharField(max_length=1, choices=USER_TYPE)
    user = models.ForeignKey(User, unique=True)
    
    class Meta:
        permissions=(
            ("student", "Permission of student"),
            ("teacher", "Permission of teacher"),
            ("classmanager", "Permission of class manager")
        )
    
    def __unicode__(self):
        return self.user_type

class Teacher(models.Model):
    #TeacherId=models.AutoField(primary_key=True)
    name=models.CharField(max_length=30)
    user = models.ForeignKey(User, unique=True, null=True, blank=True)

    def __unicode__(self):
        return self.name
class ClassManager(models.Model):
    #ClassManagerId=models.AutoField(primary_key=True)
    name=models.CharField(max_length=30)
    user = models.ForeignKey(User, unique=True, null=True, blank=True)
    
    def __unicode__(self):
        return self.name

class Class(models.Model):
    #ClassId=models.AutoField(primary_key=True)
    class_name=models.CharField(max_length=50, verbose_name='班级名称')
    grade=models.IntegerField(verbose_name='年级')
    class_manager=models.ForeignKey(ClassManager, verbose_name='班级管理员')
    
    def __unicode__(self):
        return '%d %s' % (self.grade, self.class_name)
    
class Student(models.Model):
    GENDER=(
            ('M', 'Male'),
            ('F', 'Female')
    )
    #StudentId=models.AutoField(primary_key=True)
    name=models.CharField(max_length=30, verbose_name='学生姓名')
    birth=models.DateField(verbose_name='出生日期')
    gender=models.CharField(max_length=1, choices=GENDER, default='M', verbose_name='性别')
    native=models.CharField(max_length=30, verbose_name='学生籍贯')
    class_obj=models.ForeignKey(Class, verbose_name='班级')
    user = models.ForeignKey(User, unique=True, null=True, blank=True, verbose_name='Student account')
    
    course_filter=None
    
    def __unicode__(self):
        return self.name
    def as_table(self):
        output = u''
        for field in self._meta.fields:
            output += u'<tr><th>%s</th><td>%s</td></tr>' % (
                field.verbose_name, getattr(self, field.name))
        return mark_safe(output)
    
    def set_filter(self, obj, *args, **kwargs):
        if obj=='course': self.course_filter=kwargs
        return self
    
    def records(self):
        return self.studentevent_set.filter(event_type='R')
    def punishments(self):
        return self.studentevent_set.filter(event_type='P')
    def awards(self):
        return self.studentevent_set.filter(event_type='A')
    def courses(self):
        if self.course_filter is None:
            return self.courseonstudent_set.all()
        return self.courseonstudent_set.filter(**self.course_filter)
    def notifications(self):
        return self.class_obj.notification_set.all().order_by('-release_date', 'expire_date', '-id')
    def performances(self):
        return self.performance_set.all()
    def generate_performance(self, term, amr):
        aca=self.courseonstudent_set.filter(term=term, final_score__isnull=False).aggregate(Avg('final_score'))['final_score__avg']
        mor=self.studentevent_set.filter(effect_term=term, event_type='R', point__gt=0).aggregate(Avg('point'))['point__avg']
        awd=self.studentevent_set.filter(effect_term=term, event_type='A').aggregate(Sum('point'))['point__sum']
        pns=self.studentevent_set.filter(effect_term=term, event_type='P').aggregate(Sum('point'))['point__sum']
        if aca is None: aca=0
        if mor is None: mor=0
        if awd is None: awd=0
        if pns is None: pns=0
        aca, mor, awd, pns = aca*100, mor*100, awd*100, pns*100
        fin=(aca*amr+mor*(100-amr))/100+awd-pns
        try:
            p=Performance.objects.get(student=self, term=term)
        except Performance.DoesNotExist:
            p=Performance()
        p.student=self
        p.academic_score=aca
        p.moral_score=mor
        p.award_score=awd-pns
        p.aca_mor_ratio=amr
        p.final_score=fin
        p.term=term
        p.generated_date=date.today()
        p.save()


class StudentEvent(models.Model):
    EVENT_TYPE=(
           ('A', 'Award'),
           ('P', 'Punishment'),
           ('R', 'Record')
    )
    #EventId=models.AutoField(primary_key=True)
    event_body=models.CharField(max_length=200, verbose_name='事件描述')
    event_type=models.CharField(max_length=1, choices=EVENT_TYPE, default='R', verbose_name='事件类型')
    point=models.IntegerField(default=0, verbose_name='事件得分')
    student=models.ForeignKey(Student, verbose_name='学生')
    event_date=models.DateField(verbose_name='事件日期')
    effect_term=models.IntegerField(verbose_name='有效学期')
    
    def __unicode__(self):
        return self.event_body
    def table_title(self):
        output = u'<tr>'
        for field in self._meta.fields:
            if field.name not in ['id', 'student','event_type']:
                output += u'<th>%s</th>' % field.verbose_name
        output += u'</tr>'
        return mark_safe(output)
    def put_row(self):
        output = u'<tr>'
        for field in self._meta.fields:
            if field.name not in ['id', 'student','event_type']:
                output += u'<td>%s</td>' % getattr(self, field.name)
        output += u'</tr>'
        return mark_safe(output)

class Course(models.Model):
    COURSE_TYPE=(
           ('M','Mandatory'),
           ('O','Optional')
    )
    #CourseId=models.AutoField(primary_key=True)
    course_title=models.CharField(max_length=50)
    credit=models.IntegerField()
    course_type=models.CharField(max_length=1, choices=COURSE_TYPE)
    teacher=models.ForeignKey(Teacher)
    exam_weight=models.IntegerField()
    
    def __unicode__(self):
        return self.course_title
    
    
class CourseOnStudent(models.Model):
    course=models.ForeignKey(Course)
    student=models.ForeignKey(Student)
    term=models.IntegerField()
    exam_score=models.IntegerField(null=True, blank=True)
    non_exam_score=models.IntegerField(null=True, blank=True)
    final_score=models.IntegerField(null=True, blank=True)
    
    def put_row(self):
        output = u'<tr>'
        for field in self._meta.fields:
            if field.name not in ['student']:
                output += u'<td>%s</td>' % getattr(self, field.name)
        output += u'</tr>'
        return mark_safe(output)
    
class Performance(models.Model):
    academic_score=models.IntegerField()
    moral_score=models.IntegerField()
    award_score=models.IntegerField()
    final_score=models.IntegerField()
    aca_mor_ratio=models.IntegerField()
    term=models.IntegerField()
    generated_date=models.DateField()
    student=models.ForeignKey(Student)
    
    def table_title(self):
        output = u'<tr>'
        for field in self._meta.fields:
            if field.name not in ['student']:
                output += u'<th>%s</th>' % field.verbose_name
        output += u'</tr>'
        return mark_safe(output)
    def put_row(self):
        output = u'<tr>'
        for field in self._meta.fields:
            if field.name not in ['student']:
                output += u'<td>%s</td>' % getattr(self, field.name)
        output += u'</tr>'
        return mark_safe(output)
    
class Notification(models.Model):
    notification_title=models.CharField(max_length=200, verbose_name='通知标题')
    notification_body=models.CharField(max_length=1000, verbose_name='通知内容')
    class_obj=models.ForeignKey(Class, verbose_name='通知班级')
    release_date=models.DateField(default=date.today)
    expire_date=models.DateField(verbose_name='截止日期')
    
data_obj_map={'S':Student, 'T':Teacher, 'M':ClassManager}
    
    
