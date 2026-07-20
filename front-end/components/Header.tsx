'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import './Header.css'

const links = [
  { href: '/', label: 'Gallery' },
  { href: '/library', label: 'My library' },
  { href: '/chatbot', label: 'Chat bot' },
]

export default function Header() {
  const pathname = usePathname()

  return (
    <header className="header">
      <Link className="header__brand" href="/">
        <img className="header__chest" src="/assets/chest.svg" alt="" />
        <span className="header__title">
          Games <span className="header__title-accent">Vault</span>
        </span>
      </Link>
      <nav className="header__nav">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className={`header__link${pathname === l.href ? ' header__link--active' : ''}`}
          >
            {l.label}
          </Link>
        ))}
      </nav>
      <span className="header__avatar">
        <img className="header__avatar-img" src="/assets/avatar.png" alt="Profile" />
      </span>
    </header>
  )
}
