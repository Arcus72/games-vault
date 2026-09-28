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
        className="FilterAside__search"
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
    <details className="FilterAside__section" open={s.open}>
      <summary className="FilterAside__header">
        <span className="FilterAside__label">{s.label}</span>
        <span className="FilterAside__chevron">&gt;</span>
      </summary>

      {s.type === "slider" && (
        <Slider section={s} value={values[s.name] as number | null} set={set} />
      )}

      {s.type === "range" && (
        <div className="FilterAside__year">
          <input
            className="FilterAside__year-input"
            placeholder={s.startLabel ?? "Od"}
            value={(values[s.startName] as string) ?? ""}
            onChange={(e) => set(s.startName, e.target.value || null)}
          />
          <span className="FilterAside__year-dash" />
          <input
            className="FilterAside__year-input"
            placeholder={s.endLabel ?? "Do"}
            value={(values[s.endName] as string) ?? ""}
            onChange={(e) => set(s.endName, e.target.value || null)}
          />
        </div>
      )}

      {s.type === "checkboxes" && checked && (
        <div className="FilterAside__tags">
          {visibleOptions.map((option) => (
            <label className="FilterAside__tag" key={option}>
              <input
                className="FilterAside__tag-input"
                type="checkbox"
                checked={checked.includes(option)}
                onChange={(e) => {
                  const next = e.target.checked
                    ? [...checked, option]
                    : checked.filter((o) => o !== option);
                  set(s.name, next.length ? next : null); // [] would filter to zero games
                }}
              />
              <span className="FilterAside__tag-box" />
              <span className="FilterAside__tag-name">{option}</span>
            </label>
          ))}
          <input
            className="FilterAside__search"
            placeholder="Szukaj po nazwie"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      )}
    </details>
  );
}
