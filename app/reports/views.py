from django.shortcuts import render, get_object_or_404, redirect

from .forms import ReportForm
from ..schools.models import Comment
from .models import Report

def report_comment(request, pk, comment_id):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.comment_id = comment_id
            report.save()
            return redirect('school:school_detail', pk=pk)
    else:
        form = ReportForm()
    return render(request, 'report_comment.html', {'form': form})