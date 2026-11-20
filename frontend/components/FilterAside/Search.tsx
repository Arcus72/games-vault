import { FilterSection, FilterValues } from '../../interfaces/main';

export default function Search({
  section: s,
  values,
  value,
  set,
}: {
  section: Extract<FilterSection, { type: 'search' }>;
  values?: FilterValues;
  value?: string | null;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  const currentValue = value !== undefined ? value : (values?.[s.name] as string | null);

  return (
    <input
      className='FilterAside__search'
      placeholder={s.placeholder ?? 'Szukaj po nazwie'}
      value={currentValue ?? ''}
      onChange={(e) => set(s.name, e.target.value || null)}
    />
  );
}
