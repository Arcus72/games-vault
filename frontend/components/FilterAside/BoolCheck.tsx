import { FilterSection, FilterValues } from '../../interfaces/main';

export default function BoolCheck({
  section: s,
  values,
  value,
  set,
}: {
  section: Extract<FilterSection, { type: 'boolCheck' }>;
  values?: FilterValues;
  value?: boolean | null;
  set: (key: string, value: FilterValues[string]) => void;
}) {
  const currentValue = value !== undefined ? value : (values?.[s.name] as boolean | null);

  return (
    <details className='FilterAside__section' open={s.open}>
      <summary className='FilterAside__header'>
        <span className='FilterAside__label'>{s.label}</span>
        <span className='FilterAside__chevron'>&gt;</span>
      </summary>
      <div className='FilterAside__tags'>
        <label className='FilterAside__tag'>
          <input
            className='FilterAside__tag-input'
            type='checkbox'
            checked={currentValue ?? false}
            onChange={(e) => {
              console.log(e);
              set(s.name, e.target.checked || false);
            }}
          />
          <span className='FilterAside__tag-box' />
          <span className='FilterAside__tag-name'>{s.option}</span>
        </label>
      </div>
    </details>
  );
}
