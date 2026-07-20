import type { MessageResponse } from '../interfaces'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:4000'

async function post<T>(path: string, body: unknown, fallback: T): Promise<T> {
  // ponytail: fallback keeps pages rendering when the back-end is down
  try {
    const res = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      cache: 'no-store',
    })
    if (!res.ok) return fallback
    return (await res.json()) as T
  } catch {
    return fallback
  }
}
//TODO: Fix sending
//TODO: Działanie filtru
export const getGames = (data: unknown) => post<any>('/api/games', data, [])

export const sendMessage = (data: unknown) => post<MessageResponse | null>('/api/message',  data , null)

export const getLibrary = ( data: unknown) => post<any>('/api/library',  data , null)