'use client';

import { useState, useEffect } from 'react';
import './aktywacja.scss';
import { useSearchParams } from 'next/navigation';
import { activateAccount } from '@/lib/api';
import { showMessage } from '@/components/Message/Message';

export default function AktywacjaPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSuccess, setIsSuccess] = useState(true);
  const searchParams = useSearchParams();

  useEffect(() => {
    const activateToken: string = searchParams.get('token');
    console.log(activateToken);
    activateAccount(activateToken)
      .then(() => {
        setIsSuccess(true);
      })
      .catch((error) => {
        console.log(error, error.status);
        showMessage(error.message, 'error');
        setIsSuccess(false);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [searchParams]);

  return (
    <main className='activate'>
      <div className='activate__card'>
        {isLoading ? (
          <div className='activate__loading'>
            <div className='activate__spinner' />
            <p className='activate__text'>Aktywowanie konta…</p>
          </div>
        ) : isSuccess ? (
          <div className='activate__success'>
            <div className='activate__check'>
              <svg viewBox='0 0 52 52' fill='none' xmlns='http://www.w3.org/2000/svg'>
                <circle
                  className='activate__check-circle'
                  cx='26'
                  cy='26'
                  r='24'
                  stroke='currentColor'
                  strokeWidth='3'
                />
                <path
                  className='activate__check-mark'
                  d='M15 27l7 7 15-15'
                  stroke='currentColor'
                  strokeWidth='3'
                  strokeLinecap='round'
                  strokeLinejoin='round'
                />
              </svg>
            </div>
            <h1 className='activate__title'>Konto aktywne</h1>
            <p className='activate__subtitle'>
              Twoje konto zostało pomyślnie aktywowane. Możesz się teraz zalogować.
            </p>
            <a className='activate__link' href='/login'>
              Przejdź do logowania
            </a>
          </div>
        ) : (
          <div className='activate__error'>
            <div className='activate__error-icon'>
              <svg viewBox='0 0 52 52' fill='none' xmlns='http://www.w3.org/2000/svg'>
                <circle
                  className='activate__error-circle'
                  cx='26'
                  cy='26'
                  r='24'
                  stroke='currentColor'
                  strokeWidth='3'
                />
                <path
                  className='activate__error-x'
                  d='M18 18l16 16M34 18l-16 16'
                  stroke='currentColor'
                  strokeWidth='3'
                  strokeLinecap='round'
                />
              </svg>
            </div>
            <h1 className='activate__title'>Wystąpił błąd</h1>
            <p className='activate__subtitle'>
              Nie udało się aktywować konta. Prosimy spróbować później.
            </p>
            <a className='activate__link activate__link--gray' href='/'>
              Wróć na stronę główną
            </a>
          </div>
        )}
      </div>
    </main>
  );
}
