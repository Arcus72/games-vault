import { FilterSection, FilterValues } from '../../interfaces/main';

export default function Year({
  section: s,
  values,
  set,
}: {
  section: Extract<FilterSection, { type: 'range' }>;
  values: FilterValues;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  return (
    <details className='FilterAside__section' open={s.open}>
      <summary className='FilterAside__header'>
        <span className='FilterAside__label'>{s.label}</span>
        <span className='FilterAside__chevron'>&gt;</span>
      </summary>

      <div className='FilterAside__year'>
        <input
          className='FilterAside__year-input'
          placeholder={s.startLabel ?? 'Od'}
          value={(values[s.startName] as string) ?? ''}
          onChange={(e) => set(s.startName, e.target.value || null)}
        />
        <span className='FilterAside__year-dash' />
        <input
          className='FilterAside__year-input'
          placeholder={s.endLabel ?? 'Do'}
          value={(values[s.endName] as string) ?? ''}
          onChange={(e) => set(s.endName, e.target.value || null)}
        />
      </div>
    </details>
  );
}
