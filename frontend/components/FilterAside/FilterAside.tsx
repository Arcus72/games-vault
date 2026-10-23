"use client";

import { useEffect, useState } from "react";
import "./FilterAside.scss";
import { FilterSection, FilterValues } from "../../interfaces/main";
import Section from "./Section";
import { loadAtributeListForFilter } from "@/lib/api";
import Button from "../Button/Button";
async function getConfig(): Promise<FilterSection[]> {
  const tags = await loadAtributeListForFilter("/api/get_tags", "gameTags");

  const platforms = await loadAtributeListForFilter("/api/get_platforms", "gamePlatforms");

  const genres = await loadAtributeListForFilter("/api/get_genres", "gameGenres");

  const languages = await loadAtributeListForFilter("/api/get_languages", "gamelanguages");

  return [
    { type: "search", name: "name" },
    {
      type: "select",
      label: "Sortuj według",
      name: "sorting",
      options: [
        { label: "Trafność", value: { sort_by: "recommendations", ascending: 0 } },
        { label: "Data wydania", value: { sort_by: "release_date", ascending: 1 } },
        { label: "Nazwa", value: { sort_by: "name", ascending: 1 } },
        { label: "Najniższa cena", value: { sort_by: "price", ascending: 1 } },
        { label: "Najwyższa cena", value: { sort_by: "price", ascending: 0 } },
      ],
      open: true,
    },
    {
      type: "slider",
      label: "zakres cen",
      name: "price_max",
      value: null,
      steps: [
        { label: "Za darmo", value: 0 },
        { label: "poniżej 20zł", value: 20 },
        { label: "poniżej 50zł", value: 50 },
        { label: "poniżej 100zł", value: 100 },
        { label: "poniżej 200zł", value: 200 },
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
    if (s.type === "search" || s.type === "select") values[s.name] = null;
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
    <aside className="FilterAside">
      <h2 className="FilterAside__title">Filtry:</h2>
      {config.map((s) => (
        <Section key={s.name} section={s} values={values} set={set} />
      ))}
      <div className="FilterAside__buttons">
        <Button text="Zapisz" onClick={() => onSave?.(values)} className="FilterAside__btn" />
        <Button
          text="Reset"
          onClick={() => {
            const initial = initialValues(config);
            setValues(initial);
            onChange?.(initial);
          }}
          className="FilterAside__btn"
          color="gray"
        />
      </div>
    </aside>
  );
}
