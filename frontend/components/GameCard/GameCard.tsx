"use client";
import type { Game } from "../../interfaces/main";
import { useState } from "react";
import { addGameToLibrary } from "@/lib/api";
import "./GameCard.scss";
import { showMessage } from "../Message/Message";
type GameStatus = "hidden" | "wishlist" | "library" | null;

// const getGameSatus = (game: Game): GameStatus => {
//   console.log(game.name, game.isHidden, game.library_wishlist);
//   return null;
// };

const BADGES: { status: Exclude<GameStatus, null>; icon: string; alt: string }[] = [
  // { status: "hidden", icon: "/assets/icon-hidden.svg", alt: "Ukryte" },
  // { status: "wishlist", icon: "/assets/icon-wishlist.svg", alt: "Lista życzeń" },
  { status: "library", icon: "/assets/icon-plus.svg", alt: "Dodaj" },
];

interface Props {
  game: Game;
  isBadgesVisible?: boolean;
}

export default function GameCard({ game, isBadgesVisible = false }: Props) {
  const [isInLibrary, setIsInLibrary] = useState<boolean>((game.library_wishlist || 0) == 1);

  const changeGameStatus = () => {
    if (game.appid) {
      addGameToLibrary(game.appid)
        .then((res) => {
          setIsInLibrary(true);
          showMessage(res.message);
        })
        .catch((error) => {
          showMessage(error.message, "error");
        });
    }
  };

  return (
    <a
      className="GameCard"
      href={`https://store.steampowered.com/agecheck/app/${game.appid}/`}
      target="_blank"
      rel="noopener noreferrer"
    >
      <img className="GameCard__cover" src={game.header_image} alt={game.name} />
      <div />
      <div className="GameCard__namePlate">
        <span className="GameCard__nameBar" />
        <span className="GameCard__name">{game.name}</span>
      </div>
      {game.price && <span className="GameCard__price">{game.price}</span>}
      {isBadgesVisible && (
        <div className={`GameCard__badges ${isInLibrary && "GameCard__badges--show"}`}>
          {/* {gameStat != null && (
          <span
            className="GameCard__badgeSlider"
            style={{ "--i": BADGES.findIndex((b) => b.status === gameStat) } as React.CSSProperties}
          />
        )} */}
          {BADGES.map(({ status, icon, alt }) => (
            <button
              key={status}
              type="button"
              className={`GameCard__badge ${isInLibrary && "GameCard__badge--show"}`}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();

                changeGameStatus();
              }}
            >
              <img className="GameCard__badgeIcon" src={icon} alt={alt} />
            </button>
          ))}
        </div>
      )}
    </a>
  );
}
