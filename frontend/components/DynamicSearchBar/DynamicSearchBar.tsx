"use client";
import "./DynamicSearchBar.css";
import { getSearchResults } from "@/lib/api";
import { useRef, useState } from "react";
import { SearchBarGame } from "@/interfaces/api";

function DynamicSearchBar() {
  const [games, setGames] = useState<SearchBarGame[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  const inputHandler = (inputValue: string) => {
    if (inputValue.trim() == "") return;

    getSearchResults(inputValue)
      .then((res) => {
        if (res.length > 0) {
          console.log(res);

          setGames(res);
          setErrorMessage(null);
        }
      })
      .catch((error) => {
        console.log(error.status, error.message); // e.g. 404 "Not found"
        setErrorMessage("Nie znaleziono gier.");
      });
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.currentTarget.value;
    clearTimeout(timer.current);
    timer.current = setTimeout(() => inputHandler(value), 1000);
  };

  return (
    <div className="DynamicSearchBar">
      <button className="DynamicSearchBar__button">
        <img className="DynamicSearchBar__searchSVG" src="/assets/search.svg" alt="" />
      </button>
      <div className="DynamicSearchBar__inputSection">
        <input type="text" placeholder="Nazwa gry" onChange={onInputChange} />
        {!errorMessage ? (
          <div className="DynamicSearchBar__games">
            {games.map((game) => (
              <div className="DynamicSearchBar__game" key={game.appid}>
                <img
                  className="DynamicSearchBar__gameImage"
                  src={game.capsule_image}
                  alt={game.name}
                />{" "}
                <div className="DynamicSearchBar__gameName">{game.name}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="DynamicSearchBar__errorMessage">{errorMessage}</div>
        )}
      </div>
    </div>
  );
}

export default DynamicSearchBar;
