import "../auth.css";
import "./settings.css";

const sections = [
  {
    legend: "STEAMID",
    label: "Twój Steam ID",
    name: "steamId",
    placeholder: "STEAM_0:1:12345678",
  },
  {
    legend: "Zmień hasło",
    label: "Nowe hasło",
    name: "password",
    type: "password",
    placeholder: "••••••••",
    autoComplete: "new-password",
  },
];

// ponytail: plain forms, no submit handlers — back-end has no settings route yet.
export default function SettingsPage() {
  return (
    <main className="auth settings">
      {sections.map(({ legend, label, ...input }) => (
        <form className="settings__form" key={legend}>
          <fieldset className="settings__box">
            <legend className="settings__legend">{legend}</legend>

            <label className="settings__field">
              <span className="auth__label">{label}</span>
              <input className="auth__input" required {...input} />
            </label>

            <button className="auth__submit" type="submit">
              Potwierdź
            </button>
          </fieldset>
        </form>
      ))}
    </main>
  );
}
