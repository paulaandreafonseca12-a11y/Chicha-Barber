# ==========================================================
# POBLAR BASE DE DATOS - CHICHA BARBER STUDIO
# ==========================================================

import os
import django
import random

from datetime import date, time, timedelta
from decimal import Decimal


# ==========================================================
# CONFIGURACIÓN DJANGO
# ==========================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings"
)

django.setup()


# ==========================================================
# IMPORTACIONES
# ==========================================================

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify


from usuarios.models import (
    Usuario,
    Notificacion,
    HistorialAccion,
)


from servicios.models import (
    Servicios,
    Calificacion,
)


from reservas.models import (
    Agenda,
    Reserva,
)


from catalogo.models import (
    Categoria,
    Proveedor,
    Marca,
    Producto,
    DetalleProducto,
    MovimientoProducto,
    Promocion,
)


from compra.models import (
    Compra,
    DetalleCompra,
)


from venta.models import (
    Venta,
    DetalleVenta,
    DetallePagos,
)


from historial.models import (
    Bitacora,
)


from configuraciones.models import (
    Carrusel,
    Configuracion,
)


from soporte.models import (
    CategoriaAyuda,
    TicketSoporte,
)


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

random.seed(42)


# ==========================================================
# LIMPIAR BASE DE DATOS
# ==========================================================

def limpiar_datos():

    print("\n" + "=" * 60)
    print("LIMPIANDO BASE DE DATOS")
    print("=" * 60)

    # Soporte
    TicketSoporte.objects.all().delete()
    CategoriaAyuda.objects.all().delete()

    # Configuración
    Configuracion.objects.all().delete()
    Carrusel.objects.all().delete()

    # Historial
    Bitacora.objects.all().delete()

    # Pagos y ventas
    DetallePagos.objects.all().delete()
    DetalleVenta.objects.all().delete()
    Venta.objects.all().delete()

    # Compras
    DetalleCompra.objects.all().delete()
    Compra.objects.all().delete()

    # Movimientos
    MovimientoProducto.objects.all().delete()

    # Promociones
    Promocion.objects.all().delete()

    # Productos
    Producto.objects.all().delete()
    DetalleProducto.objects.all().delete()

    # Catálogo
    Marca.objects.all().delete()
    Categoria.objects.all().delete()
    Proveedor.objects.all().delete()

    # Reservas
    Reserva.objects.all().delete()
    Agenda.objects.all().delete()

    # Servicios
    Calificacion.objects.all().delete()
    Servicios.objects.all().delete()

    # Notificaciones e historial de usuarios
    Notificacion.objects.all().delete()
    HistorialAccion.objects.all().delete()

    # Usuarios
    Usuario.objects.all().delete()

    print("✓ Datos anteriores eliminados correctamente.")


# ==========================================================
# CREAR USUARIO
# ==========================================================

def crear_usuario(
    email,
    password,
    primer_nombre,
    segundo_nombre,
    primer_apellido,
    segundo_apellido,
    telefono,
    numero_documento,
    rol,
    tema="dark",
):

    usuario = Usuario.objects.create_user(
        email=email,
        password=password,
        primer_nombre=primer_nombre,
        segundo_nombre=segundo_nombre,
        primer_apellido=primer_apellido,
        segundo_apellido=segundo_apellido,
        telefono=telefono,
        estado=True,
        tipo_documento="CC",
        numero_documento=numero_documento,
        rol=rol,
        tema=tema,
    )

    return usuario


# ==========================================================
# USUARIOS
# ==========================================================

def poblar_usuarios():

    print("\nCreando usuarios...")

    admin = crear_usuario(
        "admin@chichabarber.com",
        "Admin123*",
        "Carlos",
        "Andrés",
        "Gómez",
        "Rodríguez",
        "3105550001",
        "1000000001",
        "admin",
    )

    barberos = []

    datos_barberos = [
        (
            "barbero1@chichabarber.com",
            "Juan",
            "David",
            "Pérez",
            "López",
            "3105550002",
            "1000000002",
        ),
        (
            "barbero2@chichabarber.com",
            "Andrés",
            "Felipe",
            "Martínez",
            "Rojas",
            "3105550003",
            "1000000003",
        ),
        (
            "barbero3@chichabarber.com",
            "Sebastián",
            "José",
            "Torres",
            "Moreno",
            "3105550004",
            "1000000004",
        ),
    ]

    for datos in datos_barberos:

        barbero = crear_usuario(
            datos[0],
            "Barbero123*",
            datos[1],
            datos[2],
            datos[3],
            datos[4],
            datos[5],
            datos[6],
            "barbero",
        )

        barberos.append(barbero)

    clientes = []

    datos_clientes = [
        (
            "cliente1@gmail.com",
            "Valentina",
            "Sofía",
            "García",
            "Martínez",
            "3115550011",
            "1000000011",
        ),
        (
            "cliente2@gmail.com",
            "Mateo",
            "Alejandro",
            "Rodríguez",
            "Pérez",
            "3115550012",
            "1000000012",
        ),
        (
            "cliente3@gmail.com",
            "Daniela",
            "María",
            "López",
            "Gómez",
            "3115550013",
            "1000000013",
        ),
        (
            "cliente4@gmail.com",
            "Nicolás",
            "Andrés",
            "Torres",
            "Rojas",
            "3115550014",
            "1000000014",
        ),
        (
            "cliente5@gmail.com",
            "Camila",
            "Isabella",
            "Moreno",
            "Díaz",
            "3115550015",
            "1000000015",
        ),
        (
            "cliente6@gmail.com",
            "Santiago",
            "David",
            "Castro",
            "Ramírez",
            "3115550016",
            "1000000016",
        ),
    ]

    for datos in datos_clientes:

        cliente = crear_usuario(
            datos[0],
            "Cliente123*",
            datos[1],
            datos[2],
            datos[3],
            datos[4],
            datos[5],
            datos[6],
            "cliente",
        )

        clientes.append(cliente)

    print(f"✓ Administradores: 1")
    print(f"✓ Barberos: {len(barberos)}")
    print(f"✓ Clientes: {len(clientes)}")

    return admin, barberos, clientes


# ==========================================================
# SERVICIOS
# ==========================================================

def poblar_servicios():

    print("\nCreando servicios...")

    datos = [
        (
            "Corte clásico",
            Decimal("18000"),
            30,
            "Corte tradicional con acabado profesional.",
        ),
        (
            "Corte moderno",
            Decimal("22000"),
            40,
            "Corte moderno personalizado según el estilo del cliente.",
        ),
        (
            "Corte + barba",
            Decimal("30000"),
            50,
            "Corte de cabello acompañado de arreglo completo de barba.",
        ),
        (
            "Barba premium",
            Decimal("18000"),
            30,
            "Perfilado, recorte y acabado profesional de barba.",
        ),
        (
            "Diseño de cejas",
            Decimal("10000"),
            15,
            "Diseño y perfilado profesional de cejas.",
        ),
        (
            "Corte infantil",
            Decimal("16000"),
            30,
            "Corte especialmente diseñado para niños.",
        ),
        (
            "Fade",
            Decimal("25000"),
            45,
            "Degradado profesional con acabado detallado.",
        ),
        (
            "Low fade",
            Decimal("23000"),
            40,
            "Degradado bajo con acabado moderno.",
        ),
        (
            "Mid fade",
            Decimal("24000"),
            40,
            "Degradado medio adaptado al estilo del cliente.",
        ),
        (
            "High fade",
            Decimal("26000"),
            45,
            "Degradado alto con acabado profesional.",
        ),
    ]

    servicios = []

    for nombre, precio, duracion, descripcion in datos:

        servicio = Servicios.objects.create(
            nombre=nombre,
            precio=precio,
            duracion=duracion,
            descripcion=descripcion,
            estado=True,
        )

        servicios.append(servicio)

    print(f"✓ Servicios creados: {len(servicios)}")

    return servicios


# ==========================================================
# CALIFICACIONES
# ==========================================================

def poblar_calificaciones(servicios, clientes):

    print("\nCreando calificaciones...")

    comentarios = [
        "Excelente servicio.",
        "Muy buen trabajo.",
        "El corte quedó excelente.",
        "Muy profesional.",
        "Excelente atención.",
        "Volveré nuevamente.",
        "Muy recomendado.",
    ]

    cantidad = 0

    for indice, servicio in enumerate(servicios):

        for numero in range(2):

            cliente = clientes[
                (indice + numero) % len(clientes)
            ]

            puntuacion = random.choice(
                [4, 5, 5, 5]
            )

            Calificacion.objects.create(
                servicio=servicio,
                cliente=cliente,
                cliente_nombre=cliente.get_full_name(),
                puntuacion=puntuacion,
                comentario=random.choice(comentarios),
                mostrar_en_inicio=True,
            )

            cantidad += 1

    print(f"✓ Calificaciones creadas: {cantidad}")


# ==========================================================
# CATEGORÍAS
# ==========================================================

def poblar_categorias():

    print("\nCreando categorías...")

    datos = [
        (
            "Cuidado capilar",
            "Productos para el cuidado y mantenimiento del cabello.",
        ),
        (
            "Barba",
            "Productos especializados para el cuidado de la barba.",
        ),
        (
            "Máquinas y herramientas",
            "Herramientas profesionales para barbería.",
        ),
        (
            "Styling",
            "Productos para peinado y fijación.",
        ),
        (
            "Aseo personal",
            "Productos complementarios para el cuidado personal.",
        ),
    ]

    categorias = []

    for nombre, descripcion in datos:

        categoria = Categoria.objects.create(
            nombre=nombre,
            descripcion=descripcion,
        )

        categorias.append(categoria)

    print(f"✓ Categorías creadas: {len(categorias)}")

    return categorias


# ==========================================================
# MARCAS
# ==========================================================

def poblar_marcas():

    print("\nCreando marcas...")

    datos = [
        (
            "Clubman Pinaud",
            "Productos tradicionales para barbería.",
        ),
        (
            "Suavecito",
            "Productos profesionales de styling.",
        ),
        (
            "Wahl",
            "Máquinas y herramientas profesionales.",
        ),
        (
            "Elegance",
            "Productos de cuidado y styling.",
        ),
        (
            "Reuzel",
            "Productos profesionales para cabello y barba.",
        ),
        (
            "American Crew",
            "Productos premium para cuidado masculino.",
        ),
    ]

    marcas = []

    for nombre, descripcion in datos:

        marca = Marca.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            estado=True,
        )

        marcas.append(marca)

    print(f"✓ Marcas creadas: {len(marcas)}")

    return marcas


# ==========================================================
# PROVEEDORES
# ==========================================================

def poblar_proveedores():

    print("\nCreando proveedores...")

    datos = [
        (
            "Distribuciones Barber Pro",
            "6015551001",
            "ventas@barberpro.com",
            "Bogotá",
        ),
        (
            "Importadora Style",
            "6015551002",
            "contacto@style.com",
            "Tunja",
        ),
        (
            "Comercializadora Groom",
            "6015551003",
            "ventas@groom.com",
            "Duitama",
        ),
        (
            "Beauty Supply Colombia",
            "6015551004",
            "info@beautysupply.com",
            "Bogotá",
        ),
    ]

    proveedores = []

    for nombre, telefono, correo, direccion in datos:

        proveedor = Proveedor.objects.create(
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
        )

        proveedores.append(proveedor)

    print(f"✓ Proveedores creados: {len(proveedores)}")

    return proveedores


# ==========================================================
# PRODUCTOS
# ==========================================================

def poblar_productos(categorias, marcas):

    print("\nCreando productos...")

    productos_data = [
        (
            "Pomada Suavecito Original",
            "Pomada de fijación media con acabado clásico.",
            Decimal("32000"),
            0,
            1,
        ),
        (
            "Pomada Reuzel Blue",
            "Pomada de alta fijación y brillo.",
            Decimal("48000"),
            3,
            1,
        ),
        (
            "Cera American Crew",
            "Cera profesional para diferentes estilos.",
            Decimal("42000"),
            0,
            5,
        ),
        (
            "Gel Elegance Extreme",
            "Gel de fijación fuerte para estilos definidos.",
            Decimal("18000"),
            3,
            3,
        ),
        (
            "After Shave Clubman",
            "Loción refrescante para después del afeitado.",
            Decimal("38000"),
            1,
            0,
        ),
        (
            "Aceite para barba Reuzel",
            "Aceite hidratante para barba.",
            Decimal("45000"),
            1,
            4,
        ),
        (
            "Máquina Wahl Magic Clip",
            "Máquina profesional para cortes y fades.",
            Decimal("620000"),
            2,
            2,
        ),
        (
            "Trimmer Wahl Detailer",
            "Perfiladora profesional para detalles.",
            Decimal("580000"),
            2,
            2,
        ),
        (
            "Shampoo American Crew",
            "Shampoo profesional para uso diario.",
            Decimal("52000"),
            0,
            5,
        ),
        (
            "Polvo texturizador Elegance",
            "Polvo para volumen y textura.",
            Decimal("28000"),
            3,
            3,
        ),
    ]

    productos = []

    for nombre, descripcion, precio, categoria_index, marca_index in productos_data:

        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            estado=True,
            codigo_categoria=categorias[categoria_index],
            codigo_marca=marcas[marca_index],
        )

        # El signal debe crear automáticamente el detalle.
        producto.refresh_from_db()

        detalle = producto.codigo_detalle_producto

        if detalle is None:

            raise RuntimeError(
                f"No se creó DetalleProducto para {producto.nombre}"
            )

        detalle.stock_min = 5
        detalle.stock_max = 50
        detalle.cantidad_actual = 0
        detalle.observaciones = (
            "Detalle creado automáticamente para el inventario."
        )

        detalle.save()

        productos.append(producto)

    print(f"✓ Productos creados: {len(productos)}")

    return productos


# ==========================================================
# PROMOCIONES
# ==========================================================

def poblar_promociones(productos, servicios):

    print("\nCreando promociones...")

    hoy = date.today()

    datos = [
        (
            "Semana del Fade",
            Decimal("15.00"),
            "Descuento especial para servicios Fade.",
            servicios[6],
            None,
        ),
        (
            "Barba Premium",
            Decimal("10.00"),
            "Descuento especial para barba premium.",
            servicios[3],
            None,
        ),
        (
            "Promo Suavecito",
            Decimal("12.00"),
            "Descuento en productos Suavecito.",
            None,
            productos[0],
        ),
        (
            "Cuidado de barba",
            Decimal("15.00"),
            "Descuento especial en aceite para barba.",
            None,
            productos[5],
        ),
        (
            "Styling profesional",
            Decimal("10.00"),
            "Promoción en productos de styling.",
            None,
            productos[9],
        ),
    ]

    promociones = []

    for nombre, porcentaje, descripcion, servicio, producto in datos:

        promocion = Promocion.objects.create(
            nombre=nombre,
            porcentaje_descuento=porcentaje,
            descripcion=descripcion,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            estado=True,
            codigo_servicio=servicio,
            codigo_producto=producto,
        )

        promociones.append(promocion)

    print(f"✓ Promociones creadas: {len(promociones)}")

    return promociones


# ==========================================================
# AGENDAS Y RESERVAS
# ==========================================================

def poblar_agendas_y_reservas(
    barberos,
    clientes,
    servicios,
):

    print("\nCreando agendas y reservas...")

    hoy = date.today()

    agendas = []
    reservas = []

    for dia in range(10):

        fecha = hoy + timedelta(days=dia)

        # No crear agenda los domingos
        if fecha.weekday() == 6:
            continue

        for indice_barbero, barbero in enumerate(barberos):

            for hora in range(8, 18):

                hora_inicio = time(
                    hour=hora,
                    minute=0,
                )

                hora_fin = time(
                    hour=hora + 1,
                    minute=0,
                )

                # Algunas agendas quedan reservadas
                reservar = (
                    (dia + hora + indice_barbero) % 7 == 0
                )

                estado = (
                    "reservada"
                    if reservar
                    else "disponible"
                )

                agenda = Agenda.objects.create(
                    profesional=barbero,
                    fecha=fecha,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    estado=estado,
                )

                agendas.append(agenda)

                if reservar:

                    cliente = clientes[
                        len(reservas) % len(clientes)
                    ]

                    servicio = servicios[
                        len(reservas) % len(servicios)
                    ]

                    estado_reserva = (
                        "confirmada"
                        if len(reservas) % 2 == 0
                        else "reservada"
                    )

                    reserva = Reserva.objects.create(
                        agenda=agenda,
                        usuario=cliente,
                        servicio=servicio,
                        observacion=(
                            "Reserva creada como dato de prueba."
                        ),
                        estado=estado_reserva,
                        nombre_usuario=(
                            cliente.get_full_name()
                        ),
                        correo_usuario=cliente.email,
                        telefono_usuario=cliente.telefono,
                    )

                    reservas.append(reserva)

    print(f"✓ Agendas creadas: {len(agendas)}")
    print(f"✓ Reservas creadas: {len(reservas)}")

    return agendas, reservas


# ==========================================================
# COMPRAS
# ==========================================================

def poblar_compras(proveedores, productos):

    print("\nCreando compras...")

    compras = []

    for indice, proveedor in enumerate(proveedores):

        compra = Compra.objects.create(
            codigo_proveedor=proveedor,
            observaciones=(
                f"Compra de inventario #{indice + 1}"
            ),
        )

        compras.append(compra)

        for posicion in range(3):

            producto = productos[
                (indice * 2 + posicion)
                % len(productos)
            ]

            precio_compra = (
                producto.precio * Decimal("0.60")
            ).quantize(
                Decimal("0.01")
            )

            precio_venta = producto.precio

            cantidad = 15 + (
                indice * 2
            ) + posicion

            DetalleCompra.objects.create(
                codigo_compra=compra,
                codigo_producto=producto,
                cantidad=cantidad,
                precio_compra=precio_compra,
                precio_venta=precio_venta,
            )

    print(f"✓ Compras creadas: {len(compras)}")

    return compras


# ==========================================================
# VENTAS
# ==========================================================

def poblar_ventas(clientes, productos):

    print("\nCreando ventas...")

    ventas = []

    metodos = [
        "efectivo",
        "tarjeta",
        "transferencia",
    ]

    for indice in range(8):

        cliente = clientes[
            indice % len(clientes)
        ]

        metodo = metodos[
            indice % len(metodos)
        ]

        venta = Venta.objects.create(
            codigo_usuario=cliente,
            nombre_cliente=cliente.get_full_name(),
            correo=cliente.email,
            telefono=cliente.telefono,
            direccion="Nobsa, Boyacá",
            metodo_pago=metodo,
            estado_pago="completado",
            total_venta=Decimal("0"),
        )

        productos_agregados = 0

        for posicion in range(2):

            producto = productos[
                (indice + posicion)
                % len(productos)
            ]

            producto.refresh_from_db()

            detalle_producto = (
                producto.codigo_detalle_producto
            )

            if not detalle_producto:
                continue

            stock = (
                detalle_producto.cantidad_actual
            )

            if stock <= 0:
                continue

            cantidad = min(
                2,
                stock
            )

            DetalleVenta.objects.create(
                codigo_venta=venta,
                codigo_producto=producto,
                cantidad=cantidad,
                valor_descuento=Decimal("0"),
            )

            productos_agregados += 1

        venta.refresh_from_db()

        # Crear detalle bancario únicamente
        # para ventas por transferencia.
        if metodo == "transferencia":

            DetallePagos.get_or_create_para_venta(
                venta,
                banco="Bancolombia",
                numero_cuenta="1234567890",
                tipo_cuenta="Ahorros",
                titular="Chicha Barber Studio",
                instrucciones=(
                    "Pago realizado mediante transferencia bancaria."
                ),
            )

        ventas.append(venta)

    print(f"✓ Ventas creadas: {len(ventas)}")

    return ventas


# ==========================================================
# HISTORIAL DE ACCIONES
# ==========================================================

def poblar_historial_acciones(
    admin,
    barberos,
    clientes,
):

    print("\nCreando historial de acciones...")

    registros = [
        (
            admin,
            "sistema",
            "crear",
            "Inicialización de la base de datos.",
        ),
        (
            admin,
            "usuario",
            "crear",
            "Creación del usuario administrador.",
        ),
        (
            barberos[0],
            "usuario",
            "crear",
            "Registro de barbero.",
        ),
        (
            clientes[0],
            "usuario",
            "crear",
            "Registro de cliente.",
        ),
        (
            admin,
            "producto",
            "crear",
            "Registro de productos del catálogo.",
        ),
        (
            admin,
            "categoria",
            "crear",
            "Registro de categorías.",
        ),
        (
            admin,
            "marca",
            "crear",
            "Registro de marcas.",
        ),
        (
            admin,
            "proveedor",
            "crear",
            "Registro de proveedores.",
        ),
        (
            admin,
            "promocion",
            "crear",
            "Registro de promociones.",
        ),
        (
            admin,
            "agenda",
            "crear",
            "Creación de horarios de atención.",
        ),
    ]

    historial = []

    for usuario, tipo, accion, descripcion in registros:

        registro = HistorialAccion.objects.create(
            usuario=usuario,
            tipo=tipo,
            accion=accion,
            descripcion=descripcion,
        )

        historial.append(registro)

    print(f"✓ Registros creados: {len(historial)}")

    return historial


# ==========================================================
# BITÁCORA
# ==========================================================

def poblar_bitacora(
    admin,
    productos,
):

    print("\nCreando bitácora...")

    registros = []

    acciones = [
        "Registro de producto",
        "Actualización de inventario",
        "Entrada de mercancía",
        "Salida de mercancía",
        "Consulta de producto",
        "Actualización de stock",
        "Registro de compra",
        "Registro de venta",
    ]

    modulos = [
        "catalogo",
        "compra",
        "venta",
        "inventario",
    ]

    for indice in range(12):

        producto = productos[
            indice % len(productos)
        ]

        registro = Bitacora.objects.create(
            codigo_usuario=admin,
            codigo_detalle_producto=(
                producto.codigo_detalle_producto
            ),
            accion=acciones[
                indice % len(acciones)
            ],
            modulo=modulos[
                indice % len(modulos)
            ],
            descripcion=(
                f"Registro de prueba #{indice + 1} "
                f"para el producto {producto.nombre}."
            ),
            ip_origen="127.0.0.1",
        )

        registros.append(registro)

    print(f"✓ Registros de bitácora: {len(registros)}")

    return registros


# ==========================================================
# CARRUSEL
# ==========================================================

def poblar_carrusel():

    print("\nCreando carrusel...")

    datos = [
        (
            "Potencia & Estilo",
            "Cortes modernos y atención profesional.",
        ),
        (
            "Cortes Premium",
            "Encuentra el estilo perfecto para ti.",
        ),
        (
            "Barba Profesional",
            "Cuidado y diseño para una barba impecable.",
        ),
        (
            "Productos Profesionales",
            "Los mejores productos para tu estilo.",
        ),
    ]

    carruseles = []

    for nombre, texto in datos:

        carrusel = Carrusel.objects.create(
            nombre=nombre,
            texto=texto,
            estado=True,
        )

        carruseles.append(carrusel)

    print(f"✓ Carruseles creados: {len(carruseles)}")

    return carruseles


# ==========================================================
# CONFIGURACIONES
# ==========================================================

def poblar_configuraciones(
    admin,
    carruseles,
    historial,
):

    print("\nCreando configuraciones...")

    configuraciones = []

    datos = [
        (
            "Configuración principal",
            "Configuración general del sistema Chicha Barber.",
        ),
        (
            "Configuración del carrusel",
            "Configuración de imágenes y mensajes principales.",
        ),
        (
            "Configuración de reservas",
            "Configuración general para las reservas.",
        ),
    ]

    for indice, (nombre, descripcion) in enumerate(datos):

        registro_historial = (
            historial[indice]
            if indice < len(historial)
            else None
        )

        configuracion = Configuracion.objects.create(
            codigo_usuario=admin,
            codigo_carrusel=(
                carruseles[indice]
                if indice < len(carruseles)
                else None
            ),
            codigo_historial=registro_historial,
            fecha_realizacion=timezone.now(),
            nombre=nombre,
            descripcion=descripcion,
            estado=True,
        )

        configuraciones.append(configuracion)

    print(
        f"✓ Configuraciones creadas: "
        f"{len(configuraciones)}"
    )

    return configuraciones


# ==========================================================
# SOPORTE
# ==========================================================

def poblar_soporte(clientes):

    print("\nCreando módulo de soporte...")

    categorias_data = [
        (
            "Reservas",
            "Ayuda relacionada con reservas y agendas.",
            "bi bi-calendar-check",
        ),
        (
            "Pagos",
            "Problemas relacionados con pagos y compras.",
            "bi bi-credit-card",
        ),
        (
            "Productos",
            "Consultas relacionadas con productos.",
            "bi bi-box-seam",
        ),
        (
            "Cuenta",
            "Ayuda relacionada con la cuenta del usuario.",
            "bi bi-person-circle",
        ),
    ]

    categorias = []

    for nombre, descripcion, icono in categorias_data:

        categoria = CategoriaAyuda.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            icono=icono,
            slug=slugify(nombre),
        )

        categorias.append(categoria)

    tickets_data = [
        (
            0,
            0,
            "Consulta sobre reserva",
            "Necesito información sobre una reserva.",
        ),
        (
            1,
            1,
            "Consulta sobre pago",
            "Quiero confirmar el estado de mi pago.",
        ),
        (
            2,
            2,
            "Consulta sobre producto",
            "Quiero conocer la disponibilidad de un producto.",
        ),
        (
            3,
            3,
            "Problema con mi cuenta",
            "Necesito ayuda con mi cuenta.",
        ),
    ]

    tickets = []

    for cliente_index, categoria_index, asunto, descripcion in tickets_data:

        ticket = TicketSoporte.objects.create(
            usuario=clientes[
                cliente_index
                % len(clientes)
            ],
            categoria=categorias[
                categoria_index
            ],
            asunto=asunto,
            descripcion=descripcion,
            estado="ABIERTO",
        )

        tickets.append(ticket)

    print(
        f"✓ Categorías de ayuda: "
        f"{len(categorias)}"
    )

    print(
        f"✓ Tickets creados: "
        f"{len(tickets)}"
    )

    return categorias, tickets


# ==========================================================
# NOTIFICACIONES
# ==========================================================

def poblar_notificaciones(
    admin,
    barberos,
    clientes,
):

    print("\nCreando notificaciones...")

    notificaciones = []

    datos = [
        (
            admin,
            "sistema",
            "La base de datos fue inicializada correctamente.",
            "/",
        ),
        (
            clientes[0],
            "reserva",
            "Tu reserva fue registrada correctamente.",
            "/reservas/",
        ),
        (
            clientes[1],
            "sistema",
            "Bienvenido a Chicha Barber Studio.",
            "/",
        ),
        (
            barberos[0],
            "agenda",
            "Tienes nuevas reservas asignadas.",
            "/reservas/",
        ),
    ]

    for usuario, tipo, mensaje, url in datos:

        notificacion = Notificacion.objects.create(
            usuario=usuario,
            tipo=tipo,
            mensaje=mensaje,
            url=url,
            leida=False,
        )

        notificaciones.append(notificacion)

    print(
        f"✓ Notificaciones creadas: "
        f"{len(notificaciones)}"
    )

    return notificaciones


# ==========================================================
# FUNCIÓN PRINCIPAL
# ==========================================================

@transaction.atomic
def poblar_base_datos():

    print("\n")
    print("=" * 60)
    print("      CHICHA BARBER STUDIO")
    print("      POBLACIÓN DE BASE DE DATOS")
    print("=" * 60)

    # ------------------------------------------------------
    # 1. LIMPIAR
    # ------------------------------------------------------

    limpiar_datos()

    # ------------------------------------------------------
    # 2. USUARIOS
    # ------------------------------------------------------

    admin, barberos, clientes = poblar_usuarios()

    # ------------------------------------------------------
    # 3. SERVICIOS
    # ------------------------------------------------------

    servicios = poblar_servicios()

    # ------------------------------------------------------
    # 4. CALIFICACIONES
    # ------------------------------------------------------

    poblar_calificaciones(
        servicios,
        clientes,
    )

    # ------------------------------------------------------
    # 5. CATEGORÍAS
    # ------------------------------------------------------

    categorias = poblar_categorias()

    # ------------------------------------------------------
    # 6. MARCAS
    # ------------------------------------------------------

    marcas = poblar_marcas()

    # ------------------------------------------------------
    # 7. PROVEEDORES
    # ------------------------------------------------------

    proveedores = poblar_proveedores()

    # ------------------------------------------------------
    # 8. PRODUCTOS
    # ------------------------------------------------------

    productos = poblar_productos(
        categorias,
        marcas,
    )

    # ------------------------------------------------------
    # 9. PROMOCIONES
    # ------------------------------------------------------

    poblar_promociones(
        productos,
        servicios,
    )

    # ------------------------------------------------------
    # 10. AGENDAS Y RESERVAS
    # ------------------------------------------------------

    poblar_agendas_y_reservas(
        barberos,
        clientes,
        servicios,
    )

    # ------------------------------------------------------
    # 11. COMPRAS
    # ------------------------------------------------------

    poblar_compras(
        proveedores,
        productos,
    )

    # ------------------------------------------------------
    # 12. VENTAS
    # ------------------------------------------------------

    poblar_ventas(
        clientes,
        productos,
    )

    # ------------------------------------------------------
    # 13. HISTORIAL
    # ------------------------------------------------------

    historial = poblar_historial_acciones(
        admin,
        barberos,
        clientes,
    )

    # ------------------------------------------------------
    # 14. BITÁCORA
    # ------------------------------------------------------

    poblar_bitacora(
        admin,
        productos,
    )

    # ------------------------------------------------------
    # 15. CARRUSEL
    # ------------------------------------------------------

    carruseles = poblar_carrusel()

    # ------------------------------------------------------
    # 16. CONFIGURACIONES
    # ------------------------------------------------------

    poblar_configuraciones(
        admin,
        carruseles,
        historial,
    )

    # ------------------------------------------------------
    # 17. SOPORTE
    # ------------------------------------------------------

    poblar_soporte(
        clientes,
    )

    # ------------------------------------------------------
    # 18. NOTIFICACIONES
    # ------------------------------------------------------

    poblar_notificaciones(
        admin,
        barberos,
        clientes,
    )

    # ------------------------------------------------------
    # FINAL
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("      BASE DE DATOS POBLADA CORRECTAMENTE")
    print("=" * 60)

    print("\nUSUARIOS DE PRUEBA")
    print("-" * 60)

    print(
        "Administrador:"
        "\n  Correo: admin@chichabarber.com"
        "\n  Contraseña: Admin123*"
    )

    print(
        "\nBarberos:"
        "\n  Correo: barbero1@chichabarber.com"
        "\n  Contraseña: Barbero123*"
    )

    print(
        "\nClientes:"
        "\n  Correo: cliente1@gmail.com"
        "\n  Contraseña: Cliente123*"
    )

    print("\n" + "=" * 60)
    print("Puedes iniciar el servidor con:")
    print("python manage.py runserver")
    print("=" * 60)


# ==========================================================
# EJECUTAR
# ==========================================================

if __name__ == "__main__":

    try:

        poblar_base_datos()

    except Exception as error:

        print("\n" + "=" * 60)
        print("ERROR AL POBLAR LA BASE DE DATOS")
        print("=" * 60)

        print(
            f"\n{type(error).__name__}: {error}"
        )

        print(
            "\nLa transacción fue cancelada "
            "y los cambios realizados durante "
            "esta ejecución no se conservarán."
        )

        raise