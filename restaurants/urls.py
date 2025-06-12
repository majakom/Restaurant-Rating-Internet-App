from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import logout_view
from .views import restaurant_add

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('register/', views.register, name='register'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('add-restaurant/', restaurant_add, name='restaurant_add'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)