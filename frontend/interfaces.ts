export type FilterSection =
  | { type: "search"; name: string; placeholder?: string }
  | {
      type: "slider";
      label: string;
      name: string;
      value: string;
      steps?: string[];
      open?: boolean;
    }
  | {
      type: "range";
      label: string;
      name: string;
      startLabel?: string;
      endLabel?: string;
      open?: boolean;
    }
  | {
      type: "checkboxes";
      label: string;
      name: string;
      options: string[];
      checked?: string[];
      open?: boolean;
    };

export interface Game {
  appid: number | string;
  name: string;
  price: number;
  header_image: string;
  isHidden: boolean | null;
  library_wishlist: boolean | null;
  release_date: string | null;
}

export interface GamesRes {
  games: Game[];
  page: number;
  pages: number;
}

export interface ChatGame {
  id: string;
  title: string;
  price: number;
  currency: string;
  isWishList: boolean;
  imgUrl: string;
  steamUrl: string;
}

export interface MessageResponse {
  success: boolean;
  response: string;
  games: ChatGame[];
}
