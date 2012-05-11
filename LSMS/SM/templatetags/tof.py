from django import template 
register = template.Library() 

@register.filter(name='tof')
def tof(value): 
    f=float(value)/100
    return f