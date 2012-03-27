from django.db import models

class account(models.Model):
    userTypeCh=(
                ('S', 'student'),
                ('T', 'teacher'),
                ('M', 'class manager')
    )
    userId=models.AutoField()
    userName=models.CharField(maxlenth=30)
    userType=models.CharField(maxlenth=1, choices=userTypeCh)
    email=models.EmailField()
    roleId=models.IntegerField()
    regDate=models.DateField()
    isDisabled=models.BooleanField(default=False)
    
class student(models.Model):
    GENDER=(
            ('M', 'Male'),
            ('F', 'Female')
    )
    stuId=models.AutoField()
    stuName=models.CharField(maxlenth=30)
    stuBirth=models.DateField()
    stuGender=models.CharField(maxlenth=1, choices=GENDER)
    stuNative=models.CharField(maxlenth=30)
    classId=models.IntegerField()

class teacher(models.Model):
    teaId=models.AutoField()
    teaName=models.CharField(maxlenth=30)

class cmanager(models.Model):
    cmId=models.AutoField()
    cmName=models.CharField(maxlenth=30)

class cclass(models.Model):
    classId=models.AutoField()
    className=models.CharField(maxlenth=50)
    classGrade=models.IntegerField()
    cmId=models.IntegerField()

class stuEvent(models.Model):
    ETYPE=(
           ('A', 'award'),
           ('P', 'punish'),
           ('R', 'record')
    )
    eventId=models.AutoField()
    eventBody=models.CharField(maxlenth=200)
    eventType=models.CharField(maxlenth=1, choices=ETYPE)
    point=models.FloatField(default=0)
    stuId=models.IntegerField()
    eventDate=models.DateField()
    expireDate=models.DateField()

