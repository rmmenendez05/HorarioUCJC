from django.urls import path
from .views import render_dashboard, user_management, user_update_rol, alumno_update_grado

urlpatterns = [
    path("",                          render_dashboard,     name="dashboard"),
    path("usuarios/",                 user_management,      name="user_management"),
    path("usuarios/<int:pk>/rol/",    user_update_rol,      name="user_update_rol"),
    path("usuarios/<int:pk>/grado/",  alumno_update_grado,  name="alumno_update_grado"),
]