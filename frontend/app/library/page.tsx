"use client";

import { useEffect, useState } from "react";
import "./view-toggle.css";
import FilterAside, {
  FULL_FILTERS,
} from "../../components/FilterAside/FilterAside";
import GameCard from "../../components/GameCard/GameCard";
import Pagination from "../../components/Pagination/Pagination";
import Fab from "../../components/Fab/Fab";
import { getGames } from "../../lib/api";
import type { Game } from "../../interfaces";

const views = [
  { id: "all", label: "Wszystkie" },
  {
    id: "wishlist",
    label: "Lista życzeń",
    icon: "/assets/toggle-wishlist.svg",
  },
  { id: "hidden", label: "Ukryte", icon: "/assets/toggle-hidden.svg" },
] as const;

export default function LibraryPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [view, setView] = useState<(typeof views)[number]["id"]>("all");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(10);

  useEffect(() => {
    getGames({
      type: view,
      pagination: { currentPage: page, totalPages },
    }).then((res) => {
      setGames(res?.games ?? []);
      setPage(res?.currentPage ?? 1);
      setTotalPages(res?.totalPages ?? 1);
    });
    // ponytail: totalPages is sent, not read back into the deps — it would re-fire the fetch on every response.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, view]);

  return (
    <main className="page">
      <div className="layout layout--library">
        <div className="layout__sidebar">
          <section className="view-toggle">
            <h2 className="view-toggle__title">Widok</h2>
            <div className="view-toggle__group">
              {views.map((v) => (
                <button
                  key={v.id}
                  className={`view-toggle__btn${view === v.id ? " view-toggle__btn--active" : ""}`}
                  onClick={() => setView(v.id)}
                >
                  {"icon" in v && (
                    <img className="view-toggle__icon" src={v.icon} alt="" />
                  )}
                  {v.label}
                </button>
              ))}
            </div>
          </section>
          <FilterAside
            filterConfig={FULL_FILTERS}
            onSave={(filters) =>
              getGames({ page, filters }).then((res) =>
                setGames(res?.games ?? []),
              )
            }
          />
        </div>
        <section className="layout__content">
          <div className="sort-bar">
            sortuj według:{" "}
            <select>
              <option value="">Trafność</option>
              <option value="">Data wydania</option>
              <option value="">Nazwa</option>
              <option value="">Najniższa cena</option>
              <option value="">Najwyższa cena</option>
            </select>
          </div>
          <div className="grid">
            {games.map((g) => (
              <GameCard
                key={g.id}
                game={g}
                stars={g.hidden}
                dimmed={g.hidden}
              />
            ))}
          </div>
          <Pagination
            currentPage={page}
            setPage={setPage}
            totalPages={totalPages}
          />
        </section>
      </div>
      <Fab />
    </main>
  );
}
