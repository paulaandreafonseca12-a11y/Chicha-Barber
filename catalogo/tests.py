from decimal import Decimal
from datetime import date
from django.test import TestCase
from catalogo.models import Categoria, Marca, Producto, DetalleProducto, Promocion
from catalogo.forms import (
    ProductoForm,
    PromocionEditarForm,
    PromocionForm,
)
from servicios.models import Servicios


class ProductoSanitizacionXSSValidationTestCase(TestCase):
    """
    CP16 (CB-360) / HU-16: Sanitización y validación de caracteres en catálogo.
    Pruebas unitarias para confirmar la prevención XSS, rechazo de scripts/HTML,
    validación de longitud (max_length=100) y codificación UTF-8.
    """

    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre="Cuidado Capilar",
            descripcion="Categoría para pruebas unitarias de sanitización."
        )
        self.marca_activa = Marca.objects.create(
            nombre="Marca Segura",
            descripcion="Marca activa para tests.",
            estado=True
        )
        self.marca_inactiva = Marca.objects.create(
            nombre="Marca Inactiva",
            descripcion="Marca inactiva que no debe aparecer en formulario.",
            estado=False
        )

    def test_xss_injection_script_tag_in_name(self):
        """Rechaza etiquetas <script> y código JavaScript malicioso en el nombre."""
        form_data = {
            'nombre': "<script>alert('XSS')</script>",
            'descripcion': "Descripción de prueba legítima.",
            'codigo_categoria': self.categoria.pk,
            'codigo_marca': self.marca_activa.pk,
            'precio': '45000.00',
            'estado': True,
        }
        form = ProductoForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debe admitir scripts en el nombre.")
        self.assertIn('nombre', form.errors)

    def test_xss_injection_html_tag_in_name(self):
        """Rechaza etiquetas HTML como <img> con eventos inline onerror."""
        form_data = {
            'nombre': "<img src=x onerror=alert(1)>",
            'descripcion': "Descripción válida.",
            'codigo_categoria': self.categoria.pk,
            'codigo_marca': self.marca_activa.pk,
            'precio': '30000.00',
            'estado': True,
        }
        form = ProductoForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debe admitir HTML en el nombre.")
        self.assertIn('nombre', form.errors)

    def test_special_characters_and_sql_injection_symbols(self):
        """Rechaza comillas dobles, simples y sintaxis SQL sospechosa."""
        form_data = {
            'nombre': 'Pomada"; DROP TABLE catalogo_producto; --',
            'descripcion': "Intento de inyección SQL.",
            'codigo_categoria': self.categoria.pk,
            'codigo_marca': self.marca_activa.pk,
            'precio': '25000.00',
            'estado': True,
        }
        form = ProductoForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debe rechazar caracteres especiales SQL.")
        self.assertIn('nombre', form.errors)

    def test_valid_product_name_with_spanish_accents_and_utf8(self):
        """Acepta nombres legítimos en español con tildes, virgulillas (ñ) y números."""
        form_data = {
            'nombre': "Gel Fijador Máximo Élite Año 2026",
            'descripcion': "Descripción válida con acentos: áéíóú ñÑ.",
            'codigo_categoria': self.categoria.pk,
            'codigo_marca': self.marca_activa.pk,
            'precio': '35000.00',
            'estado': True,
        }
        form = ProductoForm(data=form_data)
        self.assertTrue(form.is_valid(), f"El formulario debe ser válido para texto UTF-8 legítimo. Errores: {form.errors}")
        producto = form.save()
        self.assertEqual(producto.nombre, "Gel Fijador Máximo Élite Año 2026")
        self.assertTrue(producto.codigo.startswith("PROD-"))
        # Verifica relación con marca y despliegue en __str__
        self.assertIn("Marca Segura", str(producto))

    def test_name_max_length_exceeded(self):
        """Rechaza nombres que superen la longitud máxima de 100 caracteres."""
        nombre_largo = "A" * 105
        form_data = {
            'nombre': nombre_largo,
            'descripcion': "Descripción corta válida.",
            'codigo_categoria': self.categoria.pk,
            'codigo_marca': self.marca_activa.pk,
            'precio': '20000.00',
            'estado': True,
        }
        form = ProductoForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debe rechazar nombres mayores a 100 caracteres.")
        self.assertIn('nombre', form.errors)

    def test_inactive_brand_excluded_from_form_choices(self):
        """CP17 (CB-432): Confirma que las marcas inactivas no están disponibles en el formulario."""
        form = ProductoForm()
        queryset_marcas = form.fields['codigo_marca'].queryset
        self.assertIn(self.marca_activa, queryset_marcas)
        self.assertNotIn(self.marca_inactiva, queryset_marcas)


class PromocionFormValidationTests(TestCase):
    def setUp(self):
        self.servicio = Servicios.objects.create(
            nombre='Corte premium',
            precio=Decimal('30000.00'),
            duracion=45,
            descripcion='Corte premium con lavado y peinado.',
        )
        self.producto = Producto.objects.create(
            nombre='Pomada capilar',
            descripcion='Pomada para peinar.',
            precio=Decimal('15000.00'),
        )
        self.data = {
            'codigo_servicio': self.servicio.pk,
            'codigo_producto': '',
            'nombre': '  Promo de verano  ',
            'porcentaje_descuento': '20.00',
            'fecha_inicio': '2026-10-16',
            'fecha_fin': '2026-10-31',
            'descripcion': 'Descuento especial de temporada.',
            'estado': True,
        }
        self.promocion = Promocion.objects.create(
            codigo_servicio=self.servicio,
            nombre='Promo anterior',
            porcentaje_descuento=Decimal('10.00'),
            fecha_inicio=date(2026, 9, 1),
            fecha_fin=date(2026, 9, 30),
            descripcion='Promoción anterior de prueba.',
        )

    def test_accepts_valid_promotion_and_trims_name(self):
        form = PromocionForm(data=self.data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['nombre'], 'Promo de verano')

    def test_accepts_discount_with_percent_sign_on_create_and_edit(self):
        for form_class in (PromocionForm, PromocionEditarForm):
            with self.subTest(form=form_class.__name__):
                form = form_class(
                    data={**self.data, 'porcentaje_descuento': '20%'},
                    **({'instance': self.promocion} if form_class is PromocionEditarForm else {})
                )

                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(
                    form.cleaned_data['porcentaje_descuento'],
                    Decimal('20'),
                )

    def test_rejects_misplaced_or_repeated_percent_sign(self):
        for porcentaje in ('%20', '20%%'):
            with self.subTest(porcentaje=porcentaje):
                form = PromocionForm(
                    data={**self.data, 'porcentaje_descuento': porcentaje}
                )

                self.assertFalse(form.is_valid())
                self.assertIn('porcentaje_descuento', form.errors)

    def test_rejects_numeric_only_promotion_name_on_create_and_edit(self):
        for form_class in (PromocionForm, PromocionEditarForm):
            with self.subTest(form=form_class.__name__):
                form = form_class(
                    data={**self.data, 'nombre': '12345'},
                    **({'instance': self.promocion} if form_class is PromocionEditarForm else {})
                )

                self.assertFalse(form.is_valid())
                self.assertIn('nombre', form.errors)

    def test_rejects_digits_inside_promotion_name_on_create_and_edit(self):
        for form_class in (PromocionForm, PromocionEditarForm):
            with self.subTest(form=form_class.__name__):
                form = form_class(
                    data={**self.data, 'nombre': 'Promo 2026'},
                    **({'instance': self.promocion} if form_class is PromocionEditarForm else {})
                )

                self.assertFalse(form.is_valid())
                self.assertIn('nombre', form.errors)

    def test_rejects_discount_above_limit(self):
        for form_class in (PromocionForm, PromocionEditarForm):
            with self.subTest(form=form_class.__name__):
                form = form_class(
                    data={**self.data, 'porcentaje_descuento': '50.01'},
                    **({'instance': self.promocion} if form_class is PromocionEditarForm else {})
                )

                self.assertFalse(form.is_valid())
                self.assertIn('porcentaje_descuento', form.errors)

    def test_rejects_negative_and_non_numeric_discount(self):
        for porcentaje in ('-1', 'abc'):
            with self.subTest(porcentaje=porcentaje):
                form = PromocionForm(
                    data={**self.data, 'porcentaje_descuento': porcentaje}
                )

                self.assertFalse(form.is_valid())
                self.assertIn('porcentaje_descuento', form.errors)

    def test_rejects_end_date_before_start_date(self):
        for form_class in (PromocionForm, PromocionEditarForm):
            with self.subTest(form=form_class.__name__):
                form = form_class(
                    data={**self.data, 'fecha_fin': '2026-10-15'},
                    **({'instance': self.promocion} if form_class is PromocionEditarForm else {})
                )

                self.assertFalse(form.is_valid())
                self.assertIn('fecha_fin', form.errors)

    def test_requires_exactly_one_product_or_service(self):
        invalid_data = {**self.data, 'codigo_servicio': '', 'codigo_producto': ''}
        both_data = {
            **self.data,
            'codigo_producto': self.producto.pk,
        }

        for form_class in (PromocionForm, PromocionEditarForm):
            with self.subTest(form=form_class.__name__, relation='none'):
                form = form_class(
                    data=invalid_data,
                    **({'instance': self.promocion} if form_class is PromocionEditarForm else {})
                )
                self.assertFalse(form.is_valid())
                self.assertTrue(form.non_field_errors())

            with self.subTest(form=form_class.__name__, relation='both'):
                form = form_class(
                    data=both_data,
                    **({'instance': self.promocion} if form_class is PromocionEditarForm else {})
                )
                self.assertFalse(form.is_valid())
                self.assertTrue(form.non_field_errors())

