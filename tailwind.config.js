/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.{html,css,js}"],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

