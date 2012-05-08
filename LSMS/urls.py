from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'LSMS.views.home'),
    url(r'^home/', 'LSMS.views.home'),
    
    url(r'^accounts/login', 'LSMS.views.login'),
    url(r'^accounts/register', 'LSMS.views.register'),
    url(r'^accounts/modifyPassword', 'LSMS.views.modPass'),
    url(r'^accounts/resetPassword', 'LSMS.views.getPass'),
    url(r'^accounts/logout', 'LSMS.views.logout'),
    
    url(r'^s/(\d+)/roll/', 'LSMS.views.student_read'),
    url(r'^s/(\d+)/score/', 'LSMS.views.score_read'),
    url(r'^s/(\d+)/event/add', 'LSMS.views.event_add'),
    
    url(r'^course/(\d+)/class/(\d+)/$', 'LSMS.views.score_list'),
    url(r'^course/(\d+)/class/(\d+)/grade/$', 'LSMS.views.score_grade'),
    
    url(r'^class/$', 'LSMS.views.class_list'),
    url(r'^class/add/$', 'LSMS.views.class_add'),
    
    url(r'^class/(\d+)/$', 'LSMS.views.student_list'),
    url(r'^class/(\d+)/student/$', 'LSMS.views.student_list'),
    url(r'^class/(\d+)/student/add$', 'LSMS.views.student_add'),
    
    url(r'^class/(\d+)/notification/$', 'LSMS.views.notification_list'),
    url(r'^class/(\d+)/notification/add$', 'LSMS.views.notification_add'),
    
    url(r'^class/(\d+)/performance/$', 'LSMS.views.performance_list'),
    url(r'^class/(\d+)/performance/term/(\d+)/$', 'LSMS.views.performance_list'),
    url(r'^class/(\d+)/performance/term/(\d+)/generate/$', 'LSMS.views.performance_generate'),
    
    url(r'^notification/(\d+)/$', 'LSMS.views.notification_read'),
    
    
    url(r'^class/add/', 'LSMS.views.addfor', {'obj':'class', 'perm':'classmanager'}),
    
    url(r'^notification/add/', 'LSMS.views.addfor', {'obj':'notification', 'perm':'classmanager'}),
    
    
    url(r'^read/sturoll', 'LSMS.views.readStuRoll'),
    url(r'^read/stuscore', 'LSMS.views.readStuScore'),
    url(r'^read/stuperf', 'LSMS.views.readStuPerf'),
    url(r'^read/stunoti', 'LSMS.views.readStuNoti'),
    
    url(r'^list/sturoll', 'LSMS.views.listStuRoll'),
    url(r'^list/stuscore', 'LSMS.views.listStuScore'),
    url(r'^list/stuperf', 'LSMS.views.listStuPerf'),
    url(r'^list/stunoti', 'LSMS.views.listStuNoti'),
    url(r'^list/course', 'LSMS.views.listCourse'),
    url(r'^list/class', 'LSMS.views.listClass'),
    
    url(r'^new/sturoll', 'LSMS.views.newStuRoll'),
    url(r'^new/stuevent', 'LSMS.views.newStuEvent'),
    url(r'^new/stuscore', 'LSMS.views.newStuScore'),
    url(r'^new/stuperf', 'LSMS.views.newStuPerf'),
    url(r'^new/stunoti', 'LSMS.views.newStuNoti'),
    url(r'^new/class', 'LSMS.views.newClass'),
    
    url(r'^mod/sturoll', 'LSMS.views.modStuRoll'),
    url(r'^mod/class', 'LSMS.views.modClass'),
    
    url(r'^del/stunoti', 'LSMS.views.delStuNoti'),
    url(r'^del/stuevent', 'LSMS.views.delStuEvent'),
    url(r'^del/class', 'LSMS.views.delClass'),
    url(r'^del/sturoll', 'LSMS.views.delStuRoll'),
    
    url(r'^msg', 'LSMS.views.msg'),
    # url(r'^LSMS/', include('LSMS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
