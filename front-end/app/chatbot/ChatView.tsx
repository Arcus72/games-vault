"use client";

import { useState } from "react";
import "./chat.css";
import FilterAside, {
  FULL_FILTERS,
  type FilterValues,
} from "../../components/FilterAside";
import GameCard from "../../components/GameCard";
import { sendMessage } from "../../lib/api";
import type { ChatGame, Game } from "../../interfaces";

const SUGGESTIONS = Array(4).fill("Find you new game baseing on your library");

/** /api/message returns a different game shape than the grid — adapt it for GameCard. */
function toGame(g: ChatGame): Game {
  return {
    id: g.id,
    name: g.title,
    price: `${g.price.toFixed(2)} ${g.currency}`,
    imgUrl: g.imgUrl,
    steamUrl: g.steamUrl,
    rating: 0,
    wishlisted: g.isWishList,
    hidden: false,
  };
}

interface Message {
  from: "user" | "bot";
  text?: string;
  games?: Game[];
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filterValues, setFilterValues] = useState<FilterValues>({});

  const send = async (text: string) => {
    if (!text.trim() || typing) return;
    setMessages((m) => [...m, { from: "user", text }]);
    setInput("");
    setTyping(true);

    const filtersExtention = { filters: filterValues, question: text };
    const res = await sendMessage(filtersExtention);
    setTyping(false);

    if (!res?.success) {
      setMessages((m) => [
        ...m,
        { from: "bot", text: "Sorry, something went wrong. Please try again." },
      ]);
      return;
    }
    setMessages((m) => [
      ...m,
      { from: "bot", text: res.response },
      ...(res.games.length
        ? [{ from: "bot" as const, games: res.games.map(toGame) }]
        : []),
    ]);
  };

  const empty = messages.length === 0;

  return (
    <main className="chat">
      {filtersOpen && (
        <div className="chat__aside">
          <FilterAside filterConfig={FULL_FILTERS} onChange={setFilterValues} />
        </div>
      )}
      <div className="chat__main">
        <div className="chat__glow" />
        {empty ? (
          <div className="chat-empty">
            <div className="chat-empty__chest">
              <img
                className="chat-empty__chest-img"
                src="/assets/chest-big.svg"
                alt=""
              />
            </div>
            <h1 className="chat-empty__title">Your game assistant</h1>
            <p className="chat-empty__sub">
              Ask me anything about your library — I&apos;ll help you find your
              next adventure, track achievements, or discover hidden gems
            </p>
            <div className="try-asking">
              <header className="try-asking__header">
                <img
                  className="try-asking__sparkle"
                  src="/assets/sparkle.svg"
                  alt=""
                />
                <span>TRY ASKING</span>
              </header>
              {SUGGESTIONS.map((s, i) => (
                <button
                  className="try-asking__item"
                  key={i}
                  onClick={() => send(s)}
                >
                  <span className="try-asking__icon">
                    <img
                      className="try-asking__icon-img"
                      src="/assets/gamepad.svg"
                      alt=""
                    />
                  </span>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-window">
            {messages.map((m, i) =>
              m.games ? (
                <div className="chat-window__games" key={i}>
                  {m.games.map((g) => (
                    <GameCard key={g.id} game={g} />
                  ))}
                </div>
              ) : (
                <div key={i} className={`bubble bubble--${m.from}`}>
                  {m.text}
                </div>
              ),
            )}
            {typing && (
              <div className="bubble bubble--typing">
                <span className="bubble__dot" />
                <span className="bubble__dot" />
                <span className="bubble__dot" />
              </div>
            )}
          </div>
        )}
        <form
          className="chat-input"
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
        >
          <button
            type="button"
            className="chat-input__category"
            onClick={() => setFiltersOpen((o) => !o)}
            aria-label="Toggle filters"
          >
            <img
              className="chat-input__category-img"
              src="/assets/category.svg"
              alt=""
            />
            {filtersOpen && <span className="chat-input__count">4</span>}
          </button>
          <input
            className="chat-input__field"
            placeholder="Type message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="chat-input__send" aria-label="Send">
            <img
              className="chat-input__send-img"
              src="/assets/send.svg"
              alt=""
            />
          </button>
        </form>
      </div>
    </main>
  );
}
