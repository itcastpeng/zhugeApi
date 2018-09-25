
from django.http import HttpResponse



def pay(request):
    print(request.POST)
    print(request.GET)


    return HttpResponse('-===')
