$(document).ready(function() {
    $('#generos').select2({
        placeholder: 'Elige tu género favorito',
    });

    $('#epocas').select2({
        placeholder: 'Elige tu época favorita',
    });
});

window.onload = function() {
    // Fetch genres
    fetch('/genres')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('generos');
            data.forEach(genre => {
                const option = document.createElement('option');
                option.value = genre.id;
                option.text = genre.name;
                select.add(option);
            });
        });

    // Generate years
    const select = document.getElementById('epocas');
    for (let year = 1900; year <= 2020; year += 10) {
        const option = document.createElement('option');
        option.value = `${year}-${year+9}`;
        option.text = `${year}-${year+9}`;
        select.add(option);
    }
};