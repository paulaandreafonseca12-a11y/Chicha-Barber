erDiagram
    USUARIO ||--o{ RESERVA : "Pertenece"
    USUARIO ||--o{ ROL : "Posee"
    
    RESERVA ||--|| AGENDA : "Pertenece"
    RESERVA ||--o{ CALIFICACION : "Corresponde"
    RESERVA ||--|| SERVICIO : "Pertenece"
    
    SERVICIO ||--o{ PROMOCION : "Corresponde"
    
    FACTURA ||--|| RESERVA : "Corresponde"
    FACTURA ||--|| COMPRA : "Tiene"
    
    COMPRA ||--o{ DETALLE_COMPRA : "Corresponde"
    
    DETALLE_COMPRA ||--|| STOCK : "Corresponde"
    
    STOCK ||--|| PRODUCTO : "Tiene"

    USUARIO {
        string documento PK
        string nombre
        string apellido
        string telefono
        string especialidad
        string cod_rol FK
    }

    ROL {
        string cod_rol PK
        string nombre_rol
    }

    AGENDA {
        string cod_cita PK
        string usuario
        datetime datetime
    }

    RESERVA {
        string cod PK
        date fecha
        time hora
        string codigo_calificacion FK
        string codigo_usuario FK
    }

    CALIFICACION {
        string cod PK
        string comentario
        int calificacion
    }

    SERVICIO {
        string cod PK
        string nombre
        float precio
        string duracion
        string codigo_cita_servicio FK
    }

    PROMOCION {
        string cod PK
        string cod_servici FK
        string nombre
        float descuento
        date fecha_final
    }

    FACTURA {
        string cod PK
        date fecha
        string metodo
        string cod_servicio FK
        string cod_venta FK
    }

    COMPRA {
        string cod PK
        date fecha
        float total
    }

    DETALLE_COMPRA {
        string cod_producto PK
        string nombre
        string descripcion
        string codigo_stock FK
    }

    STOCK {
        string cod PK
        int cantidad
        string cod_producto FK
    }

    PRODUCTO {
        string cod PK
        string nombre
        string descripcion
        float precio_venta
        float precio_compra
    }


