from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


# ---------------------------------------------------------------------------
# Choices reutilizables
# ---------------------------------------------------------------------------

class TipoDocumento(models.TextChoices):
    CC = 'CC', 'Cédula de ciudadanía'
    TI = 'TI', 'Tarjeta de identidad'
    CE = 'CE', 'Cédula de extranjería'
    PA = 'PA', 'Pasaporte'


class RolUsuario(models.TextChoices):
    ADMIN = 'admin', 'Administrador'
    BARBERO = 'barbero', 'Barbero'
    CLIENTE = 'cliente', 'Cliente'


class UsuarioManager(BaseUserManager):
    """Manager personalizado: obligatorio al usar AbstractBaseUser,
    ya que este no trae ninguno por defecto."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('rol', RolUsuario.ADMIN)
        usuario = self.create_user(email, password, **extra_fields)
        return usuario


class Usuario(AbstractBaseUser):
    objects = UsuarioManager()

    # --- password y last_login: AbstractBaseUser los agrega automáticamente,
    #     no hace falta (ni se puede) volver a declararlos aquí ---

    primer_nombre = models.CharField(
        max_length=150, blank=True,
        verbose_name='Primer nombre',
        db_column='primer_nombre'
    )
    segundo_nombre = models.CharField(
        max_length=150, blank=True, null=True,
        verbose_name='Segundo nombre',
        db_column='segundo_nombre'
    )
    primer_apellido = models.CharField(
        max_length=150, blank=True,
        verbose_name='Primer apellido',
        db_column='primer_apellido'
    )
    segundo_apellido = models.CharField(
        max_length=150, blank=True, null=True,
        verbose_name='Segundo apellido',
        db_column='segundo_apellido'
    )
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
    estado = models.BooleanField(
        default=True,
        verbose_name='Estado (activo/inactivo)',
        db_column='estado'
    )
    foto_perfil = models.ImageField(
        upload_to='usuarios/',
        blank=True, null=True,
        verbose_name='Foto de perfil',
        db_column='foto_perfil'
    )

    # --- Campos agregados ---
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
    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.CLIENTE,
        verbose_name='Rol',
        db_column='rol'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación de la cuenta',
        db_column='fecha_creacion'
    )

    # --- Campos ya en uso que se mantienen ---
    tema = models.CharField(
        max_length=10,
        default='dark',
        choices=[('light', 'Claro'), ('dark', 'Oscuro')],
        verbose_name='Tema',
        db_column='tema'
    )
    especialidad = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name='Especialidad',
        db_column='especialidad'
    )

    # Configuración de login: entran con el EMAIL
    USERNAME_FIELD = 'email'
    # Campos que pide 'createsuperuser' (no incluyas EMAIL ni PASSWORD)
    REQUIRED_FIELDS = ['primer_nombre', 'primer_apellido',
                        'tipo_documento', 'numero_documento']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    def get_full_name(self):
        partes = [self.primer_nombre, self.segundo_nombre,
                  self.primer_apellido, self.segundo_apellido]
        return ' '.join(p for p in partes if p)

    def get_short_name(self):
        return self.primer_nombre

    def get_rol_display(self):
        return RolUsuario(self.rol).label

    # --- Propiedades calculadas: NO generan columna en MySQL ---
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


class RegistroActividad(models.Model):
    TIPO_CHOICES = (
        ('usuario', 'Usuario'),
        ('producto', 'Producto'),
        ('servicio', 'Servicio'),
        ('reserva', 'Reserva'),
        ('promocion', 'Promoción'),
        ('sesion', 'Sesión'),
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='actividades',
        verbose_name='Usuario que realizó la acción',
        db_column='usuario_id'
    )
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES,
        verbose_name='Tipo',
        db_column='tipo'
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name='Descripción',
        db_column='descripcion'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha',
        db_column='fecha'
    )

    class Meta:
        verbose_name = 'Registro de actividad'
        verbose_name_plural = 'Registros de actividad'
        db_table = 'registros_actividad'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} - {self.descripcion} ({self.fecha:%d/%m/%Y %H:%M})"


class Notificacion(models.Model):
    TIPO_CHOICES = (
        ('venta', 'Venta'),
        ('reserva', 'Reserva'),
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Destinatario',
        db_column='usuario_id'
    )
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES,
        verbose_name='Tipo',
        db_column='tipo'
    )
    mensaje = models.CharField(
        max_length=255,
        verbose_name='Mensaje',
        db_column='mensaje'
    )
    url = models.CharField(
        max_length=255, blank=True, null=True,
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
    
    
    
                