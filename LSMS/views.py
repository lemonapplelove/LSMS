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

@login_required
def home(request):
    try:
        user_type=str(request.user.get_profile())
    except:
        return logout(request)
    if user_type=='S':
        return render_to_response('student_home.html', {'content':Student.objects.get(user=request.user)}, context_instance=RequestContext(request))
    elif user_type=='T':
        return HttpResponseRedirect('/course/')
    elif user_type=='M':
        return HttpResponseRedirect('/class/')

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
    return render_to_response('login.html', {'form':form}, context_instance=RequestContext(request))

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
    return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def password_modify(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/logout/')
    else:
        #if request.user.is_authenticated():
            #return HttpResponseRedirect(request.GET.get('next','/home'))
        form=PasswordChangeForm(user=request.user)
    return render_to_response('password_modify.html', {'form':form}, context_instance=RequestContext(request))
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/logout/')
    else:
        form=PasswordResetForm()
    return render_to_response('password_reset.html', {'form':form}, context_instance=RequestContext(request))
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

@permission_required('SM.classmanager')
def class_add(request):
    if request.method=='POST':
        form=ClassForm(data=request.POST,user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>window.opener.location.replace(window.opener.location.href);window.close();</script>')
    else:
        form=ClassForm(user=request.user)
    return render_to_response('class_add.html', {'form': form}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def class_modify(request, cid):
    if request.method=='POST':
        form=ClassForm(data=request.POST,user=request.user, instance=Class.objects.get(id=cid))
        if form.is_valid():
            form.save()
            return HttpResponse('<script>window.opener.location.replace(window.opener.location.href);window.close();</script>')
    else:
        form=ClassForm(user=request.user, instance=Class.objects.get(id=cid))
    return render_to_response('class_modify.html', {'form': form}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def class_list(request):
    q_set=Class.objects.filter(class_manager__user=request.user)
    return render_to_response('class_list.html', {'content': q_set}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def student_add(request, cid):
    if request.method=='POST':
        form=StudentForm(data=request.POST, user=request.user, cid=cid)
        if form.is_valid():
            s=form.save()
            #return HttpResponseRedirect('/class/%s/student/' % s.class_obj.id)
            return HttpResponse('<script>window.opener.location.replace(window.opener.location.href);window.close();</script>')
    else:
        form=StudentForm(user=request.user, cid=cid)
    return render_to_response('student_add.html', {'form': form}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def student_modify(request, sid):
    if request.method=='POST':
        s=Student.objects.get(id=sid)
        form=StudentForm(data=request.POST,user=request.user, instance=s, cid=s.class_obj)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>window.opener.location.replace(window.opener.location.href);window.close();</script>')
    else:
        s=Student.objects.get(id=sid)
        form=StudentForm(user=request.user, instance=s, cid=s.class_obj)
    return render_to_response('student_modify.html', {'form': form}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def student_list(request, cid):
    q_set=Student.objects.filter(class_obj=cid)
    extra_set={'class': Class.objects.get(id=cid), 'classes':Class.objects.filter(class_manager__user=request.user)}
    return render_to_response('student_list.html', {'content': q_set, 'extra': extra_set}, context_instance=RequestContext(request))

@permission_required('SM.student')
def student_read(request, sid):
    q_set=Student.objects.get(id=sid)
    return render_to_response('student_read.html', {'content': q_set}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def event_add(request, sid):
    if request.method=='POST':
        form=EventForm(data=request.POST, user=request.user, sid=sid)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>window.opener.location.replace(window.opener.location.href);window.close();</script>')
    else:
        form=EventForm(user=request.user, sid=sid)
    return render_to_response('event_add.html', {'form': form}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def notification_add(request, cid):
    if request.method=='POST':
        form=NotificationForm(data=request.POST, user=request.user, cid=cid)
        if form.is_valid():
            n=form.save()
            return HttpResponse('<script>window.opener.location.replace(window.opener.location.href);window.close();</script>')
    else:
        form=NotificationForm(user=request.user, cid=cid)
    return render_to_response('notification_add.html', {'form': form}, context_instance=RequestContext(request))

@permission_required('SM.student')
def notification_list(request, cid):
    q_set=Notification.objects.filter(class_obj=cid).order_by('-release_date', 'expire_date', '-id')
    extra_set={'class': Class.objects.get(id=cid), 'classes':Class.objects.filter(class_manager__user=request.user)}
    return render_to_response('notification_list.html', {'content': q_set, 'extra': extra_set}, context_instance=RequestContext(request))

@permission_required('SM.student')
def notification_read(request, nid):
    q_set=Notification.objects.get(id=nid)
    return render_to_response('notification_read.html', {'content': q_set}, context_instance=RequestContext(request))

@permission_required('SM.teacher')
def score_grade(request, course_id, class_id):
    if request.method=='POST':
        formset=GradeFormSet(data=request.POST)
        if formset.is_valid():
            instances=formset.save(commit=False)
            ew=Course.objects.get(id=course_id).exam_weight
            for i in instances:
                if i.exam_score and i.non_exam_score:
                    i.final_score=(i.exam_score * ew + i.non_exam_score * (100 - ew))/100
                i.save()
            return HttpResponseRedirect('/course/%s/class/%s/' % (course_id, class_id))
    else:
        extra_set={
            'course_info': Course.objects.get(id=course_id),
            'class_info': Class.objects.get(id=class_id),
        }   
        formset=GradeFormSet(queryset=CourseOnStudent.objects.filter(course=course_id, student__class_obj=class_id))
    return render_to_response('score_grade.html', {'formset': formset, 'extra': extra_set}, context_instance=RequestContext(request))

@permission_required('SM.student')
def score_read(request, sid, term=None):
    q_set=CourseOnStudent.objects.filter(student=sid)
    extra_set={
        'student':Student.objects.get(id=sid),
        'selected_term': term,
    }
    if term:
        q_set=q_set.filter(term=term)
    return render_to_response('score_read.html', {'content': q_set, 'extra': extra_set}, context_instance=RequestContext(request))

@permission_required('SM.teacher')
def score_list(request, course_id, class_id):
    q_set=CourseOnStudent.objects.filter(course=course_id, student__class_obj=class_id)
    order=request.GET.get('order', False)
    if order:
        q_set=q_set.order_by(order)
    extra_set={
        'course_info': Course.objects.get(id=course_id),
        'class_info': Class.objects.get(id=class_id),
    }    
    return render_to_response('score_list.html', {'content': q_set, 'extra': extra_set}, context_instance=RequestContext(request))

@permission_required('SM.teacher')
def course_list(request, course_id=None):
    q_set=Course.objects.filter(teacher__user=request.user)
    extra_set=None
    if course_id:
        extra_set={
            'classes': Class.objects.filter(id__in=CourseOnStudent.objects.filter(course__teacher__user=request.user, course=course_id).values_list('student__class_obj').distinct()),
            'course_id':course_id, 
        }
    return render_to_response('course_list.html', {'content': q_set, 'extra': extra_set}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def performance_list(request, cid, term=None):
    cond={'student__class_obj': cid}
    if term: cond['term']=term
    q_set=Performance.objects.filter(**cond)
    extra_set={'class': Class.objects.get(id=cid), 'classes':Class.objects.filter(class_manager__user=request.user), 'selected_term':term}
    order=request.GET.get('order', False)
    if order:
        q_set=q_set.order_by(order)
    return render_to_response('performance_list.html', {'content': q_set, 'extra': extra_set}, context_instance=RequestContext(request))

@permission_required('SM.classmanager')
def performance_generate(request, cid, term=None):
    amr=int(request.GET.get('amr', 80))
    for s in Student.objects.filter(class_obj=cid):
        s.generate_performance(term, amr)
    return HttpResponseRedirect('/class/%s/performance/term/%s/' % (cid, term))

@permission_required('SM.classmanager')
def remove(request, obj_id, obj_type):
    obj_map={
        'student':Student,
        'event':StudentEvent,
        'class':Class,
        'notification': Notification,
    }
    
    obj=obj_map[obj_type].objects.get(id=obj_id)
    confirmed=request.GET.get('confirmed', False)
    def check():
        if obj_type=='class':
            if obj.student_set.all().count() >0:
                return '班级非空，删除失败！'
        return True
    msg=check()
    if msg != True:
        return HttpResponse('<script>alert(\'%s\');window.opener.location.replace(window.opener.location.href);window.close();</script>' % msg)
    
    if obj_type=='student':
        Performance.objects.filter(student=obj).delete()
        CourseOnStudent.objects.filter(student=obj).delete()
        StudentEvent.objects.filter(student=obj).delete()
        if obj.user: obj.user.delete()
    obj.delete()
    return HttpResponse('<script>alert(\'删除成功！\');window.opener.location.replace(window.opener.location.href);window.close();</script>')
    




