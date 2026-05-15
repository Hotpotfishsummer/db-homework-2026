export function useHaptics() {
  const trigger = (type = 'light') => {
    if ('vibrate' in navigator) {
      const patterns = {
        light: [10],
        medium: [20],
        heavy: [30],
        success: [10, 50, 20],
        error: [50, 30, 50]
      }
      navigator.vibrate(patterns[type] || patterns.light)
    }
  }

  return { trigger }
}