"use client";
import type { Game } from "../../interfaces/main";
import type { StatusChangeResponse } from "../../interfaces/api";
import { useState } from "react";
import { toggleGameStatus } from "@/lib/api";
import "./GameCard.scss";
import { showMessage } from "../Message/Message";
type GameStatus = "hidden" | "wishlist" | "library" | null;

interface Badge {
  id: number;
  status: Exclude<GameStatus, null>;
  icon: string;
  alt: string;
}

const BADGES: Badge[] = [
  { id: 1, status: "wishlist", icon: "/assets/icon-wishlist.svg", alt: "Lista życzeń" },
  { id: 2, status: "library", icon: "/assets/icon-plus.svg", alt: "Dodaj" },
  { id: 3, status: "hidden", icon: "/assets/icon-hidden.svg", alt: "Ukryte" },
];

interface Props {
  game: Game;
  visibleBadges?: number[];
  showOnlyStatsu?: null | 1 | 2 | 3;
}

export default function GameCard({
  game,
  visibleBadges = [1, 2, 3],
  showOnlyStatsu = null,
}: Props) {
  const [gameStatus, setGameStatus] = useState<number>(game.status);
  const [isStatusEditable, setIsStatusEditable] = useState<boolean>(true);

  const sliderIndex = BADGES.findIndex((b) => b.id === gameStatus);

  const changeGameStatus = (app_id: number, sourceBtn: "library" | "wishlist" | "hidden") => {
    if (!isStatusEditable) return;

    setIsStatusEditable(false);
    toggleGameStatus(app_id, sourceBtn)
      .then((res: StatusChangeResponse) => {
        console.log(res);

        setGameStatus(res.status);
        showMessage(res.message);
      })
      .catch((error) => {
        showMessage(error.message, "error");
      })
      .finally(() => {
        setIsStatusEditable(true);
      });
  };

  if (showOnlyStatsu && showOnlyStatsu !== gameStatus) return null;

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
      {game.price && <span className="GameCard__price">{game.price.toFixed(2)} zł</span>}
      {visibleBadges && (
        <div className={`GameCard__badges ${sliderIndex >= 0 ? "GameCard__badges--show" : ""}`}>
          <span
            className={`GameCard__badgeSlider ${sliderIndex >= 0 ? "GameCard__badgeSlider--show" : ""}`}
            style={{ "--i": Math.max(sliderIndex, 0) } as React.CSSProperties}
          />
          {BADGES.filter(({ id }) => visibleBadges.indexOf(id) != -1).map(
            ({ id, status, icon, alt }) => (
              <button
                key={id}
                type="button"
                className="GameCard__badge"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();

                  changeGameStatus(game.appid, status);
                }}
              >
                <img className="GameCard__badgeIcon" src={icon} alt={alt} />
              </button>
            ),
          )}
        </div>
      )}
    </a>
  );
}
