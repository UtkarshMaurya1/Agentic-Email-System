from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ai_agent.graph.runner import resume_email_agent
from ai_agent.models import ApprovalRequest


def pending_approvals_list(request):
    pending = (
        ApprovalRequest.objects
        .filter(decision__isnull=True)
        .select_related("run")
        .order_by("-requested_at")
    )
    return render(request, "dashboard/pending_approvals.html", {"pending": pending})


def approval_detail(request, approval_id):
    approval = get_object_or_404(ApprovalRequest, id=approval_id)
    run = approval.run

    if request.method == "POST":
        action = request.POST.get("action")  # "approve" | "edit" | "reject"
        edited_text = request.POST.get("edited_text", "").strip()

        if action == "approve":
            resume_email_agent(run.langgraph_thread_id, decision="approved")
            messages.success(request, "Approved and sent.")
        elif action == "edit":
            resume_email_agent(run.langgraph_thread_id, decision="edited", edited_text=edited_text)
            messages.success(request, "Edited response sent.")
        elif action == "reject":
            resume_email_agent(run.langgraph_thread_id, decision="rejected")
            messages.info(request, "Rejected — no reply sent.")
        else:
            messages.error(request, "Unknown action.")
            return redirect("dashboard:approval_detail", approval_id=approval.id)

        return redirect("dashboard:pending_approvals")

    return render(request, "dashboard/approval_detail.html", {"approval": approval, "run": run})