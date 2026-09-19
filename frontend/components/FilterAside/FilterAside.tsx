"use client";

import { useState } from "react";
import "./FilterAside.css";
import { FilterSection } from "../../interfaces";

/** Current value of every filter, keyed by section name. */
export type FilterValues = Record<
  string,
  string | string[] | { start: string | null; end: string | null } | null
>;

// ponytail: these option strings are also the values POSTed to /api/games — back-end must match.
export const FULL_FILTERS: FilterSection[] = [
  { type: "search", name: "name" },
  {
    type: "slider",
    label: "zakres cen",
    name: "maxPrice",
    value: "poniżej 10$",
    steps: [
      "Za darmo",
      "poniżej 5$",
      "poniżej 10$",
      "poniżej 20$",
      "poniżej 50$",
      "Bez limitu",
    ],
    open: true,
  },
  { type: "range", label: "Zakres lat", name: "yearSpan", open: true },
  {
    type: "checkboxes",
    label: "Tagi",
    name: "tags",
    options: ["RPG", "Przygodowe", "Niezależne", "Akcja"],
    checked: ["RPG"],
    open: true,
  },
  {
    type: "checkboxes",
    label: "Języki",
    name: "languages",
    options: ["Angielski", "Polski", "Niemiecki", "Francuski"],
  },
];

function initialValues(filterConfig: FilterSection[]): FilterValues {
  const values: FilterValues = {};
  filterConfig.forEach((s) => {
    if (s.type === "search") values[s.name] = null;
    else if (s.type === "slider") values[s.name] = s.value;
    else if (s.type === "range") values[s.name] = { start: null, end: null };
    else {
      values[s.name] = s.checked ?? [];
    }
  });
  return values;
}

export default function FilterAside({
  filterConfig,
  onSave,
  onChange,
}: {
  filterConfig: FilterSection[];
  onSave?: (values: FilterValues) => void;
  /** Called with the full value set after every single change. */
  onChange?: (values: FilterValues) => void;
}) {
  const [values, setValues] = useState(() => initialValues(filterConfig));

  const set = (key: string, value: FilterValues[string]) => {
    const next = { ...values, [key]: value };
    setValues(next);
    onChange?.(next);
  };

  return (
    <aside className="filters">
      <h2 className="filters__title">Filtry:</h2>
      {filterConfig.map((s) => (
        <Section key={s.name} section={s} values={values} set={set} />
      ))}
      <div className="filters__buttons">
        <button
          className="filters__btn filters__btn--save"
          onClick={() => onSave?.(values)}
        >
          Zapisz
        </button>
        <button
          className="filters__btn filters__btn--reset"
          onClick={() => {
            const initial = initialValues(filterConfig);
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

function Slider({
  section: s,
  value,
  set,
}: {
  section: Extract<FilterSection, { type: "slider" }>;
  value: string;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  const steps = s.steps ?? [s.value];
  const index = Math.max(0, steps.indexOf(value));
  const percent = steps.length > 1 ? (index / (steps.length - 1)) * 100 : 0;

  return (
    <div className="filters__slider">
      <input
        className="filters__slider-input"
        type="range"
        min={0}
        max={steps.length - 1}
        step={1}
        value={index}
        style={{ ["--filters-slider-fill" as string]: `${percent}%` }}
        onChange={(e) => set(s.name, steps[Number(e.target.value)])}
      />
      <p className="filters__slider-value">{steps[index]}</p>
    </div>
  );
}

function Section({
  section: s,
  values,
  set,
}: {
  section: FilterSection;
  values: FilterValues;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  if (s.type === "search") {
    return (
      <input
        className="filters__search"
        placeholder={s.placeholder ?? "Szukaj po nazwie"}
        value={(values[s.name] as string) ?? ""}
        onChange={(e) => set(s.name, e.target.value)}
      />
    );
  }

  const range =
    s.type === "range"
      ? (values[s.name] as { start: string | null; end: string | null })
      : null;
  const checked = s.type === "checkboxes" ? (values[s.name] as string[]) : null;

  return (
    <details className="filters__section" open={s.open}>
      <summary className="filters__header">
        <span className="filters__label">{s.label}</span>
        <span className="filters__chevron">&gt;</span>
      </summary>

      {s.type === "slider" && (
        <Slider section={s} value={values[s.name] as string} set={set} />
      )}

      {s.type === "range" && range && (
        <div className="filters__year">
          <input
            className="filters__year-input"
            placeholder={s.startLabel ?? "Od"}
            value={range.start ?? ""}
            onChange={(e) => set(s.name, { ...range, start: e.target.value })}
          />
          <span className="filters__year-dash" />
          <input
            className="filters__year-input"
            placeholder={s.endLabel ?? "Do"}
            value={range.end ?? ""}
            onChange={(e) => set(s.name, { ...range, end: e.target.value })}
          />
        </div>
      )}

      {s.type === "checkboxes" && checked && (
        <div className="filters__tags">
          {s.options.map((option) => (
            <label className="filters__tag" key={option}>
              <input
                className="filters__tag-input"
                type="checkbox"
                checked={checked.includes(option)}
                onChange={(e) =>
                  set(
                    s.name,
                    e.target.checked
                      ? [...checked, option]
                      : checked.filter((o) => o !== option),
                  )
                }
              />
              <span className="filters__tag-box" />
              <span className="filters__tag-name">{option}</span>
            </label>
          ))}
          {/* <input className="filters__search" placeholder="Szukaj po nazwie" /> */}
        </div>
      )}
    </details>
  );
}
