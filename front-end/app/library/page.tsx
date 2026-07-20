"use client";

import { useEffect, useState } from "react";
import "./view-toggle.css";
import FilterAside, {
  FULL_FILTERS,
  type FilterValues,
} from "../../components/FilterAside";
import GameCard from "../../components/GameCard";
import Pagination from "../../components/Pagination";
import Fab from "../../components/Fab";
import { getGames } from "../../lib/api";
import type { Game } from "../../interfaces";

const views = [
  { id: "all", label: "All" },
  { id: "wishlist", label: "Wish-list", icon: "/assets/toggle-wishlist.svg" },
  { id: "hidden", label: "Hidden", icon: "/assets/toggle-hidden.svg" },
] as const;

type View = (typeof views)[number]["id"];

interface serverRes {
  success: boolean;
  games: Game[];
  currentPage: number;
  totalPages: number;
}

export default function LibraryPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [view, setView] = useState<View>("all");
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(10);

  useEffect(() => {
    const pagination = {
      currentPage: page,
      totalPages: totalPages,
    };
    getGames({ type: view, pagination: pagination }).then((res: serverRes) => {
      setGames(res?.games ?? []);
      setPage(res?.currentPage ?? 1);
      setTotalPages(res?.totalPages ?? 1);
    });
  }, [page, view]);

  const handleFiltersSave = (values: FilterValues) => {
    const data = {
      page: page,
      filters: values,
    };
    getGames(data).then((res: serverRes) => setGames(res?.games ?? []));
  };

  return (
    <main className="page">
      <div className="layout layout--library">
        <div className="layout__sidebar">
          <section className="view-toggle">
            <h2 className="view-toggle__title">View</h2>
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
          <FilterAside filterConfig={FULL_FILTERS} onSave={handleFiltersSave} />
        </div>
        <section className="layout__content">
          <div className="sort-bar">
            <img
              className="sort-bar__img"
              src="/assets/sort-by.png"
              alt="Sort by: Relevance"
            />
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
