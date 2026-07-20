from django.conf import settings
from django.db import models


class AgentRun(models.Model):
    langgraph_thread_id = models.CharField(max_length=255, unique=True)
    message_id = models.CharField(max_length=255)

    original_subject = models.CharField(max_length=500, blank=True)
    original_sender = models.CharField(max_length=255, blank=True)
    original_body = models.TextField(blank=True)

    issue_type = models.CharField(max_length=100, null=True, blank=True)
    urgency = models.CharField(max_length=20, null=True, blank=True)
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    action_taken = models.CharField(max_length=30, null=True, blank=True)

    draft_response = models.TextField(null=True, blank=True)
    final_response = models.TextField(null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("running", "running"),
            ("waiting_approval", "waiting_approval"),
            ("completed", "completed"),
            ("failed", "failed"),
        ],
        default="running",
    )

    def __str__(self):
        return f"AgentRun({self.langgraph_thread_id}, {self.status})"


class ApprovalRequest(models.Model):
    run = models.ForeignKey(AgentRun, on_delete=models.CASCADE, related_name="approval_requests")
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decision = models.CharField(
        max_length=20,
        choices=[("approved", "approved"), ("edited", "edited"), ("rejected", "rejected")],
        null=True,
        blank=True,
    )
    edited_response = models.TextField(null=True, blank=True)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"ApprovalRequest(run={self.run_id}, decision={self.decision})"


class AgentAuditLog(models.Model):
    run = models.ForeignKey(AgentRun, on_delete=models.CASCADE, related_name="audit_entries")
    node_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["timestamp"]