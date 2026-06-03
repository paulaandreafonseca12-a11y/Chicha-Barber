from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que se verán en la tabla principal del panel de administración
    list_display = ('email', 'username', 'first_name', 'last_name', 'rol', 'estado', 'is_staff')
    
    # Filtros laterales para buscar usuarios rápidamente por su rol o estado
    list_filter = ('rol', 'estado', 'is_staff')
    
    # Campos por los que podrás buscar en la barra de búsqueda
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    # Agregamos tus campos personalizados al formulario de edición del usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información de la Barbería', {
            'fields': ('telefono', 'rol', 'estado', 'tema', 'especialidad', 'foto_perfil')
        }),
    )

    # Agregamos tus campos personalizados al formulario de creación de usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de la Barbería', {
            'fields': ('telefono', 'rol', 'estado', 'tema', 'especialidad', 'foto_perfil')
        }),
    )