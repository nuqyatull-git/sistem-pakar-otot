from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('diagnosa/', views.diagnosa_view, name='diagnosa'),
    path('register/', views.register_pasien_view, name='register'),
    path('login/', views.login_pasien_view, name='login'),
    path('logout/', views.logout_pasien_view, name='logout'),
]