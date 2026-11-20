import { useState } from 'react';
import { FilterSection, FilterValues } from '../../interfaces/main';

const MAX_SHOWN_OPTIONS = 5;

export default function Checkbox({
  section: s,
  values,
  value,
  set,
}: {
  section: Extract<FilterSection, { type: 'checkboxes' }>;
  values?: FilterValues;
  value?: string[] | null;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  const checked = value ?? (values ? (values[s.name] as string[] | null) : null) ?? [];
  const [search, setSearch] = useState('');

  const visibleOptions = s.options
    .filter((option) => option.toLowerCase().includes(search.toLowerCase()))
    .slice(0, MAX_SHOWN_OPTIONS);

  return (
    <details className='FilterAside__section' open={s.open}>
      <summary className='FilterAside__header'>
        <span className='FilterAside__label'>{s.label}</span>
        <span className='FilterAside__chevron'>&gt;</span>
      </summary>

      <div className='FilterAside__tags'>
        {visibleOptions.map((option) => (
          <label className='FilterAside__tag' key={option}>
            <input
              className='FilterAside__tag-input'
              type='checkbox'
              checked={checked.includes(option)}
              onChange={(e) => {
                const next = e.target.checked
                  ? [...checked, option]
                  : checked.filter((o) => o !== option);
                set(s.name, next.length ? next : null); // [] would filter to zero games
              }}
            />
            <span className='FilterAside__tag-box' />
            <span className='FilterAside__tag-name'>{option}</span>
          </label>
        ))}
        <input
          className='FilterAside__search'
          placeholder='Szukaj po nazwie'
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
    </details>
  );
}
