
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


# ==========================================================
# CHOICES
# ==========================================================

class TipoDocumento(models.TextChoices):
    CC = 'CC', 'Cédula de ciudadanía'
    TI = 'TI', 'Tarjeta de identidad'
    CE = 'CE', 'Cédula de extranjería'
    PA = 'PA', 'Pasaporte'


class RolUsuario(models.TextChoices):
    ADMIN = 'admin', 'Administrador'
    BARBERO = 'barbero', 'Barbero'
    CLIENTE = 'cliente', 'Cliente'


# ==========================================================
# MANAGER DEL USUARIO
# ==========================================================

class UsuarioManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError(
                'El usuario debe tener un correo electrónico'
            )

        email = self.normalize_email(email)

        usuario = self.model(
            email=email,
            **extra_fields
        )

        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault(
            'rol',
            RolUsuario.ADMIN
        )

        extra_fields.setdefault(
            'estado',
            True
        )

        usuario = self.create_user(
            email,
            password,
            **extra_fields
        )

        return usuario


# ==========================================================
# MODELO USUARIO
# ==========================================================

class Usuario(AbstractBaseUser):

    objects = UsuarioManager()

    # ======================================================
    # CAMPOS HEREDADOS DE DJANGO
    # ======================================================

    password = models.CharField(
        max_length=128,
        verbose_name='Contraseña',
        db_column='contrasena'
    )

    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último acceso',
        db_column='ultimo_acceso'
    )

    # ======================================================
    # DATOS PERSONALES
    # ======================================================

    primer_nombre = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Primer nombre',
        db_column='primer_nombre'
    )

    segundo_nombre = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Segundo nombre',
        db_column='segundo_nombre'
    )

    primer_apellido = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Primer apellido',
        db_column='primer_apellido'
    )

    segundo_apellido = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Segundo apellido',
        db_column='segundo_apellido'
    )

    # ======================================================
    # CONTACTO
    # ======================================================

    email = models.EmailField(
        unique=True,
        verbose_name='Correo electrónico',
        db_column='correo_electronico'
    )

    telefono = models.CharField(
        max_length=15,
        verbose_name='Teléfono',
        db_column='telefono'
    )

    # ======================================================
    # ESTADO Y FOTO
    # ======================================================

    estado = models.BooleanField(
        default=True,
        verbose_name='Estado',
        db_column='estado'
    )

    foto_perfil = models.ImageField(
        upload_to='usuarios/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil',
        db_column='foto_perfil'
    )

    # ======================================================
    # DOCUMENTO
    # ======================================================

    tipo_documento = models.CharField(
        max_length=2,
        choices=TipoDocumento.choices,
        default=TipoDocumento.CC,
        verbose_name='Tipo de documento',
        db_column='tipo_documento'
    )

    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de documento',
        db_column='numero_documento'
    )

    # ======================================================
    # ROL
    # ======================================================

    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.CLIENTE,
        verbose_name='Rol',
        db_column='rol'
    )

    # ======================================================
    # FECHA DE CREACIÓN
    # ======================================================

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        db_column='fecha_creacion'
    )

    # ======================================================
    # CONFIGURACIÓN DE AUTENTICACIÓN
    # ======================================================

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'primer_nombre',
        'primer_apellido',
        'tipo_documento',
        'numero_documento'
    ]

    # ======================================================
    # CONFIGURACIÓN DE TABLA
    # ======================================================

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'

    # ======================================================
    # MÉTODOS
    # ======================================================

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    def get_full_name(self):

        partes = [
            self.primer_nombre,
            self.segundo_nombre,
            self.primer_apellido,
            self.segundo_apellido
        ]

        return ' '.join(
            parte for parte in partes if parte
        )

    def get_short_name(self):
        return self.primer_nombre

    def get_rol_display(self):
        return RolUsuario(self.rol).label

    # ======================================================
    # PROPIEDADES DE AUTENTICACIÓN
    # ======================================================

    @property
    def is_staff(self):
        return self.rol == RolUsuario.ADMIN

    @property
    def is_superuser(self):
        return self.rol == RolUsuario.ADMIN

    @property
    def is_active(self):
        return self.estado

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser




# ==========================================================
# NOTIFICACIONES
# ==========================================================

class Notificacion(models.Model):

    TIPO_CHOICES = (
        ('venta', 'Venta'),
        ('reserva', 'Reserva'),
        ('usuario', 'Usuario'),
        ('producto', 'Producto'),
        ('servicio', 'Servicio'),
        ('promocion', 'Promoción'),
        ('sistema', 'Sistema'),
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Destinatario',
        db_column='usuario_id'
    )

    # ======================================================
    # RELACIONES CON LOS MÓDULOS
    # ======================================================

    reserva = models.ForeignKey(
        'reservas.Reserva',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name='Reserva relacionada',
    )

    venta = models.ForeignKey(
        'venta.Venta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name='Venta relacionada',
    )

    producto = models.ForeignKey(
        'catalogo.Producto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name='Producto relacionado',
    )

    servicio = models.ForeignKey(
        'servicios.Servicios',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name='Servicio relacionado',
    )

    usuario_afectado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones_como_afectado',
        verbose_name='Usuario afectado',
    )

    # ======================================================
    # DATOS DE LA NOTIFICACIÓN
    # ======================================================

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo',
        db_column='tipo'
    )

    mensaje = models.CharField(
        max_length=255,
        verbose_name='Mensaje',
        db_column='mensaje'
    )

    url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='URL',
        db_column='url'
    )

    leida = models.BooleanField(
        default=False,
        verbose_name='Leída',
        db_column='leida'
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha',
        db_column='fecha'
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        db_table = 'notificaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} - {self.mensaje}"


# ==========================================================
# HISTORIAL DE ACCIONES
# ==========================================================

class HistorialAccion(models.Model):

    ACCION_CHOICES = (
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('reservar', 'Reservar'),
        ('comprar', 'Comprar'),
        ('cancelar', 'Cancelar'),
        ('confirmar', 'Confirmar'),
        ('cambiar_estado', 'Cambiar Estado'),
        ('reprogramar', 'Reprogramar'),
        ('otro', 'Otro'),
    )

    TIPO_CHOICES = (
        ('reserva', 'Reserva'),
        ('venta', 'Venta'),
        ('producto', 'Producto'),
        ('servicio', 'Servicio'),
        ('usuario', 'Usuario'),
        ('promocion', 'Promoción'),
        ('categoria', 'Categoría'),
        ('marca', 'Marca'),
        ('proveedor', 'Proveedor'),
        ('agenda', 'Agenda'),
        ('sistema', 'Sistema'),
    )

    # ======================================================
    # USUARIO QUE REALIZÓ LA ACCIÓN
    # ======================================================

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_acciones',
        verbose_name='Usuario que realizó la acción',
    )

    # ======================================================
    # OBJETOS RELACIONADOS
    # ======================================================

    reserva = models.ForeignKey(
        'reservas.Reserva',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_acciones',
        verbose_name='Reserva',
    )

    venta = models.ForeignKey(
        'venta.Venta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_acciones',
        verbose_name='Venta',
    )

    producto = models.ForeignKey(
        'catalogo.Producto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_acciones',
        verbose_name='Producto',
    )

    servicio = models.ForeignKey(
        'servicios.Servicios',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_acciones',
        verbose_name='Servicio',
    )

    usuario_afectado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_como_afectado',
        verbose_name='Usuario afectado',
    )

    # ======================================================
    # DATOS DE LA ACCIÓN
    # ======================================================

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Acción',
    )

    accion = models.CharField(
        max_length=30,
        choices=ACCION_CHOICES,
        verbose_name='Acción',
    )

    descripcion = models.TextField(
        verbose_name='Descripción',
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha',
    )

    class Meta:
        verbose_name = 'Historial de Acción'
        verbose_name_plural = 'Historial de Acciones'
        db_table = 'historial_acciones'
        ordering = ['-fecha']

    def __str__(self):

        usuario = (
            self.usuario.get_full_name()
            if self.usuario
            else 'Sistema'
        )

        return (
            f"{usuario} - "
            f"{self.get_accion_display()} - "
            f"{self.fecha:%d/%m/%Y %H:%M}"
        )
