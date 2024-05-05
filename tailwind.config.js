/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.{html,css,js}"],
  theme: {
    fontFamily: {
      poppins: ["Poppins", "sans-serif"],
      hind: ["Hind", "sans-serif"],
    },
    extend: {
      colors: {
        "rojo-oscuro": "#8C2E2E",
        "rojo-medio": "#B51F1F",
        "rojo-claro": "#E00000",
        light: "#E0C9C9",
        dark: "#1B1E2F",
        "dark-2": "#232538",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("daisyui")
],
};