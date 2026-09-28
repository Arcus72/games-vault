import type {
  GamesRes,
  MessageResponse,
  CreateUserData,
  SearchBarGame,
  GetGames,
} from "../interfaces/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
    cache: "no-store",
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const message =
      (data && typeof data === "object" && "detail" in data
        ? (data as { detail?: string }).detail
        : null) ?? `Request failed with status ${res.status}`;
    throw Object.assign(new Error(message), { status: res.status });
  }

  return data as T;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "GET",
    cache: "no-store",
    credentials: "include",
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const message =
      (data && typeof data === "object" && "detail" in data
        ? (data as { detail?: string }).detail
        : null) ?? `Request failed with status ${res.status}`;
    throw Object.assign(new Error(message), { status: res.status });
  }

  return data as T;
}

async function del<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "DELETE",
    credentials: "include",
    cache: "no-store",
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const message =
      (data && typeof data === "object" && "detail" in data
        ? (data as { detail?: string }).detail
        : null) ?? `Request failed with status ${res.status}`;
    throw Object.assign(new Error(message), { status: res.status });
  }

  return data as T;
}

interface SimpleMessage {
  message: string;
}

export const getUserGames = (data: GetGames): Promise<GamesRes> =>
  post<GamesRes>("/api/get_steam_games", data);

export const getGames = (data: GetGames): Promise<GamesRes> =>
  post<GamesRes>("/api/get_steam_games", data);

export const sendMessage = (data: unknown): Promise<MessageResponse> =>
  post<MessageResponse>("/api/message", data);

export const createUser = (data: CreateUserData) =>
  post<{ message: string }>("/api/create_user", data);

export const logoutUser = () => del<SimpleMessage>("/api/logout");

export const loginUser = (data: { username_or_email: string; password: string }) =>
  post<{ message: string; user_id: string }>("/api/login", data);

export const getSearchResults = (filter: string): Promise<SearchBarGame[]> =>
  get<SearchBarGame[]>(`/api/games_search_bar?${new URLSearchParams({ filter })}`);

export const loadAtributeListForFilter = async (
  path: string,
  itemName: string,
): Promise<string[]> => {
  const cached = window.localStorage.getItem(itemName);
  if (cached) {
    const parsed = JSON.parse(cached);
    if (Array.isArray(parsed) && parsed.length) return parsed.filter(Boolean);
  }

  const atributesList = await get<string[]>(path);
  window.localStorage.setItem(itemName, JSON.stringify(atributesList));

  return atributesList;
};

export const hideGame = (app_id: number): Promise<SimpleMessage> =>
  post<SimpleMessage>("/api/hide_game", app_id);

export const addGameToWishlist = (app_id: number): Promise<SimpleMessage> =>
  post<SimpleMessage>("/api/add_game_to_wishlist", app_id);

export const addGameToLibrary = (app_id: number): Promise<SimpleMessage> =>
  post<SimpleMessage>("/api/add_game_to_library", app_id);
