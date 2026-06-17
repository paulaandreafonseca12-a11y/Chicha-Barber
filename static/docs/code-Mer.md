erDiagram
    %% ================= MÓDULO: USUARIOS =================
    USUARIO ||--o{ TURNO : "Ofrece (Rol: BARBERO)"
    USUARIO ||--o{ RESERVA : "Realiza (Rol: CLIENTE)"
    USUARIO ||--o{ FACTURA : "Se le asigna"
    USUARIO ||--o{ COMPRA : "Registra (Venta Online)"

    USUARIO {
        int id PK
        string username "Documento / ID único"
        string first_name "Nombre"
        string last_name "Apellido"
        string email
        string telefono
        string rol "ENUM: admin, barbero, cliente"
        boolean estado "Activo/Inactivo"
        image foto_perfil
    }

    %% ================= MÓDULO: RESERVAS =================
    TURNO ||--o| RESERVA : "Asignado a"
    RESERVA ||--|| SERVICIO : "Solicita"
    RESERVA |o--o| PROMOCION : "Aplica (Opcional)"

    TURNO {
        int id PK
        int profesional_id FK "ID de Usuario (Barbero)"
        date fecha
        time hora_inicio
        time hora_fin
        string estado "disponible, reservado, cancelado"
    }
    RESERVA {
        int id PK
        int turno_id FK
        int cliente_id FK "ID de Usuario (Cliente)"
        int servicio_id FK
        int promocion_id FK
        string nombre_cliente "Nombre manual (Backup)"
        string correo_cliente
        string telefono_cliente
        float precio_historico "Precio al momento de reservar"
        string estado "reservada, confirmada, cancelada"
    }

    %% ================= MÓDULO: SERVICIOS =================
    SERVICIO ||--o{ PROMOCION : "Tiene"
    SERVICIO ||--o{ CALIFICACION : "Es evaluado"

    SERVICIO {
        int id PK
        string nombre
        decimal precio
        int duracion "Minutos"
        text descripcion
        image imagen
        boolean estado "Activo"
    }
    PROMOCION {
        int id PK
        int servicio_id FK
        string nombre
        decimal porcentaje_descuento
        string duracion "Texto (Ej: 2 Semanas)"
        text descripcion
        date fecha_inicio
        date fecha_fin
        image imagen
        boolean estado
    }
    CALIFICACION {
        int id PK
        int servicio_id FK
        string cliente "Nombre del autor"
        int puntuacion "1-5"
        text comentario
        datetime fecha_calificacion
        boolean mostrar_en_inicio
    }

    %% ================= MÓDULO: INVENTARIO =================
    PRODUCTO ||--|| STOCK : "Tiene (OneToOne)"
    PRODUCTO ||--o{ MOVIMIENTO_INVENTARIO : "Genera"
    PRODUCTO ||--o{ DETALLE_COMPRA : "Se incluye en"

    PRODUCTO {
        int codigo_producto PK
        string codigo "PROD-0000X"
        string nombre
        text descripcion
        decimal precio_compra
        decimal precio_venta
        image imagen
        boolean estado
    }
    STOCK {
        int id PK
        int producto_id FK
        int cantidad "Stock actual"
    }
    MOVIMIENTO_INVENTARIO {
        int id PK
        int producto_id FK
        string tipo "entrada/salida"
        int cantidad
        string motivo
        datetime fecha
    }

    %% ================= MÓDULO: COMPRAS (VENTA PRODUCTOS) =================
    COMPRA ||--o{ DETALLE_COMPRA : "Contiene"

    COMPRA {
        int codigo_compra PK
        int usuario_id FK "Cliente que compra"
        string nombre_cliente
        string correo
        string telefono
        string direccion
        decimal total
        string metodo_pago "persona, contraentrega, transferencia"
        string estado_pago "pendiente_verificacion, completado"
        file comprobante "Imagen del pago"
        datetime fecha_compra
    }
    DETALLE_COMPRA {
        int codigo_detalle PK
        int compra_id FK
        int producto_id FK
        int cantidad
        decimal subtotal
    }

    %% ================= MÓDULO: FACTURACIÓN =================
    FACTURA ||--o{ DETALLE_FACTURA : "Contiene"
    DETALLE_FACTURA |o--o| PRODUCTO : "Cobra"
    DETALLE_FACTURA |o--o| RESERVA : "Cobra"

    FACTURA {
        int id PK
        int cliente_id FK
        datetime fecha_emision
        float total_pagado
        string metodo_pago "efectivo, nequi, daviplata, etc."
        string estado "pendiente, pagada, cancelada"
        string nombre_cliente
        string correo_cliente
        string telefono_cliente
        image comprobante_pago
        image imagen_transaccion "Comprobante Admin"
    }
    DETALLE_FACTURA {
        int id PK
        int factura_id FK
        int producto_id FK "NULL si es servicio"
        int reserva_id FK "NULL si es producto"
        int cantidad
        decimal precio_unitario
        decimal subtotal
    }

    %% ================= MÓDULO: CONFIGURACIÓN =================
    DATOS_TRANSFERENCIA {
        int id PK "Singleton ID: 1"
        string banco
        string tipo_cuenta
        string numero_cuenta
        string titular
        text instructions
    }
    CARRUSEL {
        int id PK
        datetime fecha_creacion
        datetime fecha_modificacion
        string nombre
        string imagen
        string texto
        boolean estado
    }
