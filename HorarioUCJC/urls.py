from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Rutas de la aplicacion
    path('login/',     include("login.urls")),
    path('dashboard/', include("core.urls")),
    path('schedule/',  include("schedule.urls", namespace="schedule")),
    path('admin/',     admin.site.urls),

    # Debug
    path('__debug__/', include('debug_toolbar.urls')),

    # Redireccionamiento
    path("", RedirectView.as_view(pattern_name='login_index'), name="initial_root"),
]
