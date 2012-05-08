from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'LSMS.views.home', name='home'),
    url(r'^home/', 'LSMS.views.home'),
    
    url(r'^accounts/login', 'LSMS.views.login'),
    url(r'^accounts/register', 'LSMS.views.register'),
    url(r'^accounts/modifyPassword', 'LSMS.views.modPass'),
    url(r'^accounts/resetPassword', 'LSMS.views.getPass'),
    url(r'^accounts/logout', 'LSMS.views.logout'),
    
    url(r'^s/(\d+)/(roll|score)/', 'LSMS.views.student_query'),
    url(r'^t/(\d+)/(course|score)/', 'LSMS.views.teacher_query'),
    url(r'^cm/(\d+)/(roll|event|score|performance)/', 'LSMS.views.classmanager_query'),
    
    url(r'^roll/add/', 'LSMS.views.addfor', {'obj':'roll', 'perm':'classmanager'}),
    
    url(r'^class/add/', 'LSMS.views.addfor', {'obj':'class', 'perm':'classmanager'}),
    
    url(r'^notification/add/', 'LSMS.views.addfor', {'obj':'notification', 'perm':'classmanager'}),
    
    url(r'^event/add/', 'LSMS.views.addfor', {'obj':'event', 'perm':'classmanager'}),
    
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
