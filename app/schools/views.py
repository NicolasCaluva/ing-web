from django.shortcuts import render
from .models import School
# Create your views here.
def school_list(request):
    schools = School.objects.all()
    context = {
        'schools': schools
    }

    return render(request, 'school/school_list.html', context)

def school_detail(request, pk):
    school = School.objects.get(pk=pk)
    context = {
        'school': school
    }

    return render(request, 'school/school_detail.html', context)