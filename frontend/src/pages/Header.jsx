import { Link } from 'react-router-dom';
import logoImg from './assets/IIA.png';

export default function Header() {
  return (
    <header className="site-header">
      <Link to="/" className="Header">
        <img src={logoImg} className="base" alt="Is It AI Logo" />
        <h1>Is It AI?</h1>
      </Link>
      <nav className="nav-links">
        <Link to="/about" alt="About Page" hover="About">
          About
        </Link>
        <Link to="/faq" alt="Frequently Asked Questions" hover="FAQ">
          FAQ
        </Link>
      </nav>
    </header>
  );
}