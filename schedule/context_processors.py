from core.models import Notificacion


def notificaciones_count(request):
    if request.user.is_authenticated:
        qs = Notificacion.objects.filter(destinatario=request.user)
        return {
            'notif_no_leidas': qs.filter(leida=False).count(),
            'notif_recientes': list(qs[:5]),
        }
    return {'notif_no_leidas': 0, 'notif_recientes': []}
