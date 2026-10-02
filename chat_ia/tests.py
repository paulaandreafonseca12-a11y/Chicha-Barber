from types import SimpleNamespace
from unittest.mock import patch
import os

from django.test import SimpleTestCase

from chat_ia.ai_service import DEFAULT_GROQ_MODEL, obtener_respuesta_ia
from chat_ia.views import construir_contexto_dinamico


class QuerySetFalso(list):
	def exists(self):
		return bool(self)


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
