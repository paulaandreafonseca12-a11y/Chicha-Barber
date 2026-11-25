from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
import os

from django.test import RequestFactory, SimpleTestCase

from chat_ia.ai_service import DEFAULT_GROQ_MODEL, obtener_respuesta_ia
from chat_ia.contexto_adm import obtener_contexto_admin
from chat_ia.views import construir_contexto_dinamico, vista_chat_admin


class QuerySetFalso(list):
	def exists(self):
		return bool(self)

	def select_related(self, *fields):
		return self


class SessionFalsa(dict):
	modified = False


class ObtenerRespuestaIATests(SimpleTestCase):
	@patch("chat_ia.ai_service.Groq")
	def test_usa_modelo_disponible_por_defecto(self, groq_mock):
		groq_mock.return_value.chat.completions.create.return_value = SimpleNamespace(
			choices=[SimpleNamespace(message=SimpleNamespace(content="Hola"))]
		)

		with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=True):
			respuesta = obtener_respuesta_ia("Hola")

		self.assertEqual(respuesta, "Hola")
		self.assertEqual(
			groq_mock.return_value.chat.completions.create.call_args.kwargs["model"],
			DEFAULT_GROQ_MODEL,
		)

	@patch("chat_ia.ai_service.Groq")
	def test_permite_configurar_modelo_por_entorno(self, groq_mock):
		groq_mock.return_value.chat.completions.create.return_value = SimpleNamespace(
			choices=[SimpleNamespace(message=SimpleNamespace(content="Hola"))]
		)

		with patch.dict(
			os.environ,
			{"GROQ_API_KEY": "test-key", "GROQ_MODEL": "modelo-configurado"},
			clear=True,
		):
			obtener_respuesta_ia("Hola")

		self.assertEqual(
			groq_mock.return_value.chat.completions.create.call_args.kwargs["model"],
			"modelo-configurado",
		)

	@patch("chat_ia.ai_service.Groq")
	def test_permite_reemplazar_el_prompt_base(self, groq_mock):
		groq_mock.return_value.chat.completions.create.return_value = SimpleNamespace(
			choices=[SimpleNamespace(message=SimpleNamespace(content="Respuesta"))]
		)

		with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=True):
			obtener_respuesta_ia("Pregunta", system_prompt_base="Contexto administrativo")

		mensajes = groq_mock.return_value.chat.completions.create.call_args.kwargs["messages"]
		self.assertEqual(mensajes[0]["content"], "Contexto administrativo")


class VistaChatAdminTests(SimpleTestCase):
	def setUp(self):
		self.factory = RequestFactory()

	def test_rechaza_clientes(self):
		request = self.factory.get("/chat/administracion/")
		request.user = SimpleNamespace(is_authenticated=True, rol="cliente")

		respuesta = vista_chat_admin(request)

		self.assertEqual(respuesta.status_code, 403)

	@patch("chat_ia.views.obtener_respuesta_ia", return_value="Respuesta administrativa")
	@patch("chat_ia.views.obtener_contexto_admin", return_value="Solo contexto administrativo")
	def test_envia_contexto_admin_y_usa_historial_separado(self, contexto_mock, respuesta_mock):
		request = self.factory.post(
			"/chat/administracion/",
			{"pregunta": "¿Cómo reviso el inventario?"},
		)
		request.user = SimpleNamespace(is_authenticated=True, rol="admin")
		request.session = SessionFalsa()

		respuesta = vista_chat_admin(request)

		self.assertEqual(respuesta.status_code, 200)
		respuesta_mock.assert_called_once_with(
			"¿Cómo reviso el inventario?",
			system_prompt_base="Solo contexto administrativo",
		)
		self.assertIn("chat_admin", request.session)
		self.assertNotIn("chat", request.session)
		contexto_mock.assert_called_once_with()


class ObtenerContextoAdminTests(SimpleTestCase):
	def test_usa_campos_y_relaciones_reales_de_los_modelos_admin(self):
		categoria = SimpleNamespace(nombre="Cuidado personal")
		marca = SimpleNamespace(nombre="Marca Uno", estado=True)
		detalle = SimpleNamespace(cantidad_actual=12, stock_min=5, stock_max=40)
		productos = QuerySetFalso([
			SimpleNamespace(
				nombre="Cera",
				precio_venta_contexto=Decimal("35000.00"),
				codigo_categoria=categoria,
				codigo_marca=marca,
				codigo_detalle_producto=detalle,
				estado=True,
			),
			SimpleNamespace(
				nombre="Producto sin relaciones",
				precio_venta_contexto=Decimal("5000.00"),
				codigo_categoria=None,
				codigo_marca=None,
				codigo_detalle_producto=None,
				estado=False,
			),
		])
		servicio = SimpleNamespace(
			nombre="Corte",
			precio=Decimal("20000.00"),
			duracion=30,
			estado=True,
		)
		promocion = SimpleNamespace(
			nombre="Promo de prueba",
			porcentaje_descuento=Decimal("15.00"),
			codigo_servicio=servicio,
			codigo_producto=productos[0],
			fecha_inicio=date(2000, 1, 1),
			fecha_fin=date(2000, 1, 31),
			estado=True,
		)

		with (
			patch("chat_ia.contexto_adm.Producto.objects.annotate", return_value=productos),
			patch("chat_ia.contexto_adm.Categoria.objects.all", return_value=QuerySetFalso([categoria])),
			patch("chat_ia.contexto_adm.Marca.objects.all", return_value=QuerySetFalso([marca])),
			patch("chat_ia.contexto_adm.Servicios.objects.all", return_value=QuerySetFalso([servicio])),
			patch("chat_ia.contexto_adm.Promocion.objects.select_related", return_value=QuerySetFalso([promocion])),
		):
			contexto = obtener_contexto_admin()

		self.assertIn("Precio de venta: $35000", contexto)
		self.assertIn("Categoría: Cuidado personal", contexto)
		self.assertIn("Marca: Marca Uno", contexto)
		self.assertIn("Existencias: 12 unidades (mínimo: 5, máximo: 40)", contexto)
		self.assertIn("Categoría: Sin categoría", contexto)
		self.assertIn("Marca: Sin marca", contexto)
		self.assertIn("Existencias: sin registro de existencias", contexto)
		self.assertIn("Producto sin relaciones", contexto)
		self.assertIn("Corte: $20000 | Duración: 30 min | Estado: Activo", contexto)
		self.assertIn("en servicio Corte, producto Cera", contexto)
		self.assertIn("fuera del rango de fechas", contexto)


class ConstruirContextoDinamicoTests(SimpleTestCase):
	def construir_contexto_con_promocion(self, promocion):
		with (
			patch("chat_ia.views.Servicios.objects.filter", return_value=QuerySetFalso()),
			patch("chat_ia.views.Promocion.objects.filter", return_value=QuerySetFalso([promocion])),
			patch("chat_ia.views.Categoria.objects.all", return_value=QuerySetFalso()),
			patch("chat_ia.views.Producto.objects.filter", return_value=QuerySetFalso()),
		):
			return construir_contexto_dinamico()

	def test_contexto_incluye_promocion_de_servicio(self):
		promocion = SimpleNamespace(
			nombre="Corte promo",
			porcentaje_descuento=20,
			codigo_servicio=SimpleNamespace(nombre="Corte clásico"),
			codigo_producto=None,
			descripcion="Oferta de prueba",
		)

		contexto = self.construir_contexto_con_promocion(promocion)

		self.assertIn("descuento en el servicio Corte clásico", contexto)

	def test_contexto_incluye_promocion_de_producto(self):
		promocion = SimpleNamespace(
			nombre="Cera promo",
			porcentaje_descuento=15,
			codigo_servicio=None,
			codigo_producto=SimpleNamespace(nombre="Cera mate"),
			descripcion="Oferta de prueba",
		)

		contexto = self.construir_contexto_con_promocion(promocion)

		self.assertIn("descuento en el producto Cera mate", contexto)

	def test_contexto_acepta_promocion_sin_destino(self):
		promocion = SimpleNamespace(
			nombre="Promo general",
			porcentaje_descuento=10,
			codigo_servicio=None,
			codigo_producto=None,
			descripcion="Oferta de prueba",
		)

		contexto = self.construir_contexto_con_promocion(promocion)

		self.assertIn("descuento en servicios o productos", contexto)
