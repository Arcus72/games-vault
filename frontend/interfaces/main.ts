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
    };

export interface Game {
  appid: number | string;
  name: string;
  price: number;
  header_image: string;
  isHidden: boolean | null;
  library_wishlist: boolean | null;
  release_date: string | null;
  steam_url?: string;
}

export interface ChatGame {
  appid: string;
  title: string;
  price: number;
  currency: string;
  isWishList: boolean;
  imgUrl: string;
  steamUrl: string;
}

export type FilterValues = Record<string, string | number | string[] | null>;

export interface FilterData {
  name: string | null;
  genres: string[] | null;
  price_max: number | null;
  release_date_min_year: number | null;
  release_date_max_year: number | null;
  tags: string[] | null;
  languages: string[] | null;
}
