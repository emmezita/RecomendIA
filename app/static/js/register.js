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
