"use client";

import { useEffect, useState } from "react";
import "./hero.css";
import FilterAside, {
  FULL_FILTERS,
  type FilterValues,
} from "../components/FilterAside";
import GameCard from "../components/GameCard";
import Pagination from "../components/Pagination";
import Fab from "../components/Fab";
import { getGames } from "../lib/api";
import { Game } from "../interfaces";

interface serverRes {
  success: boolean;
  games: Game[];
  currentPage: number;
  totalPages: number;
}

export default function MainPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(10);
  const [filters, setFilters] = useState<FilterValues | null>(null);

  useEffect(() => {
    const data = {
      page: page,
      ...(filters ? { filters } : {}),
    };
    getGames(data).then((res: serverRes) => {
      console.log(res);

      setGames(res?.games ?? []);
      setPage(res?.currentPage ?? 1);
      setTotalPages(res?.totalPages ?? 1);
    });
  }, [page, filters]);

  const handleFiltersSave = (values: FilterValues) => {
    setFilters(values);
  };

  return (
    <main className="page">
      <section className="hero">
        <img className="hero__bg" src="/assets/hero.png" alt="" />
        <div className="hero__overlay" />
        <div className="hero__content">
          <h1 className="hero__title">
            Discover <span className="hero__title-underline">Your</span> Next
            <br />
            <span className="hero__title-accent">Epic Adventure</span>
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
          <FilterAside onSave={handleFiltersSave} filterConfig={FULL_FILTERS} />
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
