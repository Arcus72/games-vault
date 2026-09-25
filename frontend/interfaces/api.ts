import { ChatGame, Game, FilterValues } from "./main";

export interface MessageResponse {
  success: boolean;
  response: string;
  games: ChatGame[];
}

export interface GamesRes {
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

export interface SearchBarGame {
  appid: number;
  name: string;
  capsule_image: string;
}

export interface GetGames {
  page: number;
  filters: FilterValues | null;
}
