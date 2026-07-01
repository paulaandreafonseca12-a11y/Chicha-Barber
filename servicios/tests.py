import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import Servicios, Promocion, Calificacion

class ChichaBarberModelsTestCase(TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas."""
        # Creamos una imagen falsa en memoria para probar las subidas
        self.imagen_falsa = SimpleUploadedFile(
            name='mi_foto_original.jpg', 
            content=b'\x47\x49\x46\x38\x39\x61', 
            content_type='image/jpeg'
        )
        
        # Servicio base para usar en las pruebas con ForeingKey
        self.servicio = Servicios.objects.create(
            nombre="Corte Fade Clásico",
            precio=15000.00,
            duracion=30,
            descripcion="El degradado perfecto para la barbería."
        )

    def test_creacion_servicio_y_renombrado_imagen(self):
        """Verifica que un servicio se guarde correctamente y renombre su imagen usando su PK."""
        servicio_con_foto = Servicios.objects.create(
            nombre="Corte de Cabello Premium",
            precio=25000.00,
            duracion=45,
            descripcion="Corte con lavado y masaje.",
            imagen=self.imagen_falsa
        )
        
        # Comprobamos que el método __str__ funcione
        self.assertEqual(str(servicio_con_foto), "Corte de Cabello Premium")
        
        # Validamos que el método save() haya estructurado y renombrado la imagen como querías:
        # "servicios/corte-de-cabello-premium_<pk>.jpg"
        nombre_esperado = f"servicios/corte-de-cabello-premium_{servicio_con_foto.pk}.jpg"
        self.assertEqual(servicio_con_foto.imagen.name, nombre_esperado)

    def test_creacion_promocion_y_renombrado_imagen(self):
        """Verifica la correcta asignación de promociones y el slugify de su imagen."""
        promocion = Promocion.objects.create(
            servicio=self.servicio,
            nombre="Combo Descuento Papá",
            porcentaje_descuento=15.50,
            duracion="Mes de Junio",
            descripcion="Trae a tu hijo y recibe descuento.",
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date(),
            imagen=self.imagen_falsa
        )
        
        self.assertEqual(str(promocion), "Combo Descuento Papá")
        
        # Validamos la ruta esperada: "promociones/combo-descuento-papa_<pk>.jpg"
        nombre_esperado = f"promociones/combo-descuento-papa_{promocion.pk}.jpg"
        self.assertEqual(promocion.imagen.name, nombre_esperado)

    def test_calificacion_y_ordenamiento(self):
        """Prueba que las calificaciones se vinculen al servicio y respeten el orden invertido."""
        # Creamos dos calificaciones con tiempos sutilmente distintos
        calificacion_antigua = Calificacion.objects.create(
            servicio=self.servicio,
            cliente="Juan Pérez",
            puntuacion=5,
            comentario="¡El mejor degradado del barrio!"
        )
        
        calificacion_reciente = Calificacion.objects.create(
            servicio=self.servicio,
            cliente="Andrés Mendoza",
            puntuacion=4,
            comentario="Muy buen servicio, demoró un poco."
        )
        
        # Comprobamos el método __str__
        self.assertEqual(
            str(calificacion_antigua), 
            "Juan Pérez - Corte Fade Clásico (5 estrellas)"
        )
        
        # Comprobamos el ordenamiento ['-fecha_calificacion'] 
        # La más reciente debe aparecer primero en la lista
        primer_elemento = Calificacion.objects.all().first()
        self.assertEqual(primer_elemento, calificacion_reciente)

    def tearDown(self):
        """Limpieza de archivos huérfanos creados durante los tests."""
        # Evita que se llene tu carpeta media/ de archivos basura generados por las pruebas
        for servicio in Servicios.objects.all():
            if servicio.imagen:
                if os.path.exists(servicio.imagen.path):
                    os.remove(servicio.imagen.path)
                    
        for promo in Promocion.objects.all():
            if promo.imagen:
                if os.path.exists(promo.imagen.path):
                    os.remove(promo.imagen.path)

# Create your tests here.
