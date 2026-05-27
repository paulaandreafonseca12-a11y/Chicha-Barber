import ssl
from django.core.mail import EmailMultiAlternatives, send_mail, get_connection
from django.conf import settings
from django.utils import timezone
import pytz #es la calculadora que hace el cambio de moneda exacto entre la hora global del servidor y la hora de tu barbería.
import locale

try:
    locale.setlocale(locale.LC_TIME, 'es_CO.UTF-8') # Para Linux/macOS
except:
    locale.setlocale(locale.LC_TIME, 'es_ES') # Para Windows

def enviar_correo_cancelacion_admin(correo_cliente, nombre, servicio, fecha):
    subject = f"IMPORTANTE: Cambio en tu cita - Chicha Barber Studio"
    
    # 1. Convertimos la fecha a la zona horaria de Colombia explícitamente
    zona_local = pytz.timezone('America/Bogota')
    
    # Si la fecha ya tiene zona horaria, la convertimos. Si no, la localizamos.
    if timezone.is_aware(fecha):
        fecha_local = fecha.astimezone(zona_local)
    else:
        fecha_local = zona_local.localize(fecha)
    
    # 2. Formateamos usando la fecha local
    # %H:%M para formato 24h o %I:%M %p para 12h con AM/PM
    fecha_formateada = fecha_local.strftime('%A %d de %B a las %I:%M %p')
    
    message = f"""
    Hola, {nombre}.
    
    Te escribimos de Chicha Barber Studio para informarte que, debido a motivos de fuerza mayor, 
    no podremos atender tu cita de {servicio} programada para el {fecha_formateada}.
    
    Lamentamos mucho los inconvenientes que esto pueda causarte. Queremos invitarte a que 
    programes una nueva cita a través de nuestra web en un horario que te sea cómodo.
    
    ¡Estamos listos para dejarte con el mejor estilo apenas regreses!
    
    Atentamente,
    El equipo de Chicha Barber Studio ✂️💈
    """

    connection = get_connection(ssl_context=ssl._create_unverified_context())

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [correo_cliente],
        fail_silently=False,
        connection=connection
    )


def enviar_correo_compra(correo_cliente, nombre, carrito, total):

    asunto = 'Confirmación de compra 💈'

    productos_html = ""

    for item in carrito:
        productos_html += f"""
        <tr>
            <td style="padding:12px; border-bottom:1px solid #ddd;">
                {item['nombre']}
            </td>

            <td style="padding:12px; border-bottom:1px solid #ddd; text-align:center;">
                {item['cantidad']}
            </td>

            <td style="padding:12px; border-bottom:1px solid #ddd; text-align:right;">
                ${item['precio']}
            </td>
        </tr>
        """

    html_content = f"""
    <div style="
        background:#f4f4f4;
        padding:40px;
        font-family:Arial;
    ">

        <div style="
            max-width:700px;
            margin:auto;
            background:white;
            border-radius:15px;
            overflow:hidden;
            box-shadow:0 0 15px rgba(0,0,0,.1);
        ">

            <!-- HEADER -->
            <div style="
                background:black;
                color:white;
                padding:35px;
                text-align:center;
            ">

                <img
                    src="logo.png"
                    width="90"
                >

                <h1 style="margin-top:15px;">
                    Chicha Barber 💈
                </h1>

                <p>
                    Confirmación de compra
                </p>

            </div>

            <!-- BODY -->
            <div style="padding:35px;">

                <h2>Hola {nombre} 👋</h2>

                <p>
                    Gracias por realizar tu compra en nuestra barbería.
                </p>

                <h3 style="margin-top:30px;">
                    🛒 Resumen de compra
                </h3>

                <table style="
                    width:100%;
                    border-collapse:collapse;
                    margin-top:20px;
                ">

                    <thead>

                        <tr style="background:#f1f1f1;">

                            <th style="padding:15px;">
                                Producto
                            </th>

                            <th style="padding:15px;">
                                Cantidad
                            </th>

                            <th style="padding:15px;">
                                Precio
                            </th>

                        </tr>

                    </thead>

                    <tbody>
                        {productos_html}
                    </tbody>

                </table>

                <h2 style="
                    margin-top:30px;
                    text-align:right;
                    color:#28a745;
                ">
                    Total: ${total}
                </h2>

                <p style="margin-top:40px;">
                    ✂️ Gracias por confiar en nosotros.
                </p>

            </div>

            <!-- FOOTER -->
            <div style="
                background:#111;
                color:#bbb;
                text-align:center;
                padding:20px;
                font-size:14px;
            ">
                © 2026 Chicha Barber
            </div>

        </div>

    </div>
    """

    connection = get_connection(ssl_context=ssl._create_unverified_context())

    email = EmailMultiAlternatives(
        asunto,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [correo_cliente],
        connection=connection
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

#reservas correo
def enviar_correo_reserva(correo_cliente, nombre, servicio, fecha):

    asunto = 'Confirmación de tu reserva 💈'

    html_content = f"""
    <div style="
        background:#f4f4f4;
        padding:40px;
        font-family:Arial;
    ">

        <div style="
            max-width:700px;
            margin:auto;
            background:white;
            border-radius:15px;
            overflow:hidden;
            box-shadow:0 0 15px rgba(0,0,0,.1);
        ">

            <!-- HEADER -->
            <div style="
                background:black;
                color:white;
                padding:35px;
                text-align:center;
            ">

                <img
                    src="logo.png"
                    width="90"
                >

                <h1 style="margin-top:15px;">
                    Chicha Barber 💈
                </h1>

                <p>
                    Confirmación de reserva
                </p>

            </div>

            <!-- BODY -->
            <div style="padding:35px;">

                <h2>Hola {nombre} 👋</h2>

                <p>
                    Tu reserva ha sido registrada correctamente.
                </p>

                <h3 style="margin-top:25px;">
                    📅 Detalles de la cita
                </h3>

                <p><strong>Servicio:</strong> {servicio.nombre}</p>

                <p><strong>Fecha:</strong> {fecha.strftime('%Y-%m-%d %H:%M')}</p>
                
                <p><strong>Servicio:</strong> {servicio.precio}</p>
                

                <p style="margin-top:30px;">
                    Te esperamos en nuestra barbería ✂️
                </p>

            </div>

            <!-- FOOTER -->
            <div style="
                background:#111;
                color:#bbb;
                text-align:center;
                padding:20px;
                font-size:14px;
            ">
                © 2026 Chicha Barber
            </div>

        </div>

    </div>
    """

    connection = get_connection(ssl_context=ssl._create_unverified_context())

    email = EmailMultiAlternatives(
        asunto,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [correo_cliente],
        connection=connection
    )

    email.attach_alternative(html_content, "text/html")
    email.send()