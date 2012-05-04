from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg,Sum
from django.utils import crypto
import datetime
from LSMS.SM.msg import msg
# Create your models here.

class Profile(models.Model):
    USER_TYPE=(
                ('S', 'Student'),
                ('T', 'Teacher'),
                ('M', 'Class Manager')
    )
    user_type=models.CharField(max_length=1, choices=USER_TYPE)
    user = models.ForeignKey(User, unique=True)
    
    def __unicode__(self):
        return self.user_type

class Teacher(models.Model):
    #TeacherId=models.AutoField(primary_key=True)
    teacher_name=models.CharField(max_length=30)
    user = models.ForeignKey(User, unique=True, null=True)

class ClassManager(models.Model):
    #ClassManagerId=models.AutoField(primary_key=True)
    classmanager_name=models.CharField(max_length=30)
    user = models.ForeignKey(User, unique=True, null=True)

class Class(models.Model):
    #ClassId=models.AutoField(primary_key=True)
    class_name=models.CharField(max_length=50)
    grade=models.IntegerField()
    class_manager=models.ForeignKey(ClassManager)
    
class Student(models.Model):
    GENDER=(
            ('M', 'Male'),
            ('F', 'Female')
    )
    #StudentId=models.AutoField(primary_key=True)
    student_name=models.CharField(max_length=30)
    birth=models.DateField()
    gender=models.CharField(max_length=1, choices=GENDER)
    native=models.CharField(max_length=30)
    class_obj=models.ForeignKey(Class)
    user = models.ForeignKey(User, unique=True, null=True)

class StudentEvent(models.Model):
    EVENT_TYPE=(
           ('A', 'Award'),
           ('P', 'Punishment'),
           ('R', 'Record')
    )
    #EventId=models.AutoField(primary_key=True)
    event_body=models.CharField(max_length=200)
    event_type=models.CharField(max_length=1, choices=EVENT_TYPE)
    point=models.FloatField(default=0)
    student=models.ForeignKey(Student)
    event_date=models.DateField()
    effect_term=models.IntegerField()

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
    
    
class CourseOnStu(models.Model):
    course=models.ForeignKey(Course)
    student=models.ForeignKey(Student)
    term=models.IntegerField()
    exam_score=models.IntegerField()
    non_exam_score=models.IntegerField()
    final_score=models.IntegerField()
    
class Performance(models.Model):
    academic_score=models.IntegerField()
    moral_score=models.IntegerField()
    award_score=models.IntegerField()
    final_score=models.IntegerField()
    aca_mor_ratio=models.IntegerField()
    term=models.IntegerField()
    generated_date=models.DateField()
    student=models.ForeignKey(Student)
    
class Notification(models.Model):
    class_obj=models.ForeignKey(Class)
    notification_title=models.CharField(max_length=200)
    notification_body=models.CharField(max_length=1000)
    release_date=models.DateField()
    expire_date=models.DateField()
    
    
    
    
