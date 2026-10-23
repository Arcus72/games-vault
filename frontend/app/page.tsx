"use client";

import { useEffect, useState } from "react";
import "./gallery.scss";
import FilterAside from "../components/FilterAside/FilterAside";
import GameCard from "../components/GameCard/GameCard";
import Pagination from "../components/Pagination/Pagination";
import Fab from "../components/Fab/Fab";
import { getGames } from "../lib/api";
import type { Game } from "../interfaces/main";
import { FilterValues } from "../interfaces/main";

import { useAuth } from "@/context/AuthContext";
import { showMessage } from "@/components/Message/Message";

export default function MainPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(10);
  const [filters, setFilters] = useState<FilterValues | null>(null);
  const { isLogged } = useAuth();

  useEffect(() => {
    const filterData = { page: page, ...filters };

    getGames(filterData)
      .then((res) => {
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
  }, [page, filters]);

  return (
    <main className="page">
      <section className="Gallery">
        <img className="Gallery__bg" src="/assets/hero.png" alt="" />
        <div className="Gallery__overlay" />
        <div className="Gallery__content">
          <h1 className="Gallery__title">
            Odkryj <span className="Gallery__titleUnderline">Swoją</span> Następną
            <br />
            <span className="Gallery__titleAccent">Epicką Przygodę</span>
          </h1>
          <p className="Gallery__text">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis neque dui, aliquet ac nibh
            id, aliquet suscipit felis. Curabitur eleifend purus quam, non congue lorem rutrum a.
            Sed dictum nunc ligula, et dignissim diam bibendum ac. Nullam ut sapien non massa
            molestie porta a nec quam. Pellentesque gravida urna non ex efficitur,
          </p>
        </div>
      </section>
      <div className="Gallery__strip" />
      <div className="layout">
        <div className="layout__sidebar">
          <FilterAside onSave={setFilters} />
        </div>
        <section className="layout__content">
          {games.length == 0 ? (
            <div className="Gallery__noGameFound">Nie znaleziono gier</div>
          ) : (
            <div className="grid">
              {games.map((g) => (
                <GameCard key={g.appid} game={g} visibleBadges={isLogged() ? [1, 2] : []} />
              ))}
            </div>
          )}
          <Pagination currentPage={page} setPage={setPage} totalPages={totalPages} />
        </section>
      </div>
      {isLogged() && <Fab />}
    </main>
  );
}
