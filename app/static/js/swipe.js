'use strict';

var moveOutHeight = document.body.clientHeight * 1.5;

var tinderContainer = document.querySelector('.tinder');
var allCards = document.querySelectorAll('.tinder--card');
var buttonsContainer = document.querySelector('.tinder--buttons');

buttonsContainer.addEventListener('click', function(event) {
    var button = event.target.closest('button');
    if (!button) return;

    var action = button.getAttribute('id');
    var card = document.querySelector('.tinder--card:not(.removed)');

    if (!card) return;

    card.classList.add('removed');
    var moveOutWidth = document.body.clientWidth * 1.5;

    if (action === 'love') {
        card.style.transform = 'translate(' + moveOutWidth + 'px, -100px) rotate(-30deg)';
    } else if (action === 'nolove') {
        card.style.transform = 'translate(-' + moveOutWidth + 'px, -100px) rotate(30deg)';
    } else if (action === 'ignore') {
        card.style.transform = 'translate(0, -' + moveOutHeight + 'px)';
    }

    initCards();

    // Obtener el ID de la película
    var movieId = card.dataset.movieId;

    // Determinar si se está ignorando
    var ignore = action === 'ignore';

    // Enviar la interacción del usuario al servidor
    saveInteraction(movieId, action, ignore);

    event.preventDefault();
});

function initCards() {
    var newCards = document.querySelectorAll('.tinder--card:not(.removed)');

    newCards.forEach(function(card, index) {
        card.style.zIndex = allCards.length - index;
        card.style.transform = 'scale(' + (20 - index) / 20 + ') translateY(-' + 30 * index + 'px)';
        card.style.opacity = (10 - index) / 10;
    });

    tinderContainer.classList.add('loaded');
}

initCards();

// Función para guardar la interacción del usuario
function saveInteraction(movieId, action, ignore) {
    var valoracion = ignore ? 2 : (action === 'love' ? 1 : 0);

    // Crear un objeto con los datos a enviar
    var data = {
        movie_id: movieId,
        action: action,
        valoracion: valoracion
    };

    // Realizar la solicitud AJAX al servidor
    fetch('/save_interaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            console.log('Interacción del usuario guardada correctamente.');
        } else {
            console.error('Error al guardar la interacción del usuario.');
        }
    })
    .catch(error => {
        console.error('Error al guardar la interacción del usuario:', error);
    });
}
