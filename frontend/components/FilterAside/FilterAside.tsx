"use client";

import { useEffect, useState } from "react";
import "./FilterAside.css";
import { FilterSection, FilterValues } from "../../interfaces/main";
import Section from "./Section";
import { loadAtributeListForFilter } from "@/lib/api";

async function getConfig(): Promise<FilterSection[]> {
  const tags = await loadAtributeListForFilter("/api/get_tags", "gameTags");

  const platforms = await loadAtributeListForFilter("/api/get_platforms", "gamePlatforms");

  const genres = await loadAtributeListForFilter("/api/get_genres", "gameGenres");

  const languages = await loadAtributeListForFilter("/api/get_languages", "gamelanguages");

  return [
    { type: "search", name: "name" },
    {
      type: "slider",
      label: "zakres cen",
      name: "price_max",
      value: null,
      steps: [
        { label: "Za darmo", value: 0 },
        { label: "poniżej 5$", value: 5 },
        { label: "poniżej 10$", value: 10 },
        { label: "poniżej 20$", value: 20 },
        { label: "poniżej 50$", value: 50 },
        { label: "Bez limitu", value: null },
      ],
      open: true,
    },
    {
      type: "range",
      label: "Zakres lat",
      name: "yearSpan",
      startName: "release_date_min_year",
      endName: "release_date_max_year",
      open: true,
    },
    {
      type: "checkboxes",
      label: "Tagi",
      name: "tags",
      options: tags || [""],
      open: true,
    },
    {
      type: "checkboxes",
      label: "Języki",
      name: "languages",
      options: languages || [""],
    },
    {
      type: "checkboxes",
      label: "Platformy",
      name: "platforms",
      options: platforms || [""],
    },
    {
      type: "checkboxes",
      label: "Kategorie",
      name: "genres",
      options: genres || [""],
    },
  ];
}

function initialValues(filterConfig: FilterSection[]): FilterValues {
  const values: FilterValues = {};
  filterConfig.forEach((s) => {
    if (s.type === "search") values[s.name] = null;
    else if (s.type === "slider") values[s.name] = s.value;
    else if (s.type === "range") {
      values[s.startName] = null;
      values[s.endName] = null;
    } else {
      values[s.name] = s.checked?.length ? s.checked : null;
    }
  });
  return values;
}

export default function FilterAside({
  onSave,
  onChange,
}: {
  onSave?: (values: FilterValues) => void;
  onChange?: (values: FilterValues) => void;
}) {
  const [config, setConfig] = useState<FilterSection[]>([]);
  const [values, setValues] = useState<FilterValues>({});

  useEffect(() => {
    getConfig().then((c) => {
      setConfig(c);
      setValues(initialValues(c));
    });
  }, []);

  const set = (key: string, value: FilterValues[string]) => {
    const next = { ...values, [key]: value };
    setValues(next);
    onChange?.(next);
  };

  return (
    <aside className="filters">
      <h2 className="filters__title">Filtry:</h2>
      {config.map((s) => (
        <Section key={s.name} section={s} values={values} set={set} />
      ))}
      <div className="filters__buttons">
        <button className="filters__btn filters__btn--save" onClick={() => onSave?.(values)}>
          Zapisz
        </button>
        <button
          className="filters__btn filters__btn--reset"
          onClick={() => {
            const initial = initialValues(config);
            setValues(initial);
            onChange?.(initial);
          }}
        >
          Resetuj
        </button>
      </div>
    </aside>
  );
}
