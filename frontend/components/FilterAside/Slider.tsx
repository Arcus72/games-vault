import { FilterSection, FilterValues } from '../../interfaces/main';

export default function Slider({
  section: s,
  values,
  value,
  set,
}: {
  section: Extract<FilterSection, { type: 'slider' }>;
  values?: FilterValues;
  value?: number | null;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  const currentValue = value !== undefined ? value : (values?.[s.name] as number | null);
  const steps = s.steps;
  const index = Math.max(0, steps.findIndex((step) => step.value === currentValue));
  const percent = steps.length > 1 ? (index / (steps.length - 1)) * 100 : 0;

  return (
    <details className='FilterAside__section' open={s.open}>
      <summary className='FilterAside__header'>
        <span className='FilterAside__label'>{s.label}</span>
        <span className='FilterAside__chevron'>&gt;</span>
      </summary>

      <div className='FilterAside__slider'>
        <input
          className='FilterAside__slider-input'
          type='range'
          min={0}
          max={steps.length - 1}
          step={1}
          value={index}
          style={{ ['--filters-slider-fill' as string]: `${percent}%` }}
          onChange={(e) => set(s.name, steps[Number(e.target.value)].value)}
        />
        <p className='FilterAside__slider-value'>{steps[index].label}</p>
      </div>
    </details>
  );
}
