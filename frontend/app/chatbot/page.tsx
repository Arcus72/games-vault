"use client";

import { useState } from "react";
import "./chat.scss";
import FilterAside from "@/components/FilterAside/FilterAside";
import { FilterValues } from "../../interfaces/main";
import GameCard from "../../components/GameCard/GameCard";
import { sendMessage } from "../../lib/api";
import type { ChatGame, Game } from "../../interfaces/main";

const SUGGESTIONS = Array(4).fill("Znajdź nową grę na podstawie mojej biblioteki");

/** /api/message returns a different game shape than the grid — adapt it for GameCard. */
function toGame(g: ChatGame): Game {
  return {
    appid: g.appid,
    name: g.title,
    price: g.price,
    header_image: g.imgUrl,
    steam_url: g.steamUrl,
    library_wishlist: null,
    release_date: null,
    isHidden: false,
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

    const res = await sendMessage({ filters: filterValues, question: text });
    setTyping(false);

    if (!res?.success) {
      setMessages((m) => [
        ...m,
        {
          from: "bot",
          text: "Przepraszamy, coś poszło nie tak. Spróbuj ponownie.",
        },
      ]);
      return;
    }
    setMessages((m) => [
      ...m,
      { from: "bot", text: res.response },
      ...(res.games.length ? [{ from: "bot" as const, games: res.games.map(toGame) }] : []),
    ]);
  };

  return (
    <main className="Chat">
      {filtersOpen && (
        <div className="Chat__aside">
          <FilterAside onChange={setFilterValues} />
        </div>
      )}
      <div className="Chat__main">
        <div className="Chat__glow" />
        {messages.length === 0 ? (
          <div className="Chat__empty">
            <div className="Chat__emptyChest">
              <img className="Chat__emptyChestImg" src="/assets/chest-big.svg" alt="" />
            </div>
            <h1 className="Chat__emptyTitle">Twój asystent gier</h1>
            <p className="Chat__emptySub">
              Zapytaj mnie o cokolwiek z Twojej biblioteki — pomogę Ci znaleźć następną przygodę,
              śledzić osiągnięcia lub odkryć ukryte perełki
            </p>
            <div className="Chat__tryAsking">
              <header className="Chat__tryAskingHeader">
                <img className="Chat__tryAskingSparkle" src="/assets/sparkle.svg" alt="" />
                <span>SPRÓBUJ ZAPYTAĆ</span>
              </header>
              {SUGGESTIONS.map((s, i) => (
                <button className="Chat__tryAskingItem" key={i} onClick={() => send(s)}>
                  <span className="Chat__tryAskingIcon">
                    <img className="Chat__tryAskingIconImg" src="/assets/gamepad.svg" alt="" />
                  </span>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="Chat__window">
            {messages.map((m, i) =>
              m.games ? (
                <div className="Chat__windowGames" key={i}>
                  {m.games.map((g) => (
                    <GameCard key={g.appid} game={g} />
                  ))}
                </div>
              ) : (
                <div key={i} className={`Chat__bubble Chat__bubble--${m.from}`}>
                  {m.text}
                </div>
              ),
            )}
            {typing && (
              <div className="Chat__bubble Chat__bubble--typing">
                <span className="Chat__bubbleDot" />
                <span className="Chat__bubbleDot" />
                <span className="Chat__bubbleDot" />
              </div>
            )}
          </div>
        )}
        <form
          className="Chat__input"
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
        >
          <button
            type="button"
            className="Chat__inputCategory"
            onClick={() => setFiltersOpen((o) => !o)}
            aria-label="Przełącz filtry"
          >
            <img className="Chat__inputCategoryImg" src="/assets/category.svg" alt="" />
            {filtersOpen && <span className="Chat__inputCount">4</span>}
          </button>
          <input
            className="Chat__inputField"
            placeholder="Napisz wiadomość..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="Chat__inputSend" aria-label="Wyślij">
            <img className="Chat__inputSendImg" src="/assets/send.svg" alt="" />
          </button>
        </form>
      </div>
    </main>
  );
}
