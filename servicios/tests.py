import os
import shutil
import tempfile
from decimal import Decimal
from django.test import SimpleTestCase, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from catalogo.models import Promocion
from .forms import CalificacionForm, ServiciosForm
from .models import Servicios, Calificacion

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
            nombre="Combo Descuento Papá",
            porcentaje_descuento=15.50,
            descripcion="Trae a tu hijo y recibe descuento.",
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date(),
            imagen=self.imagen_falsa,
            codigo_servicio=self.servicio,
        )
        
        self.assertEqual(str(promocion), "Combo Descuento Papá")
        
        # Promocion conserva el nombre original del archivo dentro de promociones/.
        nombre_esperado = "promociones/mi_foto_original.jpg"
        self.assertEqual(promocion.imagen.name, nombre_esperado)

    def test_calificacion_y_ordenamiento(self):
        """Prueba que las calificaciones se vinculen al servicio y respeten el orden invertido."""
        # Creamos dos calificaciones con tiempos sutilmente distintos
        calificacion_antigua = Calificacion.objects.create(
            servicio=self.servicio,
            cliente_nombre="Juan Pérez",
            puntuacion=5,
            comentario="¡El mejor degradado del barrio!"
        )
        
        calificacion_reciente = Calificacion.objects.create(
            servicio=self.servicio,
            cliente_nombre="Andrés Mendoza",
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


class ServiciosFormValidationTests(SimpleTestCase):
    def setUp(self):
        self.valid_data = {
            'nombre': 'Corte Fade 2',
            'precio': '25000.00',
            'duracion': '30',
            'descripcion': 'Corte clásico con acabado profesional.',
        }

    def test_accepts_valid_service_data_with_spanish_characters(self):
        self.valid_data['nombre'] = 'Corte Clásico'
        form = ServiciosForm(data=self.valid_data)

        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_digits_inside_service_name(self):
        self.valid_data['nombre'] = 'Corte 2'
        form = ServiciosForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_rejects_markup_in_service_name(self):
        self.valid_data['nombre'] = '<script>alert(1)</script>'
        form = ServiciosForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_rejects_numeric_only_service_name(self):
        self.valid_data['nombre'] = '12345'
        form = ServiciosForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_rejects_negative_price(self):
        self.valid_data['precio'] = '-1'
        form = ServiciosForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_rejects_zero_duration(self):
        self.valid_data['duracion'] = '0'
        form = ServiciosForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('duracion', form.errors)

    def test_requires_description_when_creating_service(self):
        self.valid_data.pop('descripcion')
        form = ServiciosForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)

    def test_rejects_short_description(self):
        self.valid_data['descripcion'] = 'Muy corto'
        form = ServiciosForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)

    def test_trims_service_name_and_description(self):
        self.valid_data['nombre'] = '  Corte + barba  '
        self.valid_data['descripcion'] = '  Servicio completo y profesional.  '
        form = ServiciosForm(data=self.valid_data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['nombre'], 'Corte + barba')
        self.assertEqual(
            form.cleaned_data['descripcion'],
            'Servicio completo y profesional.'
        )


class CalificacionFormValidationTests(TestCase):
    def setUp(self):
        self.servicio = Servicios.objects.create(
            nombre='Corte clásico',
            precio=Decimal('25000.00'),
            duracion=30,
            descripcion='Corte tradicional con acabado profesional.',
        )
        self.valid_data = {
            'servicio': self.servicio.pk,
            'cliente_nombre': '  Paula Pérez  ',
            'puntuacion': '5',
            'comentario': '  Excelente servicio y atención.  ',
        }

    def test_accepts_valid_rating_and_trims_text(self):
        form = CalificacionForm(data=self.valid_data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['cliente_nombre'], 'Paula Pérez')
        self.assertEqual(
            form.cleaned_data['comentario'],
            'Excelente servicio y atención.'
        )

    def test_rejects_rating_outside_one_to_five(self):
        for puntuacion in ('0', '6'):
            with self.subTest(puntuacion=puntuacion):
                data = {**self.valid_data, 'puntuacion': puntuacion}
                form = CalificacionForm(data=data)

                self.assertFalse(form.is_valid())
                self.assertIn('puntuacion', form.errors)

    def test_rejects_short_comment_and_name(self):
        data = {
            **self.valid_data,
            'cliente_nombre': 'A',
            'comentario': 'Bueno',
        }
        form = CalificacionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('cliente_nombre', form.errors)
        self.assertIn('comentario', form.errors)

    def test_rejects_numeric_only_customer_name(self):
        data = {**self.valid_data, 'cliente_nombre': '12345'}
        form = CalificacionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('cliente_nombre', form.errors)

    def test_does_not_offer_inactive_services(self):
        servicio_inactivo = Servicios.objects.create(
            nombre='Servicio inactivo',
            precio=Decimal('10000.00'),
            duracion=20,
            descripcion='Servicio temporalmente no disponible.',
            estado=False,
        )
        data = {**self.valid_data, 'servicio': servicio_inactivo.pk}
        form = CalificacionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('servicio', form.errors)

    def test_invalid_submission_renders_form_errors(self):
        response = self.client.post(
            reverse('enviar_calificacion'),
            {
                'servicio': self.servicio.pk,
                'cliente_nombre': 'A',
                'puntuacion': '6',
                'comentario': 'Corto',
            },
        )

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('cliente_nombre', form.errors)
        self.assertIn('puntuacion', form.errors)
        self.assertIn('comentario', form.errors)


# Create your tests here.
