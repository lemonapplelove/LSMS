from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from LSMS.SM.libs import *
from LSMS.SM.models import *
import datetime

def msg(request):
    return render_to_response('message.html',{'mbody':request.GET.get('mbody',''), 'mtype':request.GET.get('mtype','info')})

def home(request):
    if request.session.get('utype', False):
        if(request.session['utype']=='S'):
            return HttpResponseRedirect('/stuhome')
        elif(request.session['utype']=='T'):
            return HttpResponseRedirect('/teahome')
        elif(request.session['utype']=='M'):
            return HttpResponseRedirect('/cmhome')
        else:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Unexpected error'))
    else:
        return render_to_response('welcome.html')
def stuHome(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact your class manager.'))
    elif uinfo['utype']!='S':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You are not a student. Please go back to the proper UI.'))
    else:
        return render_to_response('stuhome.html', request.session)
def teaHome(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % 'error',('Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']!='T':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % 'error',('You are not a teacher. Please go back to the proper UI.'))
    else:
        return render_to_response('teahome.html', request.session)
def cmHome(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    elif uinfo['utype']!='M':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','You are not a class manager. Please go back to the proper UI.'))
    else:
        return render_to_response('cmhome.html', request.session)

def register(request):
    if len(request.POST)==0:
        return render_to_response('register.html')
    elif request.POST['password']!=request.POST['cpassword']:
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Please confirm you enter the same password twice!'))
    else:
        res=reg(request.POST['utype'],request.POST['username'],request.POST['password'],request.POST['email'],request.POST['internalid'])
        if res=='OK':
            return authorize(request)
        else:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error',res))
        
def modPass(request):
    uinfo=getuinfo(request)
    if uinfo['state']=='not logon':
        return HttpResponseRedirect('/')
    elif uinfo['state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    else:
        if len(request.POST)==0:
            return render_to_response('modpass.html')
        elif request.POST['npassword']!=request.POST['cpassword']:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Please confirm you enter the same password twice!'))
        elif len(request.POST['npassword'])<6:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Password must have 6 or more characters!'))
        else:
            r=account.objects.get(userId=uinfo['uid'])
            r.userPwd=encrypt(uinfo['uname'],request.POST['npassword'])
            r.save()
            return HttpResponseRedirect('/')
def getPass(request):
    return render_to_response('getpass.html')
def disableUser(requst):
    return HttpResponse('disable user')
def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/')
def authorize(request):
    uname=request.POST.get('username','')
    upass=request.POST.get('password','')
    auth_res=auth(uname,upass)
    if auth_res['auth_state']=='failed':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your username or password is invalid!'))
    elif auth_res['auth_state']=='disabled':
        return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Your account is disabled. Please contact the system administrator.'))
    else:
        request.session['uid']=auth_res['user_object'].userId
        request.session['uname']=auth_res['user_object'].userName
        request.session['email']=auth_res['user_object'].email
        request.session['utype']=auth_res['user_object'].userType
        request.session['rid']=auth_res['user_object'].roleId
        request.session.set_expiry(0)
        if(auth_res['user_object'].userType=='S'):
            request.session['rname']=student.objects.get(stuId=request.session['rid']).stuName
            #return HttpResponseRedirect('/stuhome')
        elif(auth_res['user_object'].userType=='T'):
            request.session['rname']=teacher.objects.get(teaId=request.session['rid']).teaName
            #return HttpResponseRedirect('/teahome')
        elif(auth_res['user_object'].userType=='M'):
            request.session['rname']=cmanager.objects.get(cmId=request.session['rid']).cmName
            #return HttpResponseRedirect('/cmhome')
        else:
            return HttpResponseRedirect('/msg?mtype=%s&mbody=%s' % ('error','Unexpected error'))
        return HttpResponseRedirect('/')

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
