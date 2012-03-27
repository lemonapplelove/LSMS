from LSMS.SM.models import *
import datetime
from django.db.models import Avg,Sum
from django.utils import crypto


#user control functions:
def encrypt(username, password):
    return crypto.salted_hmac(username, password).hexdigest()

def auth(username, password):
    u=account.objects.filter(userName=username, userPwd=encrypt(username,password))
    if u.count()==0:
        return {'auth_state':'failed'}
    elif u[0].isDisabled:
        return {'auth_state':'disabled'}
    else:
        return{'auth_state':'success',
               'user_object':u[0]
        }
def getuinfo(request):
    uid=request.session.get('uid',False)
    if not uid:
        return {'state':'not logon'}
    elif account.objects.get(userId=uid).isDisabled==True:
        return {'state':'disabled'}
    else:
        return {'state':'ok','uid':request.session['uid'],'uname':request.session['uname'],'email':request.session['email'],'utype':request.session['utype'],'rid':request.session['rid']}
def reg(utype, uname, upass, uemail, rid):
    if utype!='S' and utype!='T' and utype!='M':
        return 'Please select a right user type!'
    if len(rid)==0:
        return 'Please enter a Student/Teacher/Class Manager Id!'
    if len(uname)==0:
        return 'Please enter a username!'
    if account.objects.filter(userType=utype, roleId=rid).count()!=0:
        return 'You have already registered!'
    if utype=='S' and student.objects.filter(stuId=rid).count()==0:
        return 'Invalid student number!'
    if utype=='T' and teacher.objects.filter(teaId=rid).count()==0:
        return 'Invalid teacher number!'
    if utype=='M' and cmanager.objects.filter(cmId=rid).count()==0:
        return 'Invalid class manager number!'
    if len(upass)<6:
        return 'Password must have 6 or more characters!'
    if account.objects.filter(userName=uname).count()!=0:
        return 'The username is already used by other user!'
    if account.objects.filter(email=uemail).count()!=0:
        return 'The email address is already used by other user!'
    r=account(userName=uname,userPwd=encrypt(uname,upass),userType=utype,roleId=rid,email=uemail,regDate=datetime.date.today())
    r.save()
    return 'OK'

#get data functions
def getStuRoll(sid):
    s=student.objects.get(stuId=sid)
    awards=stuEvent.objects.filter(stuId=sid, eventType='A').order_by('eventDate','effectTerm')
    punishments=stuEvent.objects.filter(stuId=sid, eventType='P').order_by('eventDate','effectTerm')
    records=stuEvent.objects.filter(stuId=sid, eventType='R').order_by('eventDate','effectTerm')
    return {'stuInfo': s, 'awards': awards, 'punishments': punishments, 'records':records}
def getStuList(cid):
    if cid=='all':
        return student.objects.all()
    else:
        return student.objects.filter(classId=cid)

def getClassList(cmid):
    cs=cclass.objects.filter(cmId=cmid)
    cl=[]
    for c in cs:
        cl.append({'cid':c.classId, 'cname':str(c.classGrade)+'-'+c.className})
    return cl

def getStuScore(sid, pterm=-1):
    if pterm==-1:
        sc=courseOnStu.objects.filter(stuId=sid)
    else:
        sc=courseOnStu.objects.filter(stuId=sid,term=pterm)
    scl=[]
    for s in sc:
        tmp={}
        tmp['cname']=course.objects.get(courseId=s.courseId).courseTitle
        tmp['ctype']=course.objects.get(courseId=s.courseId).courseType
        tmp['tname']=teacher.objects.get(teaId=course.objects.get(courseId=s.courseId).teaId).teaName
        tmp['credit']=course.objects.get(courseId=s.courseId).courseCredit
        tmp['term']=s.term
        tmp['escore']=s.examScore
        tmp['nscore']=s.nonExamScore
        tmp['fscore']=s.finalScore
        if tmp['escore']<0: tmp['escore']='N/A'
        if tmp['nscore']<0: tmp['nscore']='N/A'
        if tmp['fscore']<0: tmp['fscore']='N/A'
        scl.append(tmp)
    return scl

def getStuScoreList(coId, claId, odby='stuId'):
    sidl=student.objects.filter(classId=claId).values_list('stuId',flat=True)
    sl=courseOnStu.objects.filter(courseId=coId, stuId__in=sidl).order_by(odby)
    sll=[]
    for s in sl:
        tmp={}
        tmp['id']=s.id
        tmp['sid']=s.stuId
        tmp['sname']=student.objects.get(stuId=s.stuId).stuName
        tmp['escore']=s.examScore
        tmp['nscore']=s.nonExamScore
        tmp['fscore']=s.finalScore
        tmp['term']=s.term
        sll.append(tmp)
    sld={'tname':teacher.objects.get(teaId=(course.objects.get(courseId=coId).teaId)).teaName,
         'crname':course.objects.get(courseId=coId).courseTitle,
         'clname':str(cclass.objects.get(classId=claId).classGrade)+'-'+cclass.objects.get(classId=claId).className,
         'crid':coId,
         'clid':claId,
         'credit':course.objects.get(courseId=coId).courseCredit,
         'ew':course.objects.get(courseId=coId).examWeight,
         'slist':sll
    }
    return sld

def getNoti(nid):
    return notification.objects.get(id=nid)

def getNotiList(cid,ntype='effective'):
    if ntype=='all':
        nl=notification.objects.filter(classId=cid)
    elif ntype=='effective':
        nl=notification.objects.filter(classId=cid, expireDate__gte=datetime.date.today())
    elif ntype=='history':
        nl=notification.objects.filter(classId=cid, expireDate__lt=datetime.date.today())
    return nl

def getPerf(sid, pterm=-1):
    if pterm==-1:
        return performance.objects.filter(stuId=sid).order_by('term')
    else:
        return performance.objects.get(stuId=sid, term=pterm)
def getPerfList(cid, pterm=-1, odby='stuId'):
    try:
        sl=student.objects.filter(classId=cid)
        spl=[]
        for s in sl:
            spl.append({'s':s, 'p':performance.objects.get(stuId=s.stuId,term=pterm)})
        if odby=='FIN': spl.sort(key=lambda x:x['p'].finalScore, reverse=True)
        if odby=='ACA': spl.sort(key=lambda x:x['p'].acaScore, reverse=True)
        if odby=='MOR': spl.sort(key=lambda x:x['p'].moralScore, reverse=True)
        if odby=='AWA': spl.sort(key=lambda x:x['p'].awardScore, reverse=True)
    except:
        spl=[]
    return spl
        
def getClass(cid):
    c=cclass.objects.get(classId=cid)
    return str(c.classGrade)+'-'+c.className
#new data functions:
def newClass(cname, cgrade, cmid):
    c=cclass(className=cname, classGrade=cgrade, cmId=cmid)
    c.save()

def saveStu(sname, sbirth, sgender, snative, sclass, sid='new'):
    if len(sname)==0 or len(sbirth)==0 or len(sgender)==0 or len(snative)==0 or len(sclass)==0:
        return 'All the fields must not be empty!'
    else:
        if sid=='new':
            s=student()
        else:
            s=student.objects.get(stuId=sid)
        s.stuName=sname
        s.stuBirth=sbirth
        s.stuGender=sgender
        s.stuNative=snative
        s.classId=sclass
        s.save()
        return 'OK'
    
def newEvent(sid, ebody, etype, edate, eterm, epoint):
    if len(sid)==0 or len(ebody)==0 or len(etype)==0 or len(edate)==0 or len(eterm)==0 or len(epoint)==0:
        return 'All the fields must not be empty!'
    else:
        e=stuEvent(stuId=sid, eventBody=ebody, eventType=etype, eventDate=edate, effectTerm=eterm, point=epoint)
        e.save()
        return 'OK'

def saveScore(sheet):
    ew=course.objects.get(courseId=sheet['cid']).examWeight*1.0/100
    for rec in sheet['scores']:
        s=courseOnStu.objects.get(courseId=sheet['cid'],stuId=rec['sid'])
        s.examScore=rec['escore']
        s.nonExamScore=rec['nscore']
        s.finalScore=int(rec['escore']*ew+rec['nscore']*(1-ew))
        s.save()
    return 'OK'    

def newNoti(cid, ntitle, nbody, edate):
    if len(cid)==0 or len(ntitle)==0 or len(nbody)==0 or len(edate)==0:
        return 'All the fields must not be empty!'
    else:
        n=notification(classId=cid, notiTitle=ntitle, notiBody=nbody, notiDate=datetime.date.today(), expireDate=edate)
        n.save()
        return 'OK'

def genPerf(cid, pterm, amr=80):
    ss=student.objects.filter(classId=cid)
    for s in ss:
        aca=courseOnStu.objects.filter(stuId=s.stuId, term=pterm).exclude( finalScore=-1).aggregate(Avg('finalScore'))['finalScore__avg']
        mor=stuEvent.objects.filter(stuId=s.stuId, effectTerm=pterm, eventType='R').exclude(point=0).aggregate(Avg('point'))['point__avg']
        awd=stuEvent.objects.filter(stuId=s.stuId, effectTerm=pterm, eventType='A').aggregate(Sum('point'))['point__sum']
        pns=stuEvent.objects.filter(stuId=s.stuId, effectTerm=pterm, eventType='P').aggregate(Sum('point'))['point__sum']
        if aca is None: aca=0
        if mor is None: mor=0
        if awd is None: awd=0
        if pns is None: pns=0
        fin=(aca*amr+mor*(100-amr))*1.0/100+awd-pns
        if performance.objects.filter(stuId=s.stuId, term=pterm).count()!=0:
            p=performance.objects.get(stuId=s.stuId, term=pterm)
        else:
            p=performance()
        p.stuId=s.stuId
        p.acaScore=aca
        p.moralScore=mor
        p.awardScore=awd-pns
        p.amRadio=amr
        p.finalScore=fin
        p.term=pterm
        p.genDate=datetime.date.today()
        p.save()
    return 'OK'

def saveClass(cid, cname, grade, cmid):
    if cid=='new':
        c=cclass(className=cname, classGrade=grade, cmId=cmid)
        c.save()
        return 'OK'
    else:
        try:
            c=cclass.objects.get(classId=cid)
            c.classId=cid
            c.className=cname
            c.classGrade=grade
            c.cmId=cmid
            c.save()
            return 'OK'
        except:
            return 'Can not save this class'
    









