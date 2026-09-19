"use client";

import { useEffect, useState } from "react";
import "./hero.css";
import FilterAside, {
  FULL_FILTERS,
  type FilterValues,
} from "../components/FilterAside/FilterAside";
import GameCard from "../components/GameCard/GameCard";
import Pagination from "../components/Pagination/Pagination";
import Fab from "../components/Fab/Fab";
import { getGames } from "../lib/api";
import type { Game } from "../interfaces";

export default function MainPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(10);
  const [filters, setFilters] = useState<FilterValues | null>(null);

  useEffect(() => {
    getGames({ page, ...(filters && { filters }) }).then((res) => {
      setGames(res?.games ?? []);
      setPage(res?.currentPage ?? 1);
      setTotalPages(res?.totalPages ?? 1);
    });
  }, [page, filters]);

  return (
    <main className="page">
      <section className="hero">
        <img className="hero__bg" src="/assets/hero.png" alt="" />
        <div className="hero__overlay" />
        <div className="hero__content">
          <h1 className="hero__title">
            Odkryj <span className="hero__title-underline">Swoją</span> Następną
            <br />
            <span className="hero__title-accent">Epicką Przygodę</span>
          </h1>
          <p className="hero__text">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis neque
            dui, aliquet ac nibh id, aliquet suscipit felis. Curabitur eleifend
            purus quam, non congue lorem rutrum a. Sed dictum nunc ligula, et
            dignissim diam bibendum ac. Nullam ut sapien non massa molestie
            porta a nec quam. Pellentesque gravida urna non ex efficitur,
          </p>
        </div>
      </section>
      <div className="hero__strip" />

      <div className="layout">
        <div className="layout__sidebar">
          <FilterAside onSave={setFilters} filterConfig={FULL_FILTERS} />
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
              <GameCard key={g.id} game={g} />
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

//TODO: Extra search bar on top for dynamic search
//TODO: Wszyskie -> moje gry
//TODO: Platformy jako filtry
//TODO: sortowanie na lewo do filtrów
