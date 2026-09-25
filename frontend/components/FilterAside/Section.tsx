import { useState } from "react";
import { FilterSection, FilterValues } from "../../interfaces/main";
import Slider from "./Slider";

const MAX_SHOWN_OPTIONS = 5;

export default function Section({
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
        onChange={(e) => set(s.name, e.target.value || null)}
      />
    );
  }

  const checked =
    s.type === "checkboxes"
      ? ((values[s.name] as string[] | null) ?? [])
      : null;
  const [search, setSearch] = useState("");
  const visibleOptions =
    s.type === "checkboxes"
      ? s.options
          .filter((option) =>
            option.toLowerCase().includes(search.toLowerCase()),
          )
          .slice(0, MAX_SHOWN_OPTIONS)
      : [];

  return (
    <details className="filters__section" open={s.open}>
      <summary className="filters__header">
        <span className="filters__label">{s.label}</span>
        <span className="filters__chevron">&gt;</span>
      </summary>

      {s.type === "slider" && (
        <Slider section={s} value={values[s.name] as number | null} set={set} />
      )}

      {s.type === "range" && (
        <div className="filters__year">
          <input
            className="filters__year-input"
            placeholder={s.startLabel ?? "Od"}
            value={(values[s.startName] as string) ?? ""}
            onChange={(e) => set(s.startName, e.target.value || null)}
          />
          <span className="filters__year-dash" />
          <input
            className="filters__year-input"
            placeholder={s.endLabel ?? "Do"}
            value={(values[s.endName] as string) ?? ""}
            onChange={(e) => set(s.endName, e.target.value || null)}
          />
        </div>
      )}

      {s.type === "checkboxes" && checked && (
        <div className="filters__tags">
          {visibleOptions.map((option) => (
            <label className="filters__tag" key={option}>
              <input
                className="filters__tag-input"
                type="checkbox"
                checked={checked.includes(option)}
                onChange={(e) => {
                  const next = e.target.checked
                    ? [...checked, option]
                    : checked.filter((o) => o !== option);
                  set(s.name, next.length ? next : null); // [] would filter to zero games
                }}
              />
              <span className="filters__tag-box" />
              <span className="filters__tag-name">{option}</span>
            </label>
          ))}
          <input
            className="filters__search"
            placeholder="Szukaj po nazwie"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      )}
    </details>
  );
}
