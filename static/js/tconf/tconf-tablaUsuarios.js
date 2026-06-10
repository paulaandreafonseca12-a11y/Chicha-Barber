$(document).ready(function () {
    var table = $('#tablaUsuarios').DataTable({
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
        },
        dom: "<'row align-items-center mb-3'" +
                 "<'col-auto'l>" +
                 "<'col text-center'B>" +
                 "<'col-auto'f>" +
             ">" +
             "<'row'<'col-sm-12'tr>>" +
             "<'row mt-2'<'col-sm-5'i><'col-sm-7'p>>",
        buttons: [
            {
                extend: 'excel',
                text: '<i class="bi bi-file-earmark-excel me-1"></i>Excel',
                className: 'btn btn-sm dt-btn-excel me-2',
                exportOptions: { columns: ':not(:last-child)' }
            },
            {
                extend: 'pdf',
                text: '<i class="bi bi-file-earmark-pdf me-1"></i>PDF',
                className: 'btn btn-sm dt-btn-pdf me-2',
                exportOptions: { columns: ':not(:last-child)' }
            },
            {
                extend: 'print',
                text: '<i class="bi bi-printer me-1"></i>Imprimir',
                className: 'btn btn-sm dt-btn-print',
                exportOptions: { columns: ':not(:last-child)' }
            }
        ],
        pageLength: 5,
        lengthMenu: [5, 10, 25, 50],
        columnDefs: [{ orderable: false, targets: 6 }]
    });

    $('.filtro-rol').on('click', function () {
        var rol = $(this).data('rol');

        // Resetear todos al estilo inactivo
        $('.filtro-rol')
            .removeClass('border-info text-info')
            .addClass('border-secondary text-secondary');

        // Activar el presionado
        $(this)
            .removeClass('border-secondary text-secondary')
            .addClass('border-info text-info');

        // Filtrar tabla
        if (rol === '') {
            table.column(3).search('').draw();
        } else if (rol === 'cliente') {
            table.column(3).search('Cliente', false, false, false).draw();
        } else if (rol === 'barbero') {
            table.column(3).search('Barbero', false, false, false).draw();
        }
    });
});