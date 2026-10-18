import { ChatGame, Game, FilterValues } from "./main";

export interface MessageResponse {
  success: boolean;
  response: string;
  games: ChatGame[];
}

export interface GamesResponse {
  games: Game[];
  page: number;
  pages: number;
}

export interface CreateUserData {
  username: string;
  email: string;
  phone: string;
  password: string;
}

export interface LoginData {
  username_or_email: string;
  password: string;
}

export interface SearchBarGameResponse {
  appid: number;
  name: string;
  capsule_image: string;
}

export interface GetGames {
  page: number;
  filters: FilterValues | null;
}

export interface SimpleMessage {
  message: string;
}
