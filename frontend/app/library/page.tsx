"use client";

import { useEffect, useState } from "react";
import "./library.scss";
import FilterAside from "../../components/FilterAside/FilterAside";
import GameCard from "../../components/GameCard/GameCard";
import Pagination from "../../components/Pagination/Pagination";
import Fab from "../../components/Fab/Fab";
import { getUserGames } from "../../lib/api";
import type { Game } from "../../interfaces/main";
import { FilterValues } from "../../interfaces/main";
import { showMessage } from "@/components/Message/Message";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

const views = [
  { id: 2, label: "Moje gry" },
  {
    id: 1,
    label: "Lista życzeń",
    icon: "/assets/toggle-wishlist.svg",
  },
  { id: 3, label: "Ukryte", icon: "/assets/toggle-hidden.svg" },
] as const;

export default function LibraryPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [gameStatus, setGameStatus] = useState<1 | 2 | 3>(2);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(10);
  const [filters, setFilters] = useState<FilterValues | null>(null);
  const { isLogged } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLogged()) {
      router.push("/");
    }
  }, []);

  useEffect(() => {
    const filterData = { page: page, ...filters, status: gameStatus };

    getUserGames(filterData)
      .then((res) => {
        console.log(res);

        setGames(res?.games ?? []);
        setPage(res?.page ?? 1);
        setTotalPages(res?.pages ?? 1);
      })
      .catch((error) => {
        showMessage(error.message, "error");
        setGames([]);
        setPage(1);
        setTotalPages(1);
      });
  }, [page, gameStatus, filters]);

  return (
    <main className="page">
      <div className="layout layout--library">
        <div className="layout__sidebar">
          <section className="Library">
            <h2 className="Library__title">Widok</h2>
            <div className="Library__group">
              {views.map((v) => (
                <button
                  key={v.id}
                  className={`Library__btn${gameStatus === v.id ? " Library__btn--active" : ""}`}
                  onClick={() => setGameStatus(v.id)}
                >
                  {"icon" in v && <img className="Library__icon" src={v.icon} alt="" />}
                  {v.label}
                </button>
              ))}
            </div>
          </section>
          <FilterAside onSave={setFilters} />
        </div>
        <section className="layout__content">
          {games.length == 0 ? (
            <div className="Library__noGameFound">Żadna gra nie została jeszcze dodana</div>
          ) : (
            <div className="grid">
              {games.map((g) => (
                <GameCard
                  key={g.appid}
                  game={g}
                  visibleBadges={[1, 2, 3]}
                  showOnlyStatsu={gameStatus}
                />
              ))}
            </div>
          )}
          <Pagination currentPage={page} setPage={setPage} totalPages={totalPages} />
        </section>
      </div>
      <Fab />
    </main>
  );
}
