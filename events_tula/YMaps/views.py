from django.shortcuts import render
from .models import *

# Create your views here.
def index(request):
    events_tula = Event.objects.filter(is_registered=True).values()
    context = {
        "events": list(events_tula)
    }
    return render(request, "index.html", context=context)