'use client';

import { useEffect, useState } from 'react';
import './FilterAside.scss';
import { FilterSection, FilterValues } from '../../interfaces/main';
import Checkbox from './Checkbox';
import Search from './Search';
import Select from './Select';
import Slider from './Slider';
import Year from './Year';
import BoolCheck from './BoolCheck';
import { loadAtributeListForFilter } from '@/lib/api';
import Button from '../Button/Button';

async function getConfig(skipNames: string[] = []): Promise<FilterSection[]> {
  const tags = skipNames.includes('tags')
    ? []
    : await loadAtributeListForFilter('/api/get_tags', 'gameTags');

  const platforms = skipNames.includes('platforms')
    ? []
    : await loadAtributeListForFilter('/api/get_platforms', 'gamePlatforms');

  const genres = skipNames.includes('genres')
    ? []
    : await loadAtributeListForFilter('/api/get_genres', 'gameGenres');

  const languages = skipNames.includes('languages')
    ? []
    : await loadAtributeListForFilter('/api/get_languages', 'gamelanguages');

  const sections: FilterSection[] = [
    { type: 'search', name: 'name' },
    {
      type: 'select',
      label: 'Sortuj według',
      name: 'sorting',
      options: [
        { label: 'Trafność', value: { sort_by: 'recommendations', ascending: 0 } },
        { label: 'Popularność', value: { sort_by: 'popularity', ascending: 0 } },
        { label: 'Data wydania', value: { sort_by: 'release_date', ascending: 1 } },
        { label: 'Nazwa', value: { sort_by: 'name', ascending: 1 } },
        { label: 'Najniższa cena', value: { sort_by: 'price', ascending: 1 } },
        { label: 'Najwyższa cena', value: { sort_by: 'price', ascending: 0 } },
      ],
      open: true,
      value: { sort_by: 'popularity', ascending: 0 },
    },
    {
      type: 'slider',
      label: 'zakres cen',
      name: 'price_max',
      steps: [
        { label: 'Za darmo', value: 0 },
        { label: 'poniżej 20zł', value: 20 },
        { label: 'poniżej 50zł', value: 50 },
        { label: 'poniżej 100zł', value: 100 },
        { label: 'poniżej 200zł', value: 200 },
        { label: 'Bez limitu', value: null },
      ],
      open: true,
    },
    {
      type: 'range',
      label: 'Zakres lat',
      name: 'yearSpan',
      startName: 'release_date_min_year',
      endName: 'release_date_max_year',
      open: true,
    },
    {
      type: 'boolCheck',
      label: 'Premiery',
      name: 'IsReleased',
      option: 'Tylko wydane',
      checked: true,
      open: true,
    },
    {
      type: 'checkboxes',
      label: 'Tagi',
      name: 'tags',
      options: tags || [''],
      open: true,
    },
    {
      type: 'checkboxes',
      label: 'Języki',
      name: 'languages',
      options: languages || [''],
    },
    {
      type: 'checkboxes',
      label: 'Platformy',
      name: 'platforms',
      options: platforms || [''],
    },
    {
      type: 'checkboxes',
      label: 'Kategorie',
      name: 'genres',
      options: genres || [''],
    },
  ];

  return sections.filter((s) => !skipNames.includes(s.name));
}

function initialValues(filterConfig: FilterSection[]): FilterValues {
  const values: FilterValues = {};
  filterConfig.forEach((s) => {
    if (s.type === 'search') {
      values[s.name] = s.value ?? null;
    } else if (s.type === 'select') {
      values[s.name] = s.value ?? null;
    } else if (s.type === 'slider') {
      values[s.name] = s.value ?? null;
    } else if (s.type === 'range') {
      values[s.startName] = s.startValue ?? null;
      values[s.endName] = s.endValue ?? null;
    } else if (s.type === 'boolCheck') {
      values[s.name] = s.checked ?? null;
    } else {
      values[s.name] = s.checked?.length ? s.checked : null;
    }
  });
  return values;
}

interface FilterAsideProps {
  onSave?: (values: FilterValues) => void;
  onChange?: (values: FilterValues) => void;
  skipNames?: string[];
  defaultOpenMobile?: boolean;
}

export default function FilterAside({
  onSave,
  onChange,
  skipNames = [],
  defaultOpenMobile = false,
}: FilterAsideProps) {
  const [config, setConfig] = useState<FilterSection[]>([]);
  const [values, setValues] = useState<FilterValues>({});
  const [isOpenMobile, setIsOpenMobile] = useState<boolean>(defaultOpenMobile);

  const skipNamesKey = skipNames.join(',');

  useEffect(() => {
    getConfig(skipNames).then((c) => {
      setConfig(c);
      setValues(initialValues(c));
    });
  }, [skipNamesKey]);

  const set = (key: string, value: FilterValues[string]) => {
    const next = { ...values, [key]: value };
    setValues(next);
    onChange?.(next);
  };

  const toggleOpenMobile = () => {
    setIsOpenMobile((prev) => !prev);
  };

  const handleSave = () => {
    onSave?.(values);
    setIsOpenMobile(false);
  };

  const activeCount = Object.values(values).filter((v) => {
    if (v === null || v === undefined || v === '') return false;
    if (Array.isArray(v) && v.length === 0) return false;
    return true;
  }).length;

  return (
    <aside className={`FilterAside ${isOpenMobile ? 'FilterAside--open' : ''}`}>
      <div className='FilterAside__header-main' onClick={toggleOpenMobile}>
        <h2 className='FilterAside__title'>
          Filtry:
          {activeCount > 0 && <span className='FilterAside__badge'>{activeCount}</span>}
        </h2>
        <button
          type='button'
          className='FilterAside__toggle'
          onClick={(e) => {
            e.stopPropagation();
            toggleOpenMobile();
          }}
        >
          <span className='FilterAside__toggle-text'>{isOpenMobile ? 'Zwiń' : 'Rozwiń'}</span>
          <svg
            className='FilterAside__toggle-chevron'
            viewBox='0 0 12 8'
            fill='none'
            xmlns='http://www.w3.org/2000/svg'
            aria-hidden='true'
          >
            <path
              d='M1 1.5L6 6.5L11 1.5'
              stroke='currentColor'
              strokeWidth='2'
              strokeLinecap='round'
              strokeLinejoin='round'
            />
          </svg>
        </button>
      </div>

      <div id='filter-aside-content' className='FilterAside__content'>
        {config.map((s) => {
          switch (s.type) {
            case 'search':
              return <Search key={s.name} section={s} values={values} set={set} />;
            case 'slider':
              return <Slider key={s.name} section={s} values={values} set={set} />;
            case 'select':
              return <Select key={s.name} section={s} values={values} set={set} />;
            case 'range':
              return <Year key={s.name} section={s} values={values} set={set} />;
            case 'checkboxes':
              return <Checkbox key={s.name} section={s} values={values} set={set} />;
            case 'boolCheck':
              return <BoolCheck key={s.name} section={s} values={values} set={set} />;
            default:
              return null;
          }
        })}
        <div className='FilterAside__buttons'>
          <Button text='Zapisz' onClick={handleSave} className='FilterAside__btn' />
          <Button
            text='Reset'
            onClick={() => {
              const initial = initialValues(config);
              setValues(initial);
              onChange?.(initial);
            }}
            className='FilterAside__btn'
            color='gray'
          />
        </div>
        <button type='button' className='FilterAside__collapse-bottom' onClick={toggleOpenMobile}>
          Zwiń filtry
          <svg
            className='FilterAside__collapse-icon'
            viewBox='0 0 12 8'
            fill='none'
            xmlns='http://www.w3.org/2000/svg'
            aria-hidden='true'
          >
            <path
              d='M1 6.5L6 1.5L11 6.5'
              stroke='currentColor'
              strokeWidth='2'
              strokeLinecap='round'
              strokeLinejoin='round'
            />
          </svg>
        </button>
      </div>
    </aside>
  );
}
