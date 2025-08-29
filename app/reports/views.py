from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Report
from ..schools.models import Comment
from ..users.models import UserBase

@login_required
def report_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, school_id=pk)

    if request.method == "POST":
        if request.user.is_authenticated:
            reason = request.POST.get("reason")
            if reason:
                obj, created = Report.objects.get_or_create(
                    user = UserBase.objects.get(user=request.user),
                    comment=comment,
                    defaults={'reason': reason}
                )
                if not created:
                    obj.reason = reason
                    obj.save()
    return redirect('school:school_detail', pk=pk)