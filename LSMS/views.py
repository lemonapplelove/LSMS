#coding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
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
    try:
        return render_to_response(homepage[str(request.user.get_profile())], None, context_instance=RequestContext(request))
    except:
        return logout(request)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return HttpResponseRedirect(request.GET.get('next','/home'))
    else:
        #if request.user.is_authenticated():
            #return HttpResponseRedirect(request.GET.get('next','/home'))
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
        form=RegisterForm()
    return render_to_response('register.html', {'form': form})

def modPass(request):
    pass
def getPass(request):
    pass
def disableUser(requst):
    return HttpResponse('disable user')

@login_required
def read_roll(request, querystr):
    q_type=querystr[0]
    q_id=querystr[1:]
    return HttpResponse('%s,%s' % (q_type, q_id))

#@login_required
def addfor(request, *args, **kwargs):
    obj=kwargs['obj']
    f_map={
           'roll': (StudentForm, 'userinfo_required', '/roll/add/', 'roll_add.html'),
           'class': (ClassForm, 'userinfo_not_required', '/class/add/', 'class_add.html'),
           'notification': (NotificationForm, 'userinfo_required', '/notification/add/', 'notification_add.html'),
           'event': (EventForm, 'userinfo_required', '/event/add/', 'event_add.html'),
           #score
           #'performance': (PerformanceForm, 'userinfo_not_required', '/performance/add/', 'performace_add.html'),
    }
    
    def post_form(t=obj):
        if f_map[t][1]=='userinfo_required': return f_map[t][0](data=request.POST,user=request.user)
        else: return f_map[t][0](data=request.POST)
    
    def blank_form(t=obj):
        if f_map[t][1]=='userinfo_required': return f_map[t][0](user=request.user)
        else: return f_map[t][0]()
    
    def redirect_url(t=obj):
        return f_map[t][2]
    
    def template(t=obj):
        return f_map[t][3]
    
    @permission_required('SM.%s' % kwargs.get('perm', ''))
    def render(request=request):    
        if request.method=='POST':
            form=post_form()
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(redirect_url())
        else:
            form=blank_form()
        return render_to_response(template(), {'form': form})

    return render(request)

def student_query(request, *args, **kwargs):
    t_map={
        'roll':'roll_read.html',
        'score':'score_read.html',
    }
    q_type=args[1]
    if request.user.has_perm('SM.teacher') or request.user.has_perm('SM.classmanager'):
        s_obj=Student.objects.get(id=args[0])
    else:
        s_obj=Student.objects.get(user=request.user)

    def template():
        return t_map[q_type]
    #return HttpResponse(q_set())
    
    return render_to_response(template(),{'content':s_obj})
    
    

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




