import { ClientPageRoot } from "next/dist/client/components/client-page";
import type {
  GamesResponse,
  MessageResponse,
  CreateUserData,
  SearchBarGameResponse,
  GetGames,
  SimpleMessage,
  LoginData,
  GetUserGames,
  StatusChangeResponse,
  NewPasswordData,
} from "../interfaces/api";
import { AuthUser } from "../interfaces/main";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  console.log(body);

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

export const getUserGames = (data: GetUserGames): Promise<GamesResponse> =>
  post<GamesResponse>("/api/get_user_library", data);

export const getGames = (data: GetGames): Promise<GamesResponse> =>
  post<GamesResponse>("/api/get_steam_games", data);

export const sendMessage = (data: unknown): Promise<MessageResponse> =>
  post<MessageResponse>("/api/message", data);

export const createUser = (data: CreateUserData) => post<SimpleMessage>("/api/create_user", data);

export const updatePassword = (data: NewPasswordData) =>
  post<SimpleMessage>("/api/change_password", data);

export const updateSteamId = (newSteamID: string) =>
  post<SimpleMessage>("/api/add_steam_id", { steam_id: newSteamID });

export const loadSteamLibrary = (): Promise<SimpleMessage> =>
  post<SimpleMessage>("/api/add_games_from_steam", {});

export const logoutUser = () => del<SimpleMessage>("/api/logout");

export const loginUser = async (data: LoginData): Promise<AuthUser> => {
  await post<SimpleMessage>("/api/login", data);
  return await get<AuthUser>("/api/get_user_info");
};

export const getSearchResults = (filter: string): Promise<SearchBarGameResponse[]> =>
  get<SearchBarGameResponse[]>(`/api/games_search_bar?${new URLSearchParams({ filter })}`);

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

export const toggleGameStatus = (
  app_id: number,
  statusToToggle: "wishlist" | "library" | "hidden",
) => {
  const apiMap = {
    wishlist: "/api/toggle_wishlist_game",
    hidden: "/api/toggle_hide_game",
    library: "/api/toggle_library_game",
  };

  return post<StatusChangeResponse>(apiMap[statusToToggle], app_id);
};
