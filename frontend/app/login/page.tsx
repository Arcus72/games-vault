"use client";
import Link from "next/link";
import "../auth.scss";
import { loginUser } from "@/lib/api";
import { showMessage } from "@/components/Message/Message";
import { LoginData } from "@/interfaces/api";
import { useAuth, AuthUser } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();

  const formHandler = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget));

    const newUserData = {
      username_or_email: data.email,
      password: data.password,
    } as LoginData;

    loginUser(newUserData)
      .then((res) => {
        login({ email: newUserData.username_or_email });
        showMessage(res.message, "success");
        router.replace("/"); // bez wpisu w historii (dobre po loginie)
      })
      .catch((error) => {
        showMessage(error.message, "error");
      });
  };

  return (
    <main className="auth">
      <form className="auth__form" onSubmit={(e) => formHandler(e)}>
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
