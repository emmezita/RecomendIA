'use strict';

var moveOutHeight = document.body.clientHeight * 1.5;

var tinderContainer = document.querySelector('.tinder');
var allCards = document.querySelectorAll('.tinder--card');
var nolove = document.getElementById('nolove');
var love = document.getElementById('love');
var ignore = document.getElementById('ignore');
var genre_json = [];

console.log(recomendaciones_json);

window.onload = function() {
  fetch('/genres')
      .then(response => response.json())
      .then(data => {
          genre_json = data;
      });
};

// cambiar la informacion que se muestra en el modal
function showModal(id) {
  var dialog = document.getElementById('info_modal');

  // buscar la informacion de la pelicula dentro del json de recomendaciones
  var movie = recomendaciones_json.find(movie => movie.movie_id == id);

  document.querySelector('.movie-title').innerText = movie.title;
  document.querySelector('.movie-desc').innerText = movie.description;
  //generos_pelicula es un string con los ids de los generos separados por comas
  let generos_pelicula_id = movie.genre_id.split(",");
  let generos_bien = generos_pelicula_id.map(genre_id => genre_json.find(genre => genre.id == genre_id).name);
  document.querySelector('.movie-genres').innerText = `Genres: ${generos_bien.join(', ')}`;
  document.querySelector('.movie-release').innerText = `Release Date: ${movie.age_release}`;
  dialog.showModal();
}

function initCards(card, index) {
  var newCards = document.querySelectorAll('.tinder--card:not(.removed)');

  // Verificar si newCards contiene elementos
  if (newCards.length > 0) {
      newCards.forEach(function(card, index) {
          card.style.zIndex = allCards.length - index;
          card.style.transform = 'scale(' + (20 - index) / 20 + ') translateY(-' + 30 * index + 'px)';
          card.style.opacity = (10 - index) / 10;
      });
  }

  tinderContainer.classList.add('loaded');
}

initCards();

function initializeHammer() {
  allCards.forEach(function (el) {

    // Check if the element has already been initialized
    if (el.getAttribute('data-hammer-initialized')) return;

    var hammertime = new Hammer(el, {
      recognizers: [
        [Hammer.Pan, { direction: Hammer.DIRECTION_ALL }]
      ]
    });

    hammertime.on('pan', function (event) {
        el.classList.add('moving');
    });

    hammertime.on('pan', function (event) {
      if (event.deltaX === 0) return;
      if (event.center.x === 0 && event.center.y === 0) return;

      // Remove all classes first
      tinderContainer.classList.remove('tinder_love', 'tinder_nolove', 'tinder_ignore');

      // Then add the appropriate class based on deltaX and deltaY
      if (event.deltaX > 80) {
        tinderContainer.classList.add('tinder_love');
      } else if (event.deltaX < -80) {
        tinderContainer.classList.add('tinder_nolove');
      } else if (event.deltaY < -150) {
        tinderContainer.classList.add('tinder_ignore');
      }

      var xMulti = event.deltaX * 0.03;
      var yMulti = event.deltaY / 100;
      var rotate = xMulti * yMulti;

      el.style.transform = 'translate(' + event.deltaX + 'px, ' + event.deltaY + 'px) rotate(' + rotate + 'deg)';
    });

    hammertime.on('panend', function (event) {
        el.classList.remove('moving');
        tinderContainer.classList.remove('tinder_love');
        tinderContainer.classList.remove('tinder_nolove');
        tinderContainer.classList.remove('tinder_ignore');

        var moveOutWidth = document.body.clientWidth;
        var moveOutHeight = document.body.clientHeight;
        var keep = Math.abs(event.deltaX) < 80
        var ignore = event.deltaY < -150 ;

        if (keep && !ignore) {
          el.style.transform = '';
        } else {
            if (ignore) {
                console.log("IGNORING");
                var endY = Math.abs(event.velocityY) * moveOutHeight;
                var toY = event.deltaY > 0 ? endY : -endY;
                var upperMoveOutHeight = moveOutHeight * -1.2;

                // el.style.transform = 'translate(0, ' + upperMoveOutHeight + 'px)';
                ignoreListener();
            } else {
                var endX = Math.max(Math.abs(event.velocityX) * moveOutWidth, moveOutWidth);
                var toX = event.deltaX > 0 ? endX : -endX;
                var endY = Math.abs(event.velocityY) * moveOutWidth;
                var toY = event.deltaY > 0 ? endY : -endY;
                var xMulti = event.deltaX * 0.03;
                var yMulti = event.deltaY / 80;
                var rotate = xMulti * yMulti;

                if (toX > 0) {
                    loveListener();
                } else {
                    noloveListener();
                }

                // el.style.transform = 'translate(' + toX + 'px, ' + (toY + event.deltaY) + 'px) rotate(' + rotate + 'deg)';
              }
              initCards();
            }
        // el.classList.toggle('removed', !keep || ignore); 
        });

    // Add the custom attribute to indicate that the element has been initialized
    el.setAttribute('data-hammer-initialized', 'true');
  });
}

initializeHammer();

    function createButtonListener(action) {
      return function (event) {
        var cards = document.querySelectorAll('.tinder--card:not(.removed)');
        var moveOutWidth = document.body.clientWidth * 1.5;
        var moveOutHeight = document.body.clientHeight * 1.5;

        if (!cards.length) return false;

        var card = cards[0];

        card.classList.add('removed');

        if (action === 'love') {
          card.style.transform = 'translate(' + moveOutWidth + 'px, -100px) rotate(-30deg)';
        } else if (action === 'nolove') {
          card.style.transform = 'translate(-' + moveOutWidth + 'px, -100px) rotate(30deg)';
        } else if (action === 'ignore') {
          card.style.transform = 'translate(0, -' + moveOutHeight + 'px)';
        }

        initCards();

        // Obtener el ID de la película
        var movieId = card.dataset.movieid;
        console.log('Valor de movieId:', movieId);

        // Determinar si se está ignorando
        var ignore = action === 'ignore';

        console.log('love or nolove:', action)
        console.log('ignore:', ignore)

        // Enviar la interacción del usuario al servidor
        guardar_interaccion(movieId, action, ignore);

        // event.preventDefault();

        // si es la penultima carta, pedir nuevas recomendaciones
        if (cards.length === 1) {
            nuevas_recomendaciones();
        }
      };
    }

var noloveListener = createButtonListener('nolove');
var loveListener = createButtonListener('love');
var ignoreListener = createButtonListener('ignore'); // Nuevo listener

nolove.addEventListener('click', noloveListener);
love.addEventListener('click', loveListener);
ignore.addEventListener('click', ignoreListener); // Agregar el listener al boton ignore

// Función para guardar la interacción del usuario
function guardar_interaccion(movieId, action, ignore) {
  // ignore = 2, love = 1, nolove = 0
    var valoracion = ignore ? 2 : (action === 'love' ? 1 : 0);

    // Crear un objeto con los datos a enviar
    var data = {
        movie_id: String(movieId),
        action: action,
        valoracion: valoracion
    };

    // Realizar la solicitud AJAX al servidor
    fetch('/guardar_interaccion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            console.log('Interacción del usuario guardada correctamente.');
            console.log(movieId)
        } else {
            console.error('Error al guardar la interacción del usuariooo.');
            response.json().then(data => {
                console.error(data);
            });
        }
    })
    .catch(error => {
        console.error('Error al guardar la interacción del usuario:', error);
    });
}

function nuevas_recomendaciones() {
    // Realizar la solicitud AJAX al servidor
    fetch('/mostrar_recomendaciones', {
        method: 'GET'
    })
    .then(response => {
        if (response.ok) {
            console.log('Nuevas recomendaciones obtenidas correctamente.');
            response.json().then(data => {
                var newCards = data;
                console.log(newCards);
                newCards.forEach(function (card) {
                  card.image_url = "https://image.tmdb.org/t/p/w500" + card.image_url;
                  add_card(card);
                });
                allCards = document.querySelectorAll('.tinder--card:not(.removed)');
                initCards();
                initializeHammer();
                recomendaciones_json = recomendaciones_json.concat(newCards);
            });
        } else {
            console.error('Error al obtener nuevas recomendaciones.');
            response.json().then(data => {
                console.error(data);
            });
        }
    })
    .catch(error => {
        console.error('Error al obtener nuevas recomendaciones:', error);
    });
}

function add_card(card) {
    var newCard = document.createElement('div');
    newCard.classList.add('tinder--card');
    newCard.dataset.movieid = card.movie_id;
    newCard.innerHTML = `
        <button class="info-button" onclick="showModal(${card.movie_id})">
            <i class="fas fa-info-circle"></i>
        </button>
        <div class="tinder--card-image h-[100%]">
            <img class="object-cover w-full h-full" src="${card.image_url}" alt="${card.title}">
        </div>
    `;
    let tinderCards = document.querySelector('.tinder--cards');
    tinderCards.appendChild(newCard);
}
