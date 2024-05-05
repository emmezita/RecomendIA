document.getElementById('togglePassword').addEventListener('click', function (e) {
    // Obtiene los elementos del DOM
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');
    const eyeOffIcon = document.getElementById('eyeOffIcon');

    // Si el tipo de entrada es 'password', lo cambia a 'text' y muestra el icono de 'ojo tachado'
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      eyeOffIcon.classList.add('hidden');
      eyeIcon.classList.remove('hidden');
    } 
    // Si el tipo de entrada es 'text', lo cambia a 'password' y muestra el icono de 'ojo'
    else {
      passwordInput.type = 'password';
      eyeOffIcon.classList.remove('hidden');
      eyeIcon.classList.add('hidden');
    }
});

document.getElementById('togglePasswordcf').addEventListener('click', function (e) {
    // Obtiene los elementos del DOM
    const passwordInput = document.getElementById('passwordcf');
    const eyeIcon = document.getElementById('eyeIconcf');
    const eyeOffIcon = document.getElementById('eyeOffIconcf');

    // Si el tipo de entrada es 'password', lo cambia a 'text' y muestra el icono de 'ojo tachado'
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      eyeOffIcon.classList.add('hidden');
      eyeIcon.classList.remove('hidden');
    } 
    // Si el tipo de entrada es 'text', lo cambia a 'password' y muestra el icono de 'ojo'
    else {
      passwordInput.type = 'password';
      eyeOffIcon.classList.remove('hidden');
      eyeIcon.classList.add('hidden');
    }
});


function showAlertAndRedirect(message) {
    alert(message); // Mostrar el mensaje emergente
    window.location.href = "/login"; // Redirigir a la página de inicio de sesión
}

document.getElementById("registerForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevenir el envío del formulario por defecto

    fetch('/register', {
        method: 'POST',
        body: new FormData(event.target)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlertAndRedirect(data.success); // Mostrar mensaje de éxito y redirigir
        } else {
            alert(data.error); // Mostrar mensaje de error
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


