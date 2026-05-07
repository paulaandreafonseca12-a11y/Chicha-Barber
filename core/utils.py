from django.core.mail import EmailMultiAlternatives
from django.conf import settings


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

    email = EmailMultiAlternatives(
        asunto,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [correo_cliente]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

