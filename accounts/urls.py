from django.urls import path,include
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('admin-redirect/', views.admin_redirect, name='admin_redirect'),
    path('registration',views.register,name='register'),
]
