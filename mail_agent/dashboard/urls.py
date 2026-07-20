from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("approvals/", views.pending_approvals_list, name="pending_approvals"),
    path("approvals/<int:approval_id>/", views.approval_detail, name="approval_detail"),
]   