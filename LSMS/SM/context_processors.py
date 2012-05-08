from LSMS.SM.models import Student, Teacher, ClassManager, data_obj_map
def profile(request):
    try:
        usertype=str(request.user.get_profile())
        data_obj=data_obj_map[usertype].objects.get(user=request.user)
        return {'name':data_obj.name}
    except:
        return {}
    
