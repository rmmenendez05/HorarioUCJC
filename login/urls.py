from django.urls import path, include
from allauth.account.views import LoginView


urlpatterns = [
    path('', LoginView.as_view(template_name='login/login.html'), name='account_login'),
    path('accounts/', include('allauth.urls')),
]
