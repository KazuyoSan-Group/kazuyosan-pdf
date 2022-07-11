/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./public/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        transparent: 'transparent',
        'forest': '#04202c',
        'evergreen': '#304040',
        'pine': '#5b7065',
        'fog': '#c9d1c8',
      }
    },
  },
  plugins: [],
}
