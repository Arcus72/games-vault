import Link from "next/link";
import "../auth.css";

// ponytail: plain form, no submit handler — back-end has no auth route yet.
export default function RegisterPage() {
  return (
    <main className="auth">
      <form className="auth__form">
        <h1 className="auth__title">Zarejestruj się</h1>

        <label className="auth__field">
          <span className="auth__label">Nazwa użytkownika</span>
          <input
            className="auth__input"
            name="username"
            placeholder="gracz123"
            autoComplete="username"
            required
          />
        </label>

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
            autoComplete="new-password"
            minLength={8}
            required
          />
        </label>

        <button className="auth__submit" type="submit">
          Załóż konto
        </button>

        <p className="auth__alt">
          Masz już konto?{" "}
          <Link className="auth__link" href="/login">
            Zaloguj
          </Link>
        </p>
      </form>
    </main>
  );
}
