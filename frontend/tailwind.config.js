/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0F0E17",
        foreground: "#FFFFFE",
        card: "#1A1A2E",
        accent: "#7C3AED",
        muted: "#94A3B8",
        border: "#2D2D44",
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
