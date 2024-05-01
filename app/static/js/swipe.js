'use strict';

var tinderContainer = document.querySelector('.tinder');
var allCards = document.querySelectorAll('.tinder--card');
var nolove = document.getElementById('nolove');
var love = document.getElementById('love');
var ignore = document.getElementById('ignore');

function initCards(card, index) {
  var newCards = document.querySelectorAll('.tinder--card:not(.removed)');

  newCards.forEach(function (card, index) {
    card.style.zIndex = allCards.length - index;
    card.style.transform = 'scale(' + (20 - index) / 20 + ') translateY(-' + 30 * index + 'px)';
    card.style.opacity = (10 - index) / 10;
  });
  
  tinderContainer.classList.add('loaded');
}

initCards();

allCards.forEach(function (el) {
  var hammertime = new Hammer(el);

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
  
    // console.log("DELTAX", event.deltaX);
  
    var xMulti = event.deltaX * 0.03;
    var yMulti = event.deltaY / 100;
    var rotate = xMulti * yMulti;
  
    event.target.style.transform = 'translate(' + event.deltaX + 'px, ' + event.deltaY + 'px) rotate(' + rotate + 'deg)';
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
  
    console.log("IGNORE",event.deltaY);
    // console.log("KEEP", keep);

    event.target.classList.toggle('removed', !keep || ignore); // Modify this line
    

    if (keep && !ignore) { 
      console.log("KEEPING");
      event.target.style.transform = '';
    } else {
        if (ignore) {
            console.log("IGNORING");
            var endY = Math.abs(event.velocityY) * moveOutHeight;
            var toY = event.deltaY > 0 ? endY : -endY;
            var upperMoveOutHeight = moveOutHeight * -1.2;
            event.target.style.transform = 'translate(0, ' + upperMoveOutHeight + 'px)';
        } else {
            var endX = Math.max(Math.abs(event.velocityX) * moveOutWidth, moveOutWidth);
            var toX = event.deltaX > 0 ? endX : -endX;
            var endY = Math.abs(event.velocityY) * moveOutWidth;
            var toY = event.deltaY > 0 ? endY : -endY;
            var xMulti = event.deltaX * 0.03;
            var yMulti = event.deltaY / 80;
            var rotate = xMulti * yMulti;

            if (toX > 0) {
                console.log("LOVING");
            }
            else {
                console.log("NOT LOVING");
            }                

            event.target.style.transform = 'translate(' + toX + 'px, ' + (toY + event.deltaY) + 'px) rotate(' + rotate + 'deg)';
        }
            initCards();
    }
  });

});

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

    event.preventDefault();
  };
}

var noloveListener = createButtonListener('nolove');
var loveListener = createButtonListener('love');
var ignoreListener = createButtonListener('ignore'); // Nuevo listener

nolove.addEventListener('click', noloveListener);
love.addEventListener('click', loveListener);
ignore.addEventListener('click', ignoreListener); // Agregar el listener al botón ignore