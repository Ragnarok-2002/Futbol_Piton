(function () {
    function filtrarNumeros(input) {
        if (input.dataset.validacionNumeros === '1') return;
        input.dataset.validacionNumeros = '1';
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '');
        });
    }

    function filtrarLetras(input) {
        if (input.dataset.validacionLetras === '1') return;
        input.dataset.validacionLetras = '1';
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s-]/g, '');
        });
    }

    function init() {
        document.querySelectorAll('.solo-numeros').forEach(filtrarNumeros);
        document.querySelectorAll('.solo-letras').forEach(filtrarLetras);
    }

    window.reiniciarValidacionCampos = init;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
