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
    cache: "no-store",
  });

  console.log(JSON.stringify(body));

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

export const getGames = (data: GetGames): Promise<GamesRes> =>
  post<GamesRes>("/api/get_steam_games", data);

export const sendMessage = (data: unknown): Promise<MessageResponse> =>
  post<MessageResponse>("/api/message", data);

export const createUser = (data: CreateUserData) => post("/api/create_user", data);

export const getSearchResults = (filter: string): Promise<SearchBarGame[]> =>
  get<SearchBarGame[]>(`/api/games_search_bar?${new URLSearchParams({ filter })}`);

export const loadAtributeListForFilter = async (
  path: string,
  itemName: string,
): Promise<string[]> => {
  const cached = window.localStorage.getItem(itemName);
  console.log(cached);
  if (cached) {
    const parsed = JSON.parse(cached);
    if (Array.isArray(parsed) && parsed.length) return parsed.filter(Boolean);
  }

  const atributesList = await get<string[]>(path);
  window.localStorage.setItem(itemName, JSON.stringify(atributesList));
  console.log(atributesList);
  return atributesList;
};
