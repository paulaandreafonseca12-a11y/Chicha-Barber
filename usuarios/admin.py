from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario, RegistroActividad, Notificacion
from .forms import CrearUsuarioAdminForm


# =========================================================
# ADMINISTRACIÓN DE USUARIOS
# =========================================================

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    # UsuarioAdmin ya no puede reutilizar los fieldsets/list_display
    # por defecto de UserAdmin, porque nuestro modelo Usuario es
    # totalmente personalizado (hereda de AbstractBaseUser, no de
    # AbstractUser) y no tiene username, first_name, last_name,
    # date_joined, groups ni user_permissions. is_staff/is_superuser/
    # is_active son @property calculadas, no columnas editables.

    model = Usuario
    add_form = CrearUsuarioAdminForm

    # =====================================================
    # FORMULARIO PARA CREAR USUARIOS
    # =====================================================

    add_fieldsets = (
        (
            'Información de acceso',
            {
                'fields': (
                    'email',
                    'password1',
                    'password2',
                )
            }
        ),

        (
            'Información personal',
            {
                'fields': (
                    'tipo_documento',
                    'numero_documento',
                    'primer_nombre',
                    'segundo_nombre',
                    'primer_apellido',
                    'segundo_apellido',
                    'telefono',
                    'foto_perfil',
                )
            }
        ),

        (
            'Rol y configuración',
            {
                'fields': (
                    'rol',
                    'estado',
                    'especialidad',
                    'tema',
                )
            }
        ),
    )

    # =====================================================
    # LISTADO DE USUARIOS
    # =====================================================

    list_display = (
        'email',
        'tipo_documento',
        'primer_nombre',
        'primer_apellido',
        'telefono',
        'rol',
        'estado',
        'fecha_creacion',
    )

    # =====================================================
    # FILTROS
    # =====================================================

    list_filter = (
        'rol',
        'estado',
        'tipo_documento',
    )

    # =====================================================
    # BÚSQUEDA
    # =====================================================

    search_fields = (
        'email',
        'primer_nombre',
        'primer_apellido',
        'numero_documento',
        'telefono',
    )

    # =====================================================
    # ORDEN
    # =====================================================

    ordering = ('-fecha_creacion',)

    # =====================================================
    # CAMPOS DE SOLO LECTURA
    # =====================================================

    readonly_fields = (
        'last_login',
        'fecha_creacion',
    )

    # Al no tener username, Django necesita saber cuál es
    # el "identificador visual" de cada usuario en el admin.
    filter_horizontal = ()

    # =====================================================
    # FORMULARIO PARA EDITAR USUARIOS
    # =====================================================

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                    'tipo_documento',
                    'numero_documento',
                )
            }
        ),

        (
            'Información personal',
            {
                'fields': (
                    'primer_nombre',
                    'segundo_nombre',
                    'primer_apellido',
                    'segundo_apellido',
                    'telefono',
                    'foto_perfil',
                )
            }
        ),

        (
            'Rol y estado',
            {
                'fields': (
                    'rol',
                    'estado',
                    'especialidad',
                    'tema',
                )
            }
        ),

        (
            'Fechas',
            {
                'fields': (
                    'last_login',
                    'fecha_creacion',
                )
            }
        ),
    )

    # =====================================================
    # GUARDAR USUARIO
    # =====================================================

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


# =========================================================
# REGISTRO DE ACTIVIDADES
# =========================================================

@admin.register(RegistroActividad)
class RegistroActividadAdmin(admin.ModelAdmin):

    list_display = (
        'usuario',
        'tipo',
        'descripcion',
        'fecha',
    )

    list_filter = (
        'tipo',
        'fecha',
    )

    search_fields = (
        'descripcion',
        'usuario__email',
    )


# =========================================================
# NOTIFICACIONES
# =========================================================

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):

    list_display = (
        'usuario',
        'tipo',
        'mensaje',
        'leida',
        'fecha',
    )

    list_filter = (
        'tipo',
        'leida',
        'fecha',
    )

    search_fields = (
        'mensaje',
        'usuario__email',
    )