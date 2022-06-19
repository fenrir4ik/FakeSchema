from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from apps.user.forms import LoginForm

urlpatterns = [
    path('login/', LoginView.as_view(template_name='user/login.html', form_class=LoginForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
