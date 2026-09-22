const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function request(path, options = {}) {
  if (!API_BASE_URL) {
    throw new Error('API_NOT_CONFIGURED')
  }

  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) throw new Error(`API_ERROR_${response.status}`)
  return response.json()
}

export function analyzeSoil(image) {
  const body = new FormData()
  body.append('image', image)
  return request('/soil/analyze', { method: 'POST', body })
}

export function recommendCrop(data) {
  const payload = {
    district: data.location?.district,
    mandal: data.location?.mandal,
    season: data.farmer?.season || 'Kharif',
  }

  return request('/recommendation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function getWeather(latitude, longitude) {
  return request(
    `/weather?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`
  )
}
