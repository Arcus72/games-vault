import Link from "next/link";
import "./Fab.scss";

export default function Fab() {
  return (
    <Link className="Fab" href="/chatbot" aria-label="Otwórz chat bota">
      <img className="Fab__icon" src="/assets/fab-icon.svg" alt="" />
    </Link>
  );
}
