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
    
    url(r'^s/(\d+)/$', 'LSMS.views.student_read'),
    url(r'^s/(\d+)/info/', 'LSMS.views.student_read'),
    url(r'^s/(\d+)/delete/', 'LSMS.views.remove', {'obj_type': 'student'}),
    url(r'^s/(\d+)/score/', 'LSMS.views.score_read'),
    url(r'^s/(\d+)/event/add/', 'LSMS.views.event_add'),
    url(r'^event/(\d+)/delete', 'LSMS.views.remove', {'obj_type': 'event'}),
    
    
    url(r'^course/$', 'LSMS.views.course_list'),
    url(r'^course/(\d+)/class/$', 'LSMS.views.course_list'),
    url(r'^course/(\d+)/class/(\d+)/$', 'LSMS.views.score_list'),
    url(r'^course/(\d+)/class/(\d+)/grade/$', 'LSMS.views.score_grade'),
    
    url(r'^class/$', 'LSMS.views.class_list'),
    url(r'^class/add/$', 'LSMS.views.class_add'),
    
    url(r'^class/(\d+)/$', 'LSMS.views.student_list'),
    url(r'^class/(\d+)/student/$', 'LSMS.views.student_list'),
    url(r'^class/(\d+)/student/add$', 'LSMS.views.student_add'),
    url(r'^class/(\d+)/delete', 'LSMS.views.remove', {'obj_type': 'class'}),
    
    url(r'^class/(\d+)/notification/$', 'LSMS.views.notification_list'),
    url(r'^class/(\d+)/notification/add$', 'LSMS.views.notification_add'),
    url(r'^notification/(\d+)/$', 'LSMS.views.notification_read'),
    url(r'^notification/(\d+)/delete', 'LSMS.views.remove', {'obj_type': 'notification'}),
    
    url(r'^class/(\d+)/performance/$', 'LSMS.views.performance_list'),
    url(r'^class/(\d+)/performance/term/(\d+)/$', 'LSMS.views.performance_list'),
    url(r'^class/(\d+)/performance/term/(\d+)/generate/$', 'LSMS.views.performance_generate'),
    # url(r'^LSMS/', include('LSMS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
