export type FilterSection =
  | { type: "search"; name: string; placeholder?: string }
  | {
      type: "slider";
      label: string;
      name: string;
      value: number | null;
      steps: { label: string; value: number | null }[];
      open?: boolean;
    }
  | {
      type: "range";
      label: string;
      name: string;
      startName: string;
      endName: string;
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
    }
  | {
      type: "select";
      label: string;
      name: string;
      options: { label: string; value: SortValue }[];
      open?: boolean;
    };

export interface Game {
  appid: number;
  name: string;
  price: number;
  header_image: string;
  status: number; // 0 -> Brak 1 -> Wishlist 2 -> Library 3 -> Library_Hidden
  steam_url?: string;
}

export interface AuthUser {
  username: string;
  email: string;
  steam_id: string;
}

export interface ChatGame {
  appid: number;
  title: string;
  price: number;
  status: number;
  imgUrl: string;
}

export type SortValue = { sort_by: string; ascending: number };

export type FilterValues = Record<string, string | number | string[] | SortValue | null>;

export interface FilterData {
  name: string | null;
  genres: string[] | null;
  price_max: number | null;
  release_date_min_year: number | null;
  release_date_max_year: number | null;
  tags: string[] | null;
  languages: string[] | null;
}
