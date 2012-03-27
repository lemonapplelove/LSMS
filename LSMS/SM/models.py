from django.db import models

# Create your models here.

class account(models.Model):
    userTypeCh=(
                ('S', 'student'),
                ('T', 'teacher'),
                ('M', 'class manager')
    )
    userId=models.AutoField(primary_key=True)
    userName=models.CharField(max_length=30)
    userPwd=models.CharField(max_length=128)
    userType=models.CharField(max_length=1, choices=userTypeCh)
    email=models.EmailField()
    roleId=models.IntegerField()
    regDate=models.DateField()
    isDisabled=models.BooleanField(default=False)
    
    
class student(models.Model):
    GENDER=(
            ('M', 'Male'),
            ('F', 'Female')
    )
    stuId=models.AutoField(primary_key=True)
    stuName=models.CharField(max_length=30)
    stuBirth=models.DateField()
    stuGender=models.CharField(max_length=1, choices=GENDER)
    stuNative=models.CharField(max_length=30)
    classId=models.IntegerField()

class teacher(models.Model):
    teaId=models.AutoField(primary_key=True)
    teaName=models.CharField(max_length=30)

class cmanager(models.Model):
    cmId=models.AutoField(primary_key=True)
    cmName=models.CharField(max_length=30)

class cclass(models.Model):
    classId=models.AutoField(primary_key=True)
    className=models.CharField(max_length=50)
    classGrade=models.IntegerField()
    cmId=models.IntegerField()

class stuEvent(models.Model):
    ETYPE=(
           ('A', 'award'),
           ('P', 'punish'),
           ('R', 'record')
    )
    eventId=models.AutoField(primary_key=True)
    eventBody=models.CharField(max_length=200)
    eventType=models.CharField(max_length=1, choices=ETYPE)
    point=models.FloatField(default=0)
    stuId=models.IntegerField()
    eventDate=models.DateField()
    effectTerm=models.IntegerField()

class course(models.Model):
    CTYPE=(
           ('M','mandatory'),
           ('O','optional')
    )
    courseId=models.AutoField(primary_key=True)
    courseTitle=models.CharField(max_length=50)
    courseCredit=models.IntegerField()
    courseType=models.CharField(max_length=1, choices=CTYPE)
    teaId=models.IntegerField()
    examWeight=models.IntegerField()
    
class courseOnStu(models.Model):
    courseId=models.IntegerField()
    stuId=models.IntegerField()
    term=models.IntegerField()
    examScore=models.IntegerField()
    nonExamScore=models.IntegerField()
    finalScore=models.IntegerField()
    
class performance(models.Model):
    acaScore=models.FloatField()
    moralScore=models.FloatField()
    awardScore=models.FloatField()
    finalScore=models.FloatField()
    amRadio=models.IntegerField()
    term=models.IntegerField()
    genDate=models.DateField()
    stuId=models.IntegerField()
    
class notification(models.Model):
    classId=models.IntegerField()
    notiTitle=models.CharField(max_length=200)
    notiBody=models.CharField(max_length=1000)
    notiDate=models.DateField()
    expireDate=models.DateField()
    
    
    
    
