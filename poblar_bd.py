import os
import django
import random

# 1. Configurar el entorno de Django para poder usar sus modelos desde este script externo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# 2. Importar los modelos
from usuarios.models import Usuario
from servicios.models import Servicios, Promocion
from reservas.models import Reserva, Calificacion
from productos.models import Producto, Stock, Compra, DetalleCompra

def limpiar_datos():
    print("Limpiando datos anteriores...")
    # Opcional: puedes descomentar estas líneas si quieres que el script borre todo antes de poblar
    # DetalleCompra.objects.all().delete()
    # Compra.objects.all().delete()
    # Stock.objects.all().delete()
    # Producto.objects.all().delete()
    # Calificacion.objects.all().delete()
    # Reserva.objects.all().delete()
    # Promocion.objects.all().delete()
    # Servicios.objects.all().delete()
    # Usuario.objects.exclude(is_superuser=True).delete()
    pass

def poblar_usuarios():
    print("Poblando Usuarios...")
    roles = ['cliente', 'cliente', 'cliente', 'barbero', 'admin']
    for i in range(1, 11):
        email = f"usuario{i}@ejemplo.com"
        # Evitamos duplicados
        if not Usuario.objects.filter(email=email).exists():
            rol_asignado = random.choice(roles)
            Usuario.objects.create_user(
                username=f"100000000{i}",
                email=email,
                password="Password123!", # Contraseña por defecto para todos
                first_name=f"NombrePrueba{i}",
                last_name=f"ApellidoPrueba{i}",
                telefono=f"30012345{i:02d}",
                rol=rol_asignado,
                is_staff=(rol_asignado in ['barbero', 'admin']), # Dar acceso al admin si es barbero o admin
                is_superuser=(rol_asignado == 'admin')
            )

def poblar_servicios():
    print("Poblando Servicios...")
    nombres_servicios = [
        'Corte Clásico', 'Degradado (Fade)', 'Arreglo de Barba', 
        'Corte + Barba', 'Tinte Capilar', 'Perfilado de Cejas', 
        'Corte Niño', 'Masaje Facial', 'Tratamiento Capilar', 'Limpieza Facial'
    ]
    
    for nombre in nombres_servicios:
        Servicios.objects.get_or_create(
            nombre=nombre,
            defaults={
                'precio': random.randint(15, 60) * 1000, # Precios entre 15.000 y 60.000
                'duracion': random.choice([30, 45, 60, 90]),
                'descripcion': f'Descripción detallada y profesional para el servicio de {nombre}.'
            }
        )

def poblar_promociones():
    print("Poblando Promociones...")
    for i in range(1, 11):
        Promocion.objects.get_or_create(
            nombre=f"Promo Especial {i}",
            defaults={
                'descuento': f"{random.choice([10, 15, 20, 25, 50])}%",
                'duracion': f"{random.choice([1, 2, 3])} Semanas",
                'descripcion': f"Aprovecha esta increíble promoción número {i} por tiempo limitado."
            }
        )

def poblar_reservas():
    print("Poblando Reservas...")
    estados = ['reservada', 'confirmada', 'cancelada']
    
    servicios_disponibles = list(Servicios.objects.all())
    if not servicios_disponibles:
        print("  ⚠️ No se pueden crear reservas porque no hay servicios en la base de datos.")
        return

    for i in range(1, 11):
        Reserva.objects.create(
            nombre_cliente=f"Cliente Reserva {i}",
            correo_cliente=f"cliente_reserva{i}@correo.com",
            telefono_cliente=f"32000000{i:02d}",
            fecha_reserva=f"2024-11-{random.randint(10, 28)} 15:00",
            servicio=random.choice(servicios_disponibles),
            estado=random.choice(estados)
        )

def poblar_calificaciones():
    print("Poblando Calificaciones...")
    # Filtramos usuarios que sean barberos
    barberos = Usuario.objects.filter(rol='barbero')
    
    if barberos.exists():
        for i in range(1, 11):
            Calificacion.objects.create(
                barbero_a_calificar=random.choice(barberos),
                nombre_cliente=f"Cliente Anónimo {i}",
                calificacion=random.randint(1, 5),
                resenia=f"Excelente atención y profesionalismo. Calificación de prueba {i}."
            )
    else:
        print("  ⚠️ No se crearon calificaciones porque no hay usuarios con rol 'barbero'.")

def poblar_productos_y_stock():
    print("Poblando Productos y Stock...")
    nombres_productos = [
        'Cera Moldeadora', 'Aceite para Barba', 'Gel Fijador',
        'Shampoo de Cuidado', 'Navaja Profesional', 'Brocha de Afeitar',
        'Tónico Capilar', 'Peine de Madera', 'Bálsamo Hidratante', 'Aftershave'
    ]
    
    try:
        for nombre in nombres_productos:
            precio_c = random.randint(10, 30) * 1000
            producto, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': f'Producto de alta calidad para barbería: {nombre}.',
                    'precio_compra': precio_c,
                    'precio_venta': precio_c + (random.randint(10, 20) * 1000),
                }
            )
            
            # Aseguramos que el stock exista y le forzamos una cantidad
            # (Esto evita problemas si ya existía previamente con stock en 0)
            stock, created = Stock.objects.get_or_create(producto=producto)
            stock.cantidad = random.randint(15, 50)
            stock.save()
    except Exception as e:
        print(f"  ⚠️ Error al poblar productos/stock: {e}")

def poblar_compras():
    print("Poblando Compras...")
    try:
        productos = list(Producto.objects.all())
        if not productos:
            print("  ⚠️ No se pueden crear compras porque no hay productos.")
            return

        for i in range(1, 11):
            compra, created = Compra.objects.get_or_create(
                correo=f"comprador{i}@correo.com",
                defaults={
                    'nombre_cliente': f"Comprador Prueba {i}",
                    'telefono': f"30099900{i:02d}",
                    'direccion': f"Carrera {i} # {i}-{i*2}",
                    'metodo_pago': random.choice(['persona', 'contraentrega'])
                }
            )
            
            if created:
                # Añadimos un detalle (artículo) a esta compra
                DetalleCompra.objects.create(
                    compra=compra,
                    producto=random.choice(productos),
                    cantidad=random.randint(1, 3)
                )
    except Exception as e:
        print(f"  ⚠️ Error al poblar compras: {e}")

if __name__ == '__main__':
    print("Iniciando la inserción de datos de prueba...")
    limpiar_datos()
    poblar_usuarios()
    poblar_servicios()
    poblar_promociones()
    poblar_reservas()
    poblar_calificaciones()
    poblar_productos_y_stock()
    poblar_compras()
    print("✅ ¡Base de datos poblada con éxito!")
