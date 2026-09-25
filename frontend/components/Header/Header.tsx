"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import "./Header.css";
import DynamicSearchBar from "../DynamicSearchBar/DynamicSearchBar";

const links = [
  { href: "/", label: "Galeria" },
  { href: "/library", label: "Moja biblioteka" },
  { href: "/chatbot", label: "Czat bot" },
];

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="Header">
      <Link className="Header__brand" href="/">
        <img className="Header__chest" src="/assets/chest.svg" alt="" />
        <span className="Header__title">
          Games <span className="Header__title-accent">Vault</span>
        </span>
      </Link>
      <nav className="Header__nav">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className={`Header__link${pathname === l.href ? " Header__link--active" : ""}`}
          >
            {l.label}
          </Link>
        ))}
      </nav>
      <DynamicSearchBar />
      <Link className="Header__userButton" href="/register">
        Zarejestruj się
      </Link>
      <Link className="Header__userButton" href="/login">
        Zaloguj
      </Link>
    </header>
  );
}
