import Gun from 'gun/gun'

export default defineNuxtPlugin(() => {
  return {
    provide: {
      Gun: Gun()
    }
  }
})
