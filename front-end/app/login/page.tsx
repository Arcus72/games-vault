import Link from "next/link";
import "../auth.css";

// ponytail: plain form, no submit handler — back-end has no auth route yet.
export default function LoginPage() {
  return (
    <main className="auth">
      <form className="auth__form">
        <h1 className="auth__title">Zaloguj</h1>

        <label className="auth__field">
          <span className="auth__label">E-mail</span>
          <input
            className="auth__input"
            type="email"
            name="email"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
        </label>

        <label className="auth__field">
          <span className="auth__label">Hasło</span>
          <input
            className="auth__input"
            type="password"
            name="password"
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />
        </label>

        <button className="auth__submit" type="submit">
          Zaloguj
        </button>

        <p className="auth__alt">
          Nie masz konta?{" "}
          <Link className="auth__link" href="/register">
            Zarejestruj się
          </Link>
        </p>
      </form>
    </main>
  );
}
