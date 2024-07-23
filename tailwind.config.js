/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./ratatouille_app/templates/**/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms")],
};
