import { FilterSection, FilterValues, SortValue } from '../../interfaces/main';

export default function Select({
  section: s,
  values,
  value,
  set,
}: {
  section: Extract<FilterSection, { type: 'select' }>;
  values?: FilterValues;
  value?: SortValue | null;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  const currentValue = value !== undefined ? value : (values?.[s.name] as SortValue | null);

  return (
    <details className='FilterAside__section' open={s.open}>
      <summary className='FilterAside__header'>
        <span className='FilterAside__label'>{s.label}</span>
        <span className='FilterAside__chevron'>&gt;</span>
      </summary>

      <select
        className='FilterAside__select'
        value={Math.max(
          0,
          s.options.findIndex((o) => o.value === currentValue),
        )}
        onChange={(e) => set(s.name, s.options[+e.target.value].value)}
      >
        {s.options.map((o, i) => (
          <option key={o.label} value={i}>
            {o.label}
          </option>
        ))}
      </select>
    </details>
  );
}
