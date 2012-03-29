from LSMS.SM.models import *
from django.contrib import admin

class accountAdmin(admin.ModelAdmin):
    list_display=['userId','userName','userType','roleId']

admin.site.register(account, accountAdmin)
admin.site.register(student)
admin.site.register(teacher)
admin.site.register(cmanager)
admin.site.register(cclass)
admin.site.register(stuEvent)
admin.site.register(course)
admin.site.register(courseOnStu)
admin.site.register(performance)
admin.site.register(notification)