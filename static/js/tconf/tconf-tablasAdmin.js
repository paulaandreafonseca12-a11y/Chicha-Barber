$(function () {
  const lenguaje = {
    processing: "Procesando...",
    lengthMenu: "Mostrar _MENU_ registros",
    zeroRecords: "No se encontraron resultados",
    emptyTable: "Ningún dato disponible en esta tabla",
    info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
    infoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
    infoFiltered: "(filtrado de un total de _MAX_ registros)",
    search: "Buscar:",
    paginate: {
      first: "Primero",
      last: "Último",
      next: "Siguiente",
      previous: "Anterior",
    },
  };

  $("table[data-admin-datatable]").each(function () {
    const $tabla = $(this);
    const tieneFilaVacia = $tabla.find("tbody td[colspan]").length > 0;

    if (tieneFilaVacia || $.fn.DataTable.isDataTable(this)) {
      return;
    }

    const opciones = {
      language: lenguaje,
      responsive: true,
      autoWidth: false,
      pageLength: 10,
      lengthMenu: [
        [10, 25, 50, -1],
        [10, 25, 50, "Todos"],
      ],
      dom:
        '<"row align-items-center g-2 mb-3"<"col-12 col-md-4"l><"col-12 col-md-4 d-flex justify-content-center"B><"col-12 col-md-4"f>>' +
        '<"row"<"col-12"tr>>' +
        '<"row align-items-center mt-3"<"col-12 col-md-5"i><"col-12 col-md-7 d-flex justify-content-md-end"p>>',
      buttons: [
        {
          extend: "excelHtml5",
          text: '<i class="bi bi-file-earmark-excel"></i> Excel',
          className: "btn btn-sm dt-btn-excel",
          exportOptions: {
            columns: $tabla.is("[data-admin-table-actions]")
              ? ":not(:last-child)"
              : ":visible",
          },
        },
        {
          extend: "pdfHtml5",
          text: '<i class="bi bi-file-earmark-pdf"></i> PDF',
          className: "btn btn-sm dt-btn-pdf",
          exportOptions: {
            columns: $tabla.is("[data-admin-table-actions]")
              ? ":not(:last-child)"
              : ":visible",
          },
        },
        {
          extend: "print",
          text: '<i class="bi bi-printer"></i> Imprimir',
          className: "btn btn-sm dt-btn-print",
          exportOptions: {
            columns: $tabla.is("[data-admin-table-actions]")
              ? ":not(:last-child)"
              : ":visible",
          },
        },
      ],
    };

    if ($tabla.is("[data-admin-table-actions]")) {
      opciones.columnDefs = [
        { orderable: false, searchable: false, targets: -1 },
      ];
    }

    $tabla.DataTable(opciones);
  });

  $(document).on("shown.bs.tab", '[data-bs-toggle="tab"]', function () {
    $.fn.dataTable
      .tables({ visible: true, api: true })
      .columns.adjust()
      .responsive.recalc();
  });
});
