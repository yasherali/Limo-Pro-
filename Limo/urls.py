from django.contrib import admin
from django.urls import path
from portal.views import AdminView, AdminLoginView, CreatingAdminView, admins, ApproveAdminView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin1/', AdminView.as_view()),
    path('adminlogin/', AdminLoginView.as_view()),
    path('creatingadmin/', CreatingAdminView.as_view()),
    path('getnewadmin/', admins),
    path('adminapproval/', ApproveAdminView.as_view()),
]
