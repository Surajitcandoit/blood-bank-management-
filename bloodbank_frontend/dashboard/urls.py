from django.urls import path
from .views import (
    add_donation,
    delete_staff,
    login_view,
    landing_page,
    dashboard,
    logout_view,
    inventory,
    donors,
    hospitals,
    manage_staff,
    reports,
    requests_page,
    approve_request,
    reject_request,
    distributions,
    reports,
    delete_donor,
    delete_hospital,
    export_report,
    register_view,
    create_blood_request,
    
)

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('admin/manage-staff/', manage_staff, name='manage_staff'),
    path('admin/delete-staff/<int:user_id>/', delete_staff, name='delete_staff'),
    path('request-blood/', create_blood_request, name='request_blood'),
    path("inventory/", inventory, name="inventory"),
    path("donors/", donors, name="donors"),
    path("hospitals/", hospitals, name="hospitals"),
    path("requests/", requests_page, name="requests"),
    path("request/<int:request_id>/approve/", approve_request, name="approve_request"),
    path("request/<int:request_id>/reject/", reject_request, name="reject_request"),
    path("distributions/", distributions, name="distributions"),
    path("reports/", reports, name="reports"),
    path(
    "donor/delete/<int:donor_id>/",
    delete_donor,
    name="delete_donor"
),

    path(
    "hospital/delete/<int:hospital_id>/",
    delete_hospital,
    name="delete_hospital"
),
    path(
    "reports/pdf/",
    export_report,
    name="export_report"
),

    path(
        "donor/<int:donor_id>/donate/", 
        add_donation, 
        name="add_donation"
    ),

]