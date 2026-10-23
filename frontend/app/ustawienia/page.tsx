"use client";

import { SubmitEvent, useEffect, useState } from "react";
import { updatePassword, updateSteamId, loadSteamLibrary } from "@/lib/api";
import { showMessage } from "@/components/Message/Message";
import { NewPasswordData } from "@/interfaces/api";
import "../auth.scss";
import "./settings.scss";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
export default function SettingsPage() {
  const { isLogged, user, updateUserData } = useAuth();
  const router = useRouter();
  const [steamId] = useState(user?.steam_id || false);

  useEffect(() => {
    if (!isLogged()) {
      router.push("/");
    }
  }, []);

  function onForm(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);

    const [oldPass, newPass1, newPass2] = ["oldPassword", "newPassword1", "newPassword2"].map(
      (key) => String(data.get(key) ?? "").trim(),
    );

    if (oldPass && newPass1 && newPass2) {
      if (newPass1 == newPass2) {
        const postData: NewPasswordData = {
          old_password: oldPass,
          new_password: newPass1,
        };

        updatePassword(postData)
          .then((res) => {
            showMessage(res.message);
          })
          .catch((error) => {
            showMessage(error.message, "error");
          });
      } else {
        showMessage("Nowe hasło i powtórzone hasło nie są takie same.", "error");
      }
    } else {
      showMessage("Wszyskie pola hasła muszą być wypełnione.", "error");
    }
  }

  const handleSteamIdForm = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const submitter = (e.nativeEvent as SubmitEvent).submitter as HTMLButtonElement | null;
    const buttonName = submitter?.name;

    if (buttonName === "send") {
      const data = new FormData(e.currentTarget, submitter);
      const newSteamId = data.get("steamId") as string;

      updateSteamId(newSteamId)
        .then((res) => {
          showMessage(res.message);
          updateUserData("steam_id", newSteamId);
        })
        .catch((error) => {
          showMessage(error.message, "error");
        });
    } else if (buttonName === "update") {
      loadSteamLibrary()
        .then((res) => {
          showMessage(res.message);
        })
        .catch((error) => {
          showMessage(error.message, "error");
        });
    }
  };
  return (
    <main className="auth settings">
      <form className="settings__form" onSubmit={onForm}>
        <fieldset className="settings__box">
          <legend className="settings__legend">Zmień hasło</legend>

          <label className="settings__field">
            <span className="auth__label">Stare hasło</span>
            <input
              className="auth__input"
              required
              placeholder="••••••••"
              type="password"
              name="oldPassword"
              minLength={6}
            />
          </label>

          <label className="settings__field">
            <span className="auth__label">Nowe hasło</span>
            <input
              className="auth__input"
              required
              placeholder="••••••••"
              type="password"
              name="newPassword1"
              minLength={6}
            />
          </label>

          <label className="settings__field">
            <span className="auth__label">Powtórz nowe hasło</span>
            <input
              className="auth__input"
              required
              placeholder="••••••••"
              type="password"
              name="newPassword2"
              minLength={6}
            />
          </label>

          <button className="auth__submit" type="submit">
            Potwierdź
          </button>
        </fieldset>
      </form>

      <form className="settings__form" onSubmit={handleSteamIdForm}>
        <fieldset className="settings__box">
          <legend className="settings__legend">Steam ID</legend>
          <label className="settings__field">
            <span className="auth__label">Ustaw Steam ID</span>
            <input
              className="auth__input"
              placeholder={(steamId as string) || "https://steamcommunity.com/profiles/XXXXXXXX"}
              type="text"
              name="steamId"
              minLength={6}
            />
          </label>

          <button className="auth__submit" name="send" type="submit">
            Potwierdź
          </button>
          <button
            className="auth__submit auth__submit--blue"
            name="update"
            type="submit"
            disabled={steamId == ""}
          >
            Pobierz gry z Steam
          </button>
        </fieldset>
      </form>
    </main>
  );
}
//
