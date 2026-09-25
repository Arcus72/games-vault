import { FilterSection, FilterValues } from "../../interfaces/main";

export default function Slider({
  section: s,
  value,
  set,
}: {
  section: Extract<FilterSection, { type: "slider" }>;
  value: number | null;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  const steps = s.steps;
  const index = Math.max(0, steps.findIndex((step) => step.value === value));
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
        onChange={(e) => set(s.name, steps[Number(e.target.value)].value)}
      />
      <p className="filters__slider-value">{steps[index].label}</p>
    </div>
  );
}
