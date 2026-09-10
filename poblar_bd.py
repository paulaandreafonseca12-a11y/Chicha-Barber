"""
==============================================================================
CHICHA BARBER STUDIO - SCRIPT DE POBLACIÓN DE BASE DE DATOS
==============================================================================
Este script puebla la base de datos de Chicha Barber con datos coherentes,
realistas y completamente alineados con la arquitectura actual de modelos:
  - usuarios: Usuario, RegistroActividad, Notificacion
  - servicios: Servicios, Calificacion
  - reservas: Agenda, Reserva
  - catalogo: Categoria, Marca, Proveedor, DetalleProducto, Producto,
              MovimientoProducto, Promocion
  - compra: Compra, DetalleCompra
  - venta: Venta, DetalleVenta, DetallePagos
  - configuraciones: Carrusel, Configuracion
  - historial: Bitacora
 
==============================================================================
"""

import os
import sys
import random
from decimal import Decimal
from datetime import date, time, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests
from django.core.files.base import ContentFile
from django.utils import timezone


# ============================================================================
# 1. CONFIGURACIÓN DE DJANGO
# ============================================================================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()


# ============================================================================
# 2. IMPORTACIÓN DE MODELOS
# ============================================================================
from usuarios.models import Usuario, HistorialAccion, Notificacion, RolUsuario, TipoDocumento
from servicios.models import Servicios, Calificacion
from reservas.models import Agenda, Reserva
from catalogo.models import (
    Categoria,
    Marca,
    Proveedor,
    DetalleProducto,
    Producto,
    MovimientoProducto,
    Promocion,
)
from compra.models import Compra, DetalleCompra
from venta.models import Venta, DetalleVenta, DetallePagos
from configuraciones.models import Carrusel, Configuracion
from historial.models import Bitacora



# ============================================================================
# 3. LIMPIEZA DE DATOS (ORDEN ESTRICTO DE INTEGRIDAD REFERENCIAL)
# ============================================================================
def limpiar_datos():
    print("\n" + "=" * 60)
    print(" 1. LIMPIEZA DE BASE DE DATOS")
    print("=" * 60)

    

        # Historial
    Bitacora.objects.all().delete()
    print("  ✓ Bitácora limpiada.")

        # Configuraciones
    Configuracion.objects.all().delete()
    Carrusel.objects.all().delete()
    print("  ✓ Configuraciones y Carrusel limpiados.")

        # Ventas
    DetallePagos.objects.all().delete()
    DetalleVenta.objects.all().delete()
    Venta.objects.all().delete()
    print("  ✓ Ventas, detalles y pagos limpiados.")

        # Compras
    DetalleCompra.objects.all().delete()
    Compra.objects.all().delete()
    print("  ✓ Compras y detalles limpiados.")

        # Catálogo
    Promocion.objects.all().delete()
    MovimientoProducto.objects.all().delete()
    Producto.objects.all().delete()
    DetalleProducto.objects.all().delete()
    Marca.objects.all().delete()
    Proveedor.objects.all().delete()
    Categoria.objects.all().delete()
    print("  ✓ Catálogo de productos e inventario limpiados.")

        # Reservas y Servicios
    Reserva.objects.all().delete()
    Agenda.objects.all().delete()
    Calificacion.objects.all().delete()
    Servicios.objects.all().delete()
    print("  ✓ Reservas, agendas, calificaciones y servicios limpiados.")

        # Notificaciones y Actividades
    Notificacion.objects.all().delete()
    HistorialAccion.objects.all().delete()

        # Usuarios de prueba (conservar solo si se desea el admin personalizado)
    Usuario.objects.exclude(email="a@b.com").delete()
    print("  ✓ Usuarios anteriores limpiados.")

    print("=> Base de datos preparada para inserción limpia.")
    
   


# ============================================================================
# 4. UTILIDAD PARA AVATARES
# ============================================================================
def descargar_avatar(nombre_completo, email):
    """Descarga un avatar ilustrativo para los perfiles."""
    try:
        url = (
            f"https://ui-avatars.com/api/?name={nombre_completo.replace(' ', '+')}"
            f"&background=111827&color=fbbf24&size=200&bold=true"
        )
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            nombre_archivo = f"avatar_{email.split('@')[0]}.png"
            return nombre_archivo, ContentFile(resp.content)
    except Exception:
        pass
    return None, None


# ============================================================================
# 5. POBLAR USUARIOS, REGISTROS DE ACTIVIDAD Y NOTIFICACIONES
# ============================================================================
def poblar_usuarios():
    print("\n" + "=" * 60)
    print(" 2. POBLANDO USUARIOS Y PERFILES")
    print("=" * 60)

    # ------------------------------------------------------------------------
    # 5.1 Administrador Principal
    # ------------------------------------------------------------------------
    admin, created = Usuario.objects.get_or_create(
        email="a@b.com",
        defaults={
            "primer_nombre": "Admin",
            "segundo_nombre": "Principal",
            "primer_apellido": "Chicha",
            "segundo_apellido": "Barber",
            "telefono": "3000000000",
            "tipo_documento": TipoDocumento.CC,
            "numero_documento": "1000000000",
            "rol": RolUsuario.ADMIN,
            "estado": True,
        }
    )
    admin.set_password("@dmin123")
    admin.save()
    print(f"  ✓ Administrador principal configurado: {admin.email} / @dmin123")

    # ------------------------------------------------------------------------
    # 5.2 Barberos Profesionales
    # ------------------------------------------------------------------------
    barberos_data = [
        {
            "primer_nombre": "Carlos",
            "segundo_nombre": "Andrés",
            "primer_apellido": "López",
            "segundo_apellido": "Gómez",
            "email": "barbero1@ejemplo.com",
            "telefono": "3101234561",
            "tipo_documento": TipoDocumento.CC,
            "numero_documento": "2000000001",
            "rol": RolUsuario.BARBERO,
        },
        {
            "primer_nombre": "Juan",
            "segundo_nombre": "David",
            "primer_apellido": "García",
            "segundo_apellido": "Mendoza",
            "email": "barbero2@ejemplo.com",
            "telefono": "3101234562",
            "tipo_documento": TipoDocumento.CC,
            "numero_documento": "2000000002",
            "rol": RolUsuario.BARBERO,
        },
        {
            "primer_nombre": "Andrés",
            "segundo_nombre": "Felipe",
            "primer_apellido": "Martínez",
            "segundo_apellido": "Silva",
            "email": "barbero3@ejemplo.com",
            "telefono": "3101234563",
            "tipo_documento": TipoDocumento.CC,
            "numero_documento": "2000000003",
            "rol": RolUsuario.BARBERO,
        },
    ]

    barberos = []
    for b_data in barberos_data:
        b_usuario, _ = Usuario.objects.get_or_create(
            email=b_data["email"],
            defaults=b_data
        )
        b_usuario.set_password("Password123!")
        nombre_completo = b_usuario.get_full_name()
        fn, cont = descargar_avatar(nombre_completo, b_usuario.email)
        if fn and cont:
            b_usuario.foto_perfil.save(fn, cont, save=False)
        b_usuario.save()
        barberos.append(b_usuario)
        print(f"  ✓ Barbero registrado: {nombre_completo} ({b_usuario.email})")

    # ------------------------------------------------------------------------
    # 5.3 Clientes Registrados
    # ------------------------------------------------------------------------
    clientes_data = [
        ("Mateo", "Valencia", "Rojas", "cliente1@ejemplo.com", "3001234501", "1000000001"),
        ("Sebastián", "Hernández", "Castro", "cliente2@ejemplo.com", "3001234502", "1000000002"),
        ("Daniel", "Ortiz", "Navarro", "cliente3@ejemplo.com", "3001234503", "1000000003"),
        ("Alejandro", "Morales", "Pérez", "cliente4@ejemplo.com", "3001234504", "1000000004"),
        ("Camilo", "Ramírez", "Díaz", "cliente5@ejemplo.com", "3001234505", "1000000005"),
        ("Nicolás", "Vargas", "Torres", "cliente6@ejemplo.com", "3001234506", "1000000006"),
    ]

    clientes = []
    for p_nom, p_ape, s_ape, em, tel, doc in clientes_data:
        c_usuario, _ = Usuario.objects.get_or_create(
            email=em,
            defaults={
                "primer_nombre": p_nom,
                "primer_apellido": p_ape,
                "segundo_apellido": s_ape,
                "email": em,
                "telefono": tel,
                "tipo_documento": TipoDocumento.CC,
                "numero_documento": doc,
                "rol": RolUsuario.CLIENTE,
                "estado": True,
            }
        )
        c_usuario.set_password("Password123!")
        c_usuario.save()
        clientes.append(c_usuario)
        print(f"  ✓ Cliente registrado: {c_usuario.get_full_name()} ({em})")

    # ------------------------------------------------------------------------
    # 5.4 Actividad Inicial y Notificaciones
    # ------------------------------------------------------------------------
    HistorialAccion.objects.create(
        usuario=admin,
        tipo="sesion",
        descripcion="Inicio de sesión administrativo inicial"
    )
    HistorialAccion.objects.create(
        usuario=admin,
        tipo="usuario",
        descripcion="Configuración general del personal de barberos"
    )

    for c in clientes[:3]:
        Notificacion.objects.create(
            usuario=c,
            tipo="reserva",
            mensaje="¡Bienvenido a Chicha Barber! Ya puedes agendar tu turno.",
            url="/reservas/",
            leida=False
        )

    return admin, barberos, clientes


# ============================================================================
# 6. POBLAR SERVICIOS Y CALIFICACIONES
# ============================================================================
def poblar_servicios(clientes):
    print("\n" + "=" * 60)
    print(" 3. POBLANDO SERVICIOS Y CALIFICACIONES")
    print("=" * 60)

    servicios_data = [
        {
            "nombre": "Corte Clásico Caballero",
            "precio": Decimal("25000.00"),
            "duracion": 30,
            "descripcion": "Corte tradicional a tijera o máquina con acabado limpio, lavado rápido y peinado profesional.",
        },
        {
            "nombre": "Degradado / Fade Urbano",
            "precio": Decimal("30000.00"),
            "duracion": 45,
            "descripcion": "Degradado de alta precisión (Low, Mid, High Fade) con navaja y perfilado milimétrico.",
        },
        {
            "nombre": "Arreglo y Perfilado de Barba",
            "precio": Decimal("20000.00"),
            "duracion": 30,
            "descripcion": "Diseño y definición de líneas con toalla caliente, aceite hidratante y bálsamo premium.",
        },
        {
            "nombre": "Combo Chicha Premium (Corte + Barba)",
            "precio": Decimal("48000.00"),
            "duracion": 60,
            "descripcion": "La experiencia completa: corte personalizado, perfilado de barba, toalla caliente y tónico facial.",
        },
        {
            "nombre": "Perfilado de Cejas con Navaja",
            "precio": Decimal("10000.00"),
            "duracion": 15,
            "descripcion": "Limpieza y arqueo natural de cejas masculinas con navaja desechable higienizada.",
        },
        {
            "nombre": "Tinte y Camuflaje de Canas",
            "precio": Decimal("50000.00"),
            "duracion": 60,
            "descripcion": "Colorimetría capilar para cobertura de canas o cambio de tono natural con productos sin amoniaco.",
        },
        {
            "nombre": "Limpieza Facial Black Mask",
            "precio": Decimal("35000.00"),
            "duracion": 40,
            "descripcion": "Exfoliación facial, vapor de ozono, extracción de impurezas y mascarilla negra purificante.",
        },
        {
            "nombre": "Corte Infantil (Niños)",
            "precio": Decimal("22000.00"),
            "duracion": 30,
            "descripcion": "Atención paciente y divertida para los más pequeños, con diseños o cortes modernos a su gusto.",
        },
        {
            "nombre": "Masaje Capilar y Tratamiento Anticaída",
            "precio": Decimal("28000.00"),
            "duracion": 25,
            "descripcion": "Terapia estimulante del cuero cabelludo con tónico mentolado y masaje relajante.",
        },
        {
            "nombre": "Afeitado Tradicional Toalla Caliente",
            "precio": Decimal("26000.00"),
            "duracion": 35,
            "descripcion": "Ritual clásico con espuma cremosa al calor, doble toalla caliente y aftershave refrescante.",
        },
    ]

    servicios_creados = []
    for s_item in servicios_data:
        serv, _ = Servicios.objects.get_or_create(
            nombre=s_item["nombre"],
            defaults={
                "precio": s_item["precio"],
                "duracion": s_item["duracion"],
                "descripcion": s_item["descripcion"],
                "estado": True,
            }
        )
        servicios_creados.append(serv)
        print(f"  ✓ Servicio creado: {serv.nombre} (${serv.precio:,.0f} - {serv.duracion} min)")

    # ------------------------------------------------------------------------
    # Calificaciones de los Servicios
    # ------------------------------------------------------------------------
    testimonios = [
        (5, "¡El mejor corte que me han hecho en la ciudad! Atención impecable."),
        (5, "El arreglo de barba con toalla caliente es una experiencia de otro nivel."),
        (4, "Excelente técnica con la navaja y el degradado quedó perfecto."),
        (5, "Ambiente agradable, buena música y puntualidad con el turno."),
        (4, "Muy profesionales, usan productos de alta gama que dejan el cabello impecable."),
        (5, "Recomiendo totalmente el Combo Chicha. Vale cada peso."),
    ]

    for idx, serv in enumerate(servicios_creados):
        for _ in range(random.randint(1, 3)):
            cliente_azar = random.choice(clientes)
            punt, comen = random.choice(testimonios)
            Calificacion.objects.create(
                servicio=serv,
                cliente=cliente_azar,
                cliente_nombre=cliente_azar.get_full_name(),
                puntuacion=punt,
                comentario=comen,
                mostrar_en_inicio=(punt == 5 and random.choice([True, False]))
            )

    print(f"  ✓ Calificaciones generadas para todos los servicios.")
    return servicios_creados


# ============================================================================
# 7. POBLAR AGENDAS Y RESERVAS
# ============================================================================
def poblar_agendas_y_reservas(barberos, clientes, servicios):
    print("\n" + "=" * 60)
    print(" 4. POBLANDO AGENDAS Y RESERVAS")
    print("=" * 60)

    horarios = [
        (time(8, 0), time(9, 0)),
        (time(9, 0), time(10, 0)),
        (time(10, 0), time(11, 0)),
        (time(11, 0), time(12, 0)),
        (time(14, 0), time(15, 0)),
        (time(15, 0), time(16, 0)),
        (time(16, 0), time(17, 0)),
        (time(17, 0), time(18, 0)),
    ]

    total_agendas = 0
    total_reservas = 0
    hoy = date.today()

    # Generar agendas para los próximos 10 días
    for d in range(1, 11):
        dia_fecha = hoy + timedelta(days=d)
        if dia_fecha.weekday() == 6:  # Omitir domingos
            continue

        for barbero in barberos:
            for h_ini, h_fin in horarios:
                # 70% disponible, 30% reservada
                es_reservada = random.random() < 0.35
                estado_agenda = "reservada" if es_reservada else "disponible"

                agenda = Agenda.objects.create(
                    profesional=barbero,
                    fecha=dia_fecha,
                    hora_inicio=h_ini,
                    hora_fin=h_fin,
                    estado=estado_agenda,
                )
                total_agendas += 1

                if es_reservada:
                    cliente_res = random.choice(clientes)
                    servicio_res = random.choice(servicios)
                    dt_reserva = timezone.make_aware(
                        timezone.datetime.combine(dia_fecha, h_ini)
                    )

                    Reserva.objects.create(
                        agenda=agenda,
                        usuario=cliente_res,
                        servicio=servicio_res,
                        observacion="Cliente solicitó puntualidad y peinado con cera mate.",
                        estado=random.choice(["confirmada", "reservada"]),
                        nombre_usuario=cliente_res.get_full_name(),
                        correo_usuario=cliente_res.email,
                        telefono_usuario=cliente_res.telefono,
                        fecha_reserva=dt_reserva,
                        precio_historico=servicio_res.precio,
                    )
                    total_reservas += 1

    print(f"  ✓ {total_agendas} bloques de Agenda creados.")
    print(f"  ✓ {total_reservas} Reservas asociadas y confirmadas creadas.")


# ============================================================================
# 8. POBLAR CATÁLOGO (CATEGORÍAS, MARCAS, PROVEEDORES, PRODUCTOS, EXISTENCIAS)
# ============================================================================
def poblar_catalogo(servicios):
    print("\n" + "=" * 60)
    print(" 5. POBLANDO CATÁLOGO, PRODUCTOS E INVENTARIO")
    print("=" * 60)

    # ------------------------------------------------------------------------
    # 8.1 Categorías
    # ------------------------------------------------------------------------
    categorias_data = [
        ("Cuidado Capilar", "Ceras, pomadas, geles y champús de alto rendimiento."),
        ("Cuidado de Barba", "Aceites nutritivos, bálsamos estilizadores y tónicos para vello facial."),
        ("Afeitado Clásico", "Espumas, lociones aftershave y cremas para corte tradicional."),
        ("Herramientas y Accesorios", "Navajas shavette, peines de madera antiestática y brochas."),
        ("Cuidado Facial", "Exfoliantes, mascarillas limpiadoras y geles hidratantes masculinos."),
    ]
    categorias = []
    for nom, desc in categorias_data:
        cat, _ = Categoria.objects.get_or_create(
            nombre=nom,
            defaults={"descripcion": desc}
        )
        categorias.append(cat)
        print(f"  ✓ Categoría: {cat.nombre}")

    # ------------------------------------------------------------------------
    # 8.2 Marcas
    # ------------------------------------------------------------------------
    marcas_data = [
        ("Suavecito Pomade", "Marca icónica estadounidense de pomadas al agua y fijadores clásicos.", True),
        ("Wahl Professional", "Referente global de máquinas y navajas profesionales de corte.", True),
        ("Clubman Pinaud", "Línea histórica de barbería tradicional y aftershaves reconocidos.", True),
        ("Elegance Studio", "Productos modernos para estilismo, gel fijador y cuidado facial.", True),
        ("Reuzel Holland", "Gama premium de pomadas y bálsamos fundada por Schorem en Róterdam.", True),
        ("American Crew", "Cuidado personal de alta gama para el hombre contemporáneo.", True),
    ]
    marcas = []
    for nom, desc, est in marcas_data:
        m, _ = Marca.objects.get_or_create(
            nombre=nom,
            defaults={"descripcion": desc, "estado": est}
        )
        marcas.append(m)
        print(f"  ✓ Marca: {m.nombre}")

    # ------------------------------------------------------------------------
    # 8.3 Proveedores
    # ------------------------------------------------------------------------
    proveedores_data = [
        ("Distribuidora Barber Pros", "3112345678", "ventas@barberpros.com", "Cra 45 # 20-30, Bogotá"),
        ("Suministros Estilo Total", "3223456789", "info@estilototal.com", "Cll 10 # 5-40, Medellín"),
        ("Importadora Barbershop SAS", "3009876543", "contacto@barbersas.com", "Av 68 # 72-15, Cali"),
    ]
    proveedores = []
    for nom, tel, cor, dir_p in proveedores_data:
        prov, _ = Proveedor.objects.get_or_create(
            nombre=nom,
            defaults={
                "telefono": tel,
                "correo": cor,
                "direccion": dir_p,
            }
        )
        proveedores.append(prov)
        print(f"  ✓ Proveedor: {prov.nombre}")

    # ------------------------------------------------------------------------
    # 8.4 Productos y Detalle de Stock
    # ------------------------------------------------------------------------
    productos_info = [
        {
            "nombre": "Pomada Suavecito",
            "categoria": "Cuidado Capilar",
            "marca": "Suavecito Pomade",
            "precio": Decimal("65000.00"),
            "stock": 35,
            "min": 5,
            "max": 80,
            "desc": "Pomada soluble en agua con fijación extra firme y aroma característico suave.",
        },
        {
            "nombre": "Cera Mate Fijación Media Elegance",
            "categoria": "Cuidado Capilar",
            "marca": "Elegance Studio",
            "precio": Decimal("45000.00"),
            "stock": 40,
            "min": 8,
            "max": 90,
            "desc": "Acabado mate sin brillo, excelente textura y moldeado natural todo el día.",
        },
        {
            "nombre": "Aceite Nutritivo para Barba Clubman",
            "categoria": "Cuidado de Barba",
            "marca": "Clubman Pinaud",
            "precio": Decimal("42000.00"),
            "stock": 25,
            "min": 5,
            "max": 50,
            "desc": "Mezcla de aceites de macadamia y kukui que hidratan la piel y suavizan la barba.",
        },
        {
            "nombre": "Bálsamo Hidratante Reuzel Wood & Spice",
            "categoria": "Cuidado de Barba",
            "marca": "Reuzel Holland",
            "precio": Decimal("58000.00"),
            "stock": 30,
            "min": 5,
            "max": 60,
            "desc": "Formulado con manteca de karité y aceite de argán para domar y dar cuerpo a la barba.",
        },
        {
            "nombre": "Loción After Shave Clásica Clubman",
            "categoria": "Afeitado Clásico",
            "marca": "Clubman Pinaud",
            "precio": Decimal("48000.00"),
            "stock": 28,
            "min": 6,
            "max": 60,
            "desc": "La loción clásica que refresca, calma la piel tras el afeitado y previene la irritación.",
        },
        {
            "nombre": "Navaja Shavette Profesional Wahl",
            "categoria": "Herramientas y Accesorios",
            "marca": "Wahl Professional",
            "precio": Decimal("35000.00"),
            "stock": 20,
            "min": 4,
            "max": 40,
            "desc": "Navaja de acero inoxidable con seguro de cuchilla para perfilados y afeitados limpios.",
        },
        {
            "nombre": "Brocha de Afeitar Cerda Natural Wahl",
            "categoria": "Herramientas y Accesorios",
            "marca": "Wahl Professional",
            "precio": Decimal("32000.00"),
            "stock": 18,
            "min": 4,
            "max": 35,
            "desc": "Brocha densa que genera abundante espuma y masajea suavemente la piel del rostro.",
        },
        {
            "nombre": "Gel Exfoliante Facial Carbón Activado",
            "categoria": "Cuidado Facial",
            "marca": "Elegance Studio",
            "precio": Decimal("38000.00"),
            "stock": 30,
            "min": 5,
            "max": 50,
            "desc": "Elimina células muertas y puntos negros dejando la piel suave y renovada.",
        },
        {
            "nombre": "Champú Anticaspa Revitalizante American Crew",
            "categoria": "Cuidado Capilar",
            "marca": "American Crew",
            "precio": Decimal("52000.00"),
            "stock": 22,
            "min": 5,
            "max": 50,
            "desc": "Fórmula con piritionato de zinc que combate la caspa y regula el cuero cabelludo.",
        },
        {
            "nombre": "Tónico Capilar Refrescante Reuzel Grooming",
            "categoria": "Cuidado Capilar",
            "marca": "Reuzel Holland",
            "precio": Decimal("46000.00"),
            "stock": 26,
            "min": 5,
            "max": 50,
            "desc": "Tónico fijador suave con romero y hamamelis para preparar el peinado con secador.",
        },
    ]

    cat_map = {c.nombre: c for c in categorias}
    marca_map = {m.nombre: m for m in marcas}

    productos_creados = []
    for item in productos_info:
        cat_obj = cat_map[item["categoria"]]
        marca_obj = marca_map[item["marca"]]

        # 1. Crear producto (la señal post_save crea el DetalleProducto inicial)
        prod = Producto.objects.create(
            nombre=item["nombre"],
            descripcion=item["desc"],
            precio=item["precio"],
            codigo_categoria=cat_obj,
            codigo_marca=marca_obj,
            estado=True,
        )

        # 2. Configurar inventario inicial en DetalleProducto
        detalle = prod.codigo_detalle_producto
        if not detalle:
            detalle = DetalleProducto.objects.create(
                cantidad_actual=item["stock"],
                stock_min=item["min"],
                stock_max=item["max"],
                observaciones="Inventario inicial cargado por script de población."
            )
            prod.codigo_detalle_producto = detalle
            prod.save(update_fields=["codigo_detalle_producto"])
        else:
            detalle.cantidad_actual = item["stock"]
            detalle.stock_min = item["min"]
            detalle.stock_max = item["max"]
            detalle.observaciones = "Inventario inicial configurado correctamente."
            detalle.save()

        # 3. Registrar movimiento de entrada inicial
        MovimientoProducto.objects.create(
            codigo_detalle_producto=detalle,
            tipo="entrada",
            cantidad=item["stock"],
            observacion=f"Carga inicial de inventario para {prod.nombre}"
        )

        productos_creados.append(prod)
        print(f"  ✓ Producto: [{prod.codigo}] {prod.nombre} | Stock: {detalle.cantidad_actual} | Precio: ${prod.precio:,.0f}")

    # ------------------------------------------------------------------------
    # 8.5 Promociones (Catálogo)
    # ------------------------------------------------------------------------
    # Promoción para productos
    for i, prod in enumerate(productos_creados[:3]):
        Promocion.objects.create(
            nombre=f"Super Promo {prod.nombre.split()[0]}",
            porcentaje_descuento=Decimal(str(random.choice([10, 15, 20]))),
            descripcion=f"Aprovecha un gran descuento por tiempo limitado en {prod.nombre}.",
            fecha_inicio=date.today() - timedelta(days=2),
            fecha_fin=date.today() + timedelta(days=20),
            estado=True,
            codigo_producto=prod,
            codigo_servicio=None,
        )

    # Promoción para servicios
    for i, serv in enumerate(servicios[:2]):
        Promocion.objects.create(
            nombre=f"Semana Especial: {serv.nombre}",
            porcentaje_descuento=Decimal(str(random.choice([15, 20, 25]))),
            descripcion=f"Descuento exclusivo en el servicio de {serv.nombre}.",
            fecha_inicio=date.today() - timedelta(days=1),
            fecha_fin=date.today() + timedelta(days=15),
            estado=True,
            codigo_producto=None,
            codigo_servicio=serv,
        )

    print(f"  ✓ Promociones directas de productos y servicios creadas.")
    return proveedores, productos_creados


# ============================================================================
# 9. POBLAR COMPRAS (CON REABASTECIMIENTO Y MOVIMIENTOS)
# ============================================================================
def poblar_compras(proveedores, productos):
    print("\n" + "=" * 60)
    print(" 6. POBLANDO ÓRDENES DE COMPRA A PROVEEDORES")
    print("=" * 60)

    for i in range(1, 4):
        prov = random.choice(proveedores)
        compra = Compra.objects.create(
            codigo_proveedor=prov,
            observaciones=f"Reabastecimiento quincenal lote #{i:03d}."
        )

        prods_seleccionados = random.sample(productos, k=3)
        for prod in prods_seleccionados:
            cant = random.randint(10, 20)
            precio_costo = (prod.precio * Decimal("0.55")).quantize(Decimal("0.01"))

            DetalleCompra.objects.create(
                codigo_compra=compra,
                codigo_producto=prod,
                cantidad=cant,
                precio_compra=precio_costo,
                precio_venta=prod.precio,
            )

        print(f"  ✓ Compra #{compra.codigo} a {prov.nombre} registrada por Total: ${compra.total:,.0f}")


# ============================================================================
# 10. POBLAR VENTAS Y DETALLES DE PAGO
# ============================================================================
def poblar_ventas(clientes, productos):
    print("\n" + "=" * 60)
    print(" 7. POBLANDO VENTAS Y REGISTROS DE PAGO")
    print("=" * 60)

    metodos = ["efectivo", "tarjeta", "transferencia"]

    for i in range(1, 8):
        cliente = random.choice(clientes)
        metodo = random.choice(metodos)
        estado = "completado"

        venta = Venta.objects.create(
            codigo_usuario=cliente,
            nombre_cliente=cliente.get_full_name(),
            correo=cliente.email,
            telefono=cliente.telefono,
            direccion="Calle 45 # 12-34, Apto 201",
            metodo_pago=metodo,
            estado_pago=estado,
            total_venta=Decimal("0.00")
        )

        # Seleccionar 1 o 2 productos con stock suficiente
        prods_venta = random.sample(productos, k=random.randint(1, 2))
        for p in prods_venta:
            if p.codigo_detalle_producto and p.codigo_detalle_producto.cantidad_actual > 5:
                cant = random.randint(1, 2)
                DetalleVenta.objects.create(
                    codigo_venta=venta,
                    codigo_producto=p,
                    cantidad=cant,
                    valor_descuento=Decimal("0.00")
                )

        if metodo == "transferencia":
            DetallePagos.objects.create(
                codigo_venta=venta,
                banco="Bancolombia",
                tipo_cuenta="Ahorros",
                numero_cuenta="123-456789-01",
                titular="Chicha Barber Studio SAS",
                instrucciones="Comprobante verificado exitosamente vía transferencia directa."
            )

        print(f"  ✓ Venta #{venta.codigo_venta} a {venta.nombre_cliente} | Método: {metodo} | Total: ${venta.total_venta:,.0f}")


# ============================================================================
# 11. POBLAR CONFIGURACIONES Y CARRUSEL
# ============================================================================
def poblar_configuraciones(admin):
    print("\n" + "=" * 60)
    print(" 8. POBLANDO CONFIGURACIONES Y CARRUSEL")
    print("=" * 60)

    slides = [
        {
            "nombre": "Estilo Clásico & Tradición",
            "texto": "Cortes y afeitados tradicionales con toalla caliente por los mejores barberos.",
            "estado": True,
        },
        {
            "nombre": "Degradados Urbanos & Tendencia",
            "texto": "Las últimas técnicas en degradados y diseño moderno para cabello y barba.",
            "estado": True,
        },
        {
            "nombre": "Cuidado Premium Masculino",
            "texto": "Productos exclusivos de las marcas líderes para mantener tu estilo en casa.",
            "estado": True,
        },
    ]

    carruseles = []
    for s in slides:
        carr = Carrusel.objects.create(
            nombre=s["nombre"],
            texto=s["texto"],
            estado=s["estado"]
        )
        carruseles.append(carr)
        print(f"  ✓ Slide de carrusel: {carr.nombre}")

    if carruseles:
        Configuracion.objects.create(
            codigo_usuario=admin,
            codigo_carrusel=carruseles[0],
            fecha_realizacion=timezone.now(),
            nombre="Configuración General Barbería",
            descripcion="Ajustes de visualización para la portada web de Chicha Barber.",
            estado=True
        )
        print("  ✓ Registro de Configuración general asociado al administrador.")


# ============================================================================
# 12. POBLAR HISTORIAL (BITÁCORA)
# ============================================================================
def poblar_historial(admin, productos):
    print("\n" + "=" * 60)
    print(" 9. POBLANDO BITÁCORA DE HISTORIAL")
    print("=" * 60)

    eventos = [
        ("Entrada de Inventario", "catalogo", "Ingreso de lote de productos por reabastecimiento general"),
        ("Ajuste de Stock", "catalogo", "Verificación física y cuadre de existencias en estantería"),
        ("Actualización de Tarifa", "servicios", "Revisión periódica de precios de servicios de barbería"),
        ("Apertura de Agenda", "reservas", "Generación de nuevos turnos semanales para profesionales"),
        ("Cierre de Caja", "venta", "Consolidación de transacciones y ventas del turno matutino"),
    ]

    for acc, mod, desc in eventos:
        prod_ref = random.choice(productos) if productos else None
        det_ref = prod_ref.codigo_detalle_producto if prod_ref else None

        Bitacora.objects.create(
            codigo_usuario=admin,
            codigo_detalle_producto=det_ref,
            accion=acc,
            modulo=mod,
            descripcion=desc,
            ip_origen="127.0.0.1"
        )

    print(f"  ✓ {len(eventos)} registros de auditoría insertados en Bitácora.")




   


# ============================================================================
# 14. EJECUCIÓN PRINCIPAL
# ============================================================================
if __name__ == "__main__":
    print("\n")
    print("=" * 65)
    print("      CHICHA BARBER STUDIO - CARGA COMPLETA DE BASE DE DATOS")
    print("=" * 65)

    # 1. Limpieza total
    limpiar_datos()

    # 2. Usuarios, barberos y clientes
    admin, barberos, clientes = poblar_usuarios()

    # 3. Servicios y calificaciones
    servicios = poblar_servicios(clientes)

    # 4. Agendas y reservas
    poblar_agendas_y_reservas(barberos, clientes, servicios)

    # 5. Catálogo de productos e inventario
    proveedores, productos = poblar_catalogo(servicios)

    # 6. Órdenes de compra a proveedores
    poblar_compras(proveedores, productos)

    # 7. Ventas y detalles de pago
    poblar_ventas(clientes, productos)

    # 8. Configuraciones y carrusel
    poblar_configuraciones(admin)

    # 9. Bitácora de historial
    poblar_historial(admin, productos)

   
    

    print("\n" + "=" * 65)
    print("   ¡BASE DE DATOS POBLADA EXITOSAMENTE AL 100%!")
    print("=" * 65)
    print(f"  • Usuarios registrados:      {Usuario.objects.count()}")
    print(f"  • Servicios disponibles:     {Servicios.objects.count()}")
    print(f"  • Calificaciones:            {Calificacion.objects.count()}")
    print(f"  • Agendas de barberos:       {Agenda.objects.count()}")
    print(f"  • Reservas de clientes:      {Reserva.objects.count()}")
    print(f"  • Categorías de productos:   {Categoria.objects.count()}")
    print(f"  • Marcas aliadas:            {Marca.objects.count()}")
    print(f"  • Proveedores:               {Proveedor.objects.count()}")
    print(f"  • Productos activos:         {Producto.objects.count()}")
    print(f"  • Movimientos de stock:      {MovimientoProducto.objects.count()}")
    print(f"  • Promociones vigentes:      {Promocion.objects.count()}")
    print(f"  • Órdenes de compra:         {Compra.objects.count()}")
    print(f"  • Ventas completadas:        {Venta.objects.count()}")
    print(f"  • Registros en bitácora:     {Bitacora.objects.count()}")
    print(f"  • Slides de carrusel:        {Carrusel.objects.count()}")       
    print("-" * 65)
    print("  Credenciales de Administrador:")
    print("  Usuario:  a@b.com")
    print("  Clave:    @dmin123")
    print("=" * 65 + "\n")