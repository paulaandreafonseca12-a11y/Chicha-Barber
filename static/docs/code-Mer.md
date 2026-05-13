erDiagram
    %% ================= MÓDULO: USUARIOS =================
    USUARIO ||--o{ TURNO : "Ofrece (Profesional)"
    USUARIO ||--o{ RESERVA : "Realiza (Cliente)"
    USUARIO ||--o{ FACTURA : "Paga (Cliente)"

    USUARIO {
        int id PK "Ej: 15"
        string documento "Ej: 1049123456"
        string nombre "Ej: Antony Reynel"
        string apellido "Ej: Botello"
        string email "Ej: antony@email.com"
        string telefono "Ej: 3123456789"
        string rol "ENUM: ADMIN, BARBERO, CLIENTE"
        boolean estado "Ej: True (Activo)"
    }

    %% ================= MÓDULO: RESERVAS =================
    TURNO ||--o| RESERVA : "Ocupado por"
    RESERVA ||--o| CALIFICACION : "Recibe"
    RESERVA ||--|| SERVICIO : "Incluye"

    TURNO {
        int id PK "Ej: 1045"
        int profesional_id FK "Ej: 15 (ID de Antony)"
        date fecha "Ej: 2026-05-13"
        time hora_inicio "Ej: 14:00"
        time hora_fin "Ej: 15:00"
        string estado "Ej: Reservado"
    }
    RESERVA {
        int id PK "Ej: 502"
        int turno_id FK "Ej: 1045"
        int cliente_id FK "Ej: 89 (ID del Cliente)"
        int servicio_id FK "Ej: 3 (Corte Clásico)"
        float precio_historico "Ej: 25000.00"
        string estado "Ej: Completada"
    }
    CALIFICACION {
        int id PK "Ej: 120"
        int reserva_id FK "Ej: 502"
        int puntuacion "Ej: 5"
        string comentario "Ej: Excelente atención y puntualidad"
    }

    %% ================= MÓDULO: SERVICIOS =================
    SERVICIO ||--o{ PROMOCION : "Tiene"

    SERVICIO {
        int id PK "Ej: 3"
        string nombre "Ej: Corte Clásico + Barba"
        float precio_actual "Ej: 25000.00"
        int duracion_minutos "Ej: 60"
        boolean estado "Ej: True"
    }
    PROMOCION {
        int id PK "Ej: 1"
        int servicio_id FK "Ej: 3"
        string nombre "Ej: Descuento Madrugadores"
        float porcentaje_descuento "Ej: 15.0"
        date fecha_inicio "Ej: 2026-05-01"
        date fecha_fin "Ej: 2026-05-31"
        boolean estado "Ej: True"
    }

    %% ================= MÓDULO: INVENTARIO =================
    PRODUCTO ||--o{ MOVIMIENTO_INVENTARIO : "Registra"

    PRODUCTO {
        int id PK "Ej: 20"
        string nombre "Ej: Cera Mate Nishman 100g"
        string descripcion "Ej: Cera moldeadora acabado mate"
        float precio_compra "Ej: 12000.00"
        float precio_venta "Ej: 20000.00"
        int stock_actual "Ej: 14"
        boolean estado "Ej: True"
    }
    MOVIMIENTO_INVENTARIO {
        int id PK "Ej: 850"
        int producto_id FK "Ej: 20"
        string tipo "Ej: Salida"
        int cantidad "Ej: 1"
        datetime fecha "Ej: 2026-05-13 14:50:00"
        string motivo "Ej: Venta en mostrador"
    }

    %% ================= MÓDULO: FACTURACIÓN =================
    FACTURA ||--o{ DETALLE_FACTURA : "Contiene"
    DETALLE_FACTURA ||--o| PRODUCTO : "Vende (Opcional)"
    DETALLE_FACTURA ||--o| RESERVA : "Cobra (Opcional)"

    FACTURA {
        int id PK "Ej: 3001"
        int cliente_id FK "Ej: 89"
        datetime fecha_emision "Ej: 2026-05-13 15:00:00"
        float total_pagado "Ej: 45000.00"
        string metodo_pago "Ej: Nequi, Daviplata, Efectivo"
        string estado "Ej: Pagada"
    }
    DETALLE_FACTURA {
        int id PK "Ej: 6005"
        int factura_id FK "Ej: 3001"
        int producto_id FK "Ej: Null (Si es servicio)"
        int reserva_id FK "Ej: 502 (ID de la Reserva)"
        int cantidad "Ej: 1"
        float precio_unitario "Ej: 25000.00"
        float subtotal "Ej: 25000.00"
    }

    %% ================= MÓDULO: CONFIGURACIÓN =================
    CARRUSEL {
        int id PK "Ej: 1"
        datetime fecha_creacion "Ej: 2026-05-01 10:00:00"
        datetime fecha_modificacion "Ej: 2026-05-10 08:30:00"
        string nombre "Ej: Banner Promo Mayo"
        string imagen "Ej: carrusel/banner_mayo_1.jpg"
        string texto "Ej: Aprovecha un 15% de descuento"
        boolean estado "Ej: True"
    }