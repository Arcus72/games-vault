import type { Game } from "../../interfaces/main";
import "./GameCard.css";

export default function GameCard({
  game,
  stars = false,
  dimmed = false,
}: {
  game: Game;
  stars?: boolean;
  /** Keep the dim overlay always on (hidden games); otherwise it shows on hover. */
  dimmed?: boolean;
}) {
  return (
    <a
      className="game-card"
      href={""}
      target="_blank"
      rel="noopener noreferrer"
    >
      <img
        className="game-card__cover"
        src={game.header_image}
        alt={game.name}
      />
      <div
        className={`game-card__dim${dimmed ? " game-card__dim--always" : ""}`}
      />
      <div className="game-card__name-plate">
        <span className="game-card__name-bar" />
        <span className="game-card__name">{game.name}</span>
      </div>
      <span className="game-card__price">{game.price}</span>
      <div className="game-card__badges">
        <span className="game-card__badge">
          <img
            className="game-card__badge-bg"
            src="/assets/badge-hidden.svg"
            alt=""
          />
          <img
            className="game-card__badge-icon"
            src="/assets/icon-hidden.svg"
            alt="Ukryte"
          />
        </span>
        <span className="game-card__badge">
          <img
            className="game-card__badge-bg"
            src="/assets/badge-wishlist.svg"
            alt=""
          />
          <img
            className="game-card__badge-icon"
            src="/assets/icon-wishlist.svg"
            alt="Lista życzeń"
          />
        </span>
      </div>
      {/* {stars && (
        <img
          className="game-card__stars"
          src="/assets/stars.svg"
          alt={`${game.rating} gwiazdek`}
        />
      )} */}
    </a>
  );
}
