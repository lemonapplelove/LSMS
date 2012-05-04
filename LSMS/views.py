#coding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.decorators import login_required
#from LSMS.SM.libs import *
from LSMS.SM.models import *
import datetime
from LSMS.SM.forms import *
from django.contrib.auth.forms import *

def msg(request):
    return render_to_response('message.html',{'mbody':request.GET.get('mbody',''), 'mtype':request.GET.get('mtype','info')})

@login_required
def home(request):
    homepage={'S':'student_home.html', 'T':'teacher_home.html', 'M':'classmanager_home.html'}
    return render_to_response(homepage[str(request.user.get_profile())], None, context_instance=RequestContext(request))

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return HttpResponseRedirect(request.GET.get('next','/home'))
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(request.GET.get('next','/home'))
        form=AuthenticationForm()
    return render_to_response('login.html', {'form':form})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/accounts/login')

def register(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/login')
    else:
        form=RegisterForm();
    return render_to_response('register.html', {'form':form})

def modPass(request):
    pass
def getPass(request):
    pass
def disableUser(requst):
    return HttpResponse('disable user')

def readStuRoll(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    else:
        if uinfo['utype']=='S':
            sid=uinfo['rid']
        else:
            sid=(request.GET['stuId'])
        s=getStuRoll(sid)
        s['pl']=getPerf(sid)
        s['utype']=uinfo['utype']
        return render_to_response('readroll.html',s)
def readStuScore(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    else:
        if uinfo['utype']=='S':
            s=getStuScore(uinfo['rid'],int(request.GET.get('term',-1)))
        else:
            s=getStuScore(request.GET['stuId'],int(request.GET.get('term',-1)))
        return render_to_response('readscore.html',{'clist':s})
    return HttpResponse('Student Score Read')
def readStuPerf(request):
    return HttpResponse('Student Performance Read')
def readStuNoti(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    else:
        if uinfo['utype']=='T':
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Teachers have no notification in student management system.'))
        elif not request.GET.get('nid',False):
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Invalid entry of notification!'))
        elif notification.objects.filter(id=request.GET['nid']).count()==0:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Invalid entry of notification!'))
        else:
            n=notification.objects.get(id=request.GET['nid'])
            if (uinfo['utype']=='S' and n.classId==student.objects.get(stuId=uinfo['rid']).classId) or (uinfo['utype']=='M' and cclass.objects.filter(cmId=uinfo['rid'],classId=n.classId).count()!=0):
                return render_to_response('readnoti.html',{'noti':n})
            else:
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Invalid entry of notification!'))

def listStuRoll(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.GET)==0 or len(request.GET['cid'])==0:
            return render_to_response('liststu.html',{'cl':getClassList(uinfo['rid'])})
        else:
            return render_to_response('liststu.html',{'cl':getClassList(uinfo['rid']), 'sl':getStuList(request.GET['cid']), 'cid':int(request.GET['cid'])})
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def listStuScore(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='T':
        crid=request.GET['crid']
        clid=request.GET['clid']
        if course.objects.filter(teaId=uinfo['rid'],courseId=crid).count()==0:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You do not teach this course.'))
        else:
            od=request.GET.get('orderby','stuId')
            return render_to_response('listscore.html',getStuScoreList(crid,clid,od))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def listCourse(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='T':
        if request.GET.get('crid',False):
            crid=request.GET['crid']
            if request.GET.get('clid',False):
                clid=request.GET['clid']
                return HttpResponseRedirect('/list/stuscore?crid=%s&clid=%s' % (crid,clid))
            else:
                sl=courseOnStu.objects.filter(courseId=crid).values_list('stuId',flat=True)
                cidl=student.objects.filter(classId__in=sl).distinct('classId').values_list('classId',flat=True)
                cl=[]
                for c in cclass.objects.filter(classId__in=cidl):
                    tmp={'cid':c.classId, 'cname':str(c.classGrade)+'-'+c.className}
                    cl.append(tmp)
                return render_to_response('listcourse.html',{'cl':cl,'cr':crid})
        else:
            return render_to_response('listcourse.html',{'crl':course.objects.filter(teaId=uinfo['rid'])})
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def listStuPerf(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.GET)==0 or len(request.GET['cid'])==0 or len(request.GET['term'])==0:
            return render_to_response('listperf.html',{'cl':getClassList(uinfo['rid']),'term':int(request.GET.get('term',0))})
        else:
            od=request.GET.get('orderby', 'stuId')
            return render_to_response('listperf.html',{'cl':getClassList(uinfo['rid']), 'spl':getPerfList(request.GET['cid'],int(request.GET['term']), od), 'cid':int(request.GET['cid']), 'term':int(request.GET['term'])})
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def listStuNoti(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        cl=getClassList(uinfo['rid'])
        if len(request.GET)==0 or not request.GET.get('cid',False):
            return render_to_response('listnoti.html',{'cl':cl})
        else:
            ns=request.GET.get('nscope','all')
            cid=int(request.GET['cid'])
            return render_to_response('listnoti.html',{'cl':cl, 'cid':cid, 'nl':getNotiList(cid,ns), 'ns':ns})
    elif uinfo['utype']=='S':
        ns=request.GET.get('nscope','all')
        cid=student.objects.get(stuId=uinfo['rid']).classId
        return render_to_response('listnoti.html',{'cid':cid, 'nl':getNotiList(cid,ns), 'ns':ns})
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Teacher do not have notification in the system'))

def listClass(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        cl=getClassList(uinfo['rid'])
        return render_to_response('listclass.html',{'cl':cl})
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))

def newStuRoll(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.POST)==0:
            cl=[]
            for c in cclass.objects.filter(cmId=uinfo['rid']):
                tmp={'cid':c.classId, 'cname':str(c.classGrade)+'-'+c.className}
                cl.append(tmp)
            return render_to_response('newstu.html',{'cl':cl})
        else:
            res=saveStu(request.POST['sname'], request.POST['sbirth'], request.POST['sgender'], request.POST['snative'], request.POST['sclass'])
            if res=='OK':
                mt='info'
                res='The student is successfully created!'
            else:
                mt='error'
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % (mt,res))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def newStuEvent(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.POST)==0:
            if (student.objects.filter(stuId=request.GET['sid']).count==0) or (cclass.objects.filter(cmId=uinfo['rid'],classId=student.objects.get(stuId=request.GET['sid']).classId).count()==0):
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','No such student in your class!'))
            else:
                return render_to_response('newevent.html',{'sid':request.GET['sid'],'sname':student.objects.get(stuId=request.GET['sid']).stuName})
        else:
            res=newEvent(request.POST['sid'], request.POST['ebody'], request.POST['etype'], request.POST['edate'], request.POST['eterm'], request.POST['epoint'])
            if res=='OK':
                mt='info'
                res='The event is successfully created!'
            else:
                mt='error'
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % (mt,res))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def newStuScore(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='T':
        if len(request.POST)==0:
            crid=request.GET['crid']
            clid=request.GET['clid']
            if course.objects.filter(teaId=uinfo['rid'],courseId=crid).count()==0:
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You do not teach this course.'))
            else:
                return render_to_response('grade.html',getStuScoreList(crid,clid))
        else:
            ssheet=eval(request.POST['ssheet'])
            saveScore(ssheet)
            #res=newNoti(request.POST['nclass'], request.POST['ntitle'], request.POST['nbody'], request.POST['edate'])
            #if res=='OK':
            #    mt='info'
            #    res='The notification is successfully created!'
            #else:
            #    mt='error'
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('info','Score sheet has been saved!'))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def newStuPerf(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.POST)==0:
            return render_to_response('newperf.html', {'cl':getClassList(uinfo['rid'])})
        else:
            res=genPerf(request.POST['cid'], request.POST['term'], int(request.POST['aweight']))
            if res=='OK':
                return HttpResponseRedirect('/list/stuperf?cid=%s&term=%s' % (request.POST['cid'], request.POST['term']))
            else:
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error',res))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def newStuNoti(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.POST)==0:
            cl=[]
            for c in cclass.objects.filter(cmId=uinfo['rid']):
                tmp={'cid':c.classId, 'cname':str(c.classGrade)+'-'+c.className}
                cl.append(tmp)
            return render_to_response('newnoti.html',{'cl':cl})
        else:
            res=newNoti(request.POST['nclass'], request.POST['ntitle'], request.POST['nbody'], request.POST['edate'])
            if res=='OK':
                mt='info'
                res='The notification is successfully created!'
            else:
                mt='error'
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % (mt,res))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))

def newClass(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.POST)==0:
            return render_to_response('newclass.html')
        else:
            res=saveClass('new', request.POST['cname'], request.POST['grade'], uinfo['rid'])
            if res=='OK':
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('info','Your class is created!'))
            else:
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error',res))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))

def modStuRoll(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.POST)==0:
            s=getStuRoll(request.GET['sid'])
            cl=[]
            for c in cclass.objects.filter(cmId=uinfo['rid']):
                tmp={'cid':c.classId, 'cname':str(c.classGrade)+'-'+c.className}
                cl.append(tmp)
            s['cl']=cl;
            return render_to_response('modroll.html', s)
        else:
            res=saveStu(request.POST['sname'], request.POST['sbirth'], request.POST['sgender'], request.POST['snative'], request.POST['sclass'], request.POST['sid'])
            if res=='OK':
                return HttpResponseRedirect('/read/sturoll?stuId=%s' % request.POST['sid'])
            else:
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error',res))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def modClass(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if len(request.POST)==0:
            c=cclass.objects.get(classId=request.GET['cid'])
            cm=cmanager.objects.all()
            return render_to_response('modclass.html', {'c':c, 'cm':cm})
        elif uinfo['rid']!=cclass.objects.get(classId=request.POST['cid']).cmId:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission on this class!'))
        else:
            res=saveClass(request.POST['cid'], request.POST['cname'], request.POST['grade'], request.POST['cmid'])
            if res=='OK':
                return HttpResponseRedirect('/list/class/')
            else:
                return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error',res))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))

def delStuNoti(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        c=notification.objects.get(id=request.GET['nid'])
        if cclass.objects.filter(classId=c.classId, cmId=uinfo['rid']).count()!=0:
            c.delete()
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('info','The notification is deleted!'))
        else:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
def delStuEvent(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        e=stuEvent.objects.get(eventId=request.GET['eid'])
        c=student.objects.get(stuId=e.stuId)
        if cclass.objects.filter(classId=c.classId, cmId=uinfo['rid']).count()!=0:
            e.delete()
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('info','The event is deleted!'))
        else:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
    
def delClass(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        if student.objects.filter(classId=request.GET['cid']).count() !=0:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','The class is not empty. Can not delete!'))
        if cclass.objects.filter(classId=request.GET['cid'], cmId=uinfo['rid']).count()!=0:
            cclass.objects.get(classId=request.GET['cid']).delete()
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('info','The class is deleted!'))
        else:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))

def delStuRoll(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']=='M':
        sid=request.GET['sid']
        cid=student.objects.get(stuId=sid).classId
        if cclass.objects.filter(classId=cid, cmId=uinfo['rid']).count()!=0:
            stuEvent.objects.filter(stuId=sid).delete()
            courseOnStu.objects.filter(stuId=sid).delete()
            performance.objects.filter(stuId=sid).delete()
            student.objects.filter(stuId=sid).delete()
            account.objects.filter(roleId=sid, userType='S').delete()
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('info','The student is deleted!'))
        else:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
    else:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You have no permission!'))
