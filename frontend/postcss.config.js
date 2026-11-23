// Vite runs every CSS file through PostCSS: Tailwind expands the @tailwind directives,
// autoprefixer adds vendor prefixes for older browsers.
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
