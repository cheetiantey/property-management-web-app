from django.urls import path
from . import views

# Added these two lines so that files could be uploaded
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("maintenance", views.maintenance, name="maintenance"),
    path("contact", views.contact, name="contact"),
    path("documents", views.documents, name="documents"),
    path("manager_documents", views.manager_documents, name="manager_documents"),
    path("manager_documents/<int:property_id>", views.manager_documents_specific, name="manager_documents_specific"),
    path("add_property", views.add_property, name="add_property"),
    path("property/<int:property_id>", views.property_page, name="property_page"),
    path("add_tenant", views.add_tenant, name="add_tenant"),
    path("maintenance_requests", views.maintenance_requests, name="maintenance_requests"),
    path("maintenance_requests/<int:property_id>", views.maintenance_requests_specific, name="maintenance_requests_specific"),
    path("resolve/<int:maintenance_id>", views.resolve, name="resolve")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)