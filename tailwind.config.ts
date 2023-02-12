const plugin = require('tailwindcss/plugin')

module.exports = {
  theme: {
    colors: {
      primary: {
        light: '#CBF6FF',
        DEFAULT: '#9DEDFF',
        dark: '#006980',
      },
      secondary: {
        light: '#FFE5DF',
        DEFAULT: '#FFAF9D',
        dark: '#851800',
      },
      'accent-1': {
        light: '#E0FFD1',
        DEFAULT: '#BCFF9D',
        dark: '#2B8600',
      },
      'accent-2': {
        light: '#F4DDFF',
        DEFAULT: '#E09DFF',
        dark: '#590082',
      },
    },
    fontFamily: {
      sans: ['Roboto', 'sans-serif'],
    },
  },
  plugins: [
    plugin(function({ addBase, theme }: { addBase: (...args: any) => void, theme: (...args: any) => void }) {
      addBase({
        'h1': { fontSize: theme('fontSize.2xl') },
        'h2': { fontSize: theme('fontSize.xl') },
        'h3': { fontSize: theme('fontSize.lg') },
        'p': {
          fontSize: theme('fontSize.sm'),
          fontWeight: theme('fontWeight.light'),
        },
      })
    }),
    require('@tailwindcss/line-clamp'),
  ]
}