import Link from 'next/link'
import './Fab.css'

export default function Fab() {
  return (
    <Link className="fab" href="/chatbot" aria-label="Otwórz czat bota">
      <img className="fab__icon" src="/assets/fab-icon.svg" alt="" />
    </Link>
  )
}
