from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'LSMS.views.home', name='home'),
    url(r'^stuhome', 'LSMS.views.stuHome'),
    url(r'^teahome', 'LSMS.views.teaHome'),
    url(r'^cmhome', 'LSMS.views.cmHome'),
    
    url(r'^user/register', 'LSMS.views.register'),
    url(r'^user/authorize', 'LSMS.views.authorize'),
    url(r'^user/modpass', 'LSMS.views.modPass'),
    url(r'user/disable', 'LSMS.views.disableUser'),
    url(r'user/getpass', 'LSMS.views.getPass'),
    url(r'user/logout', 'LSMS.views.logout'),
    
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
