from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_compra(correo_cliente, nombre):
    asunto = 'Confirmación de compra 💈'
    mensaje = f'Hola {nombre}, tu compra fue realizada con éxito. Gracias por tu compra.'
    
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,  # 👈 mejor que None
        [correo_cliente],
        fail_silently=False,
    )


