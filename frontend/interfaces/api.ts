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

export interface NewPasswordData {
  old_password: string;
  new_password: string;
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

export interface GetGames extends FilterValues {
  page: number;
}

export interface GetUserGames extends GetGames {
  status: number;
}

export interface SimpleMessage {
  message: string;
}

export interface StatusChangeResponse {
  status: number;
  message: string;
}
