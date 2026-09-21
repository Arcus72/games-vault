import type { GamesRes, MessageResponse } from "../interfaces";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    return res.ok ? ((await res.json()) as T) : fallback;
  } catch {
    return fallback;
  }
}

export const getGames = (data: unknown) =>
  post<GamesRes | null>("/api/get_steam_games", data, null);

export const sendMessage = (data: unknown) =>
  post<MessageResponse | null>("/api/message", data, null);
