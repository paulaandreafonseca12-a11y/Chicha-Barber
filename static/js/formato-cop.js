window.formatearMonedaCOP = function (valor) {
    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return "$ 0";
    }

    const formato = new Intl.NumberFormat("es-CO", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
    const valorFormateadoConCentavos = formato.format(Math.abs(numero));
    const valorFormateado = valorFormateadoConCentavos.endsWith(",00")
        ? valorFormateadoConCentavos.slice(0, -3)
        : valorFormateadoConCentavos;

    return numero < 0
        ? `-$ ${valorFormateado}`
        : `$ ${valorFormateado}`;
};
