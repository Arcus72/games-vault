"use client";
import { useRef } from "react";
import Link from "next/link";
import "../auth.css";
import { createUser } from "@/lib/api";
import { CreateUserData } from "@/interfaces/api";
import { showMessage } from "@/components/Message/Message";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const formHandler = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget));

    const newUserData = {
      username: data.userSteamID,
      email: data.email,
      password: data.password,
      phone: "485544465",
    } as CreateUserData;

    createUser(newUserData)
      .then((res) => {
        showMessage(res.message, "success");
        router.replace("/");
      })
      .catch((error) => {
        showMessage(error.message, "error");
      });
  };

  return (
    <main className="auth">
      <form className="auth__form" onSubmit={(e) => formHandler(e)}>
        <h1 className="auth__title">Zarejestruj się</h1>

        <label className="auth__field">
          <span className="auth__label">Twój Steam ID</span>
          <input
            className="auth__input"
            name="userSteamID"
            placeholder="STEAM_0:1:12345678"
            minLength={8}
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
