$(document).ready(function() {
    $('#genres').select2({
        placeholder: 'Elige tu género favorito',
    });

    $('#epocas').select2({
        placeholder: 'Elige tu época favorita',
    });
});

window.onload = function() {
    fetch('/genres')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('genres');
            data.forEach(genre => {
                const option = document.createElement('option');
                option.value = genre.id;
                option.text = genre.name;
                select.add(option);
            });
        });
};