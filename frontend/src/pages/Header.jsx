import { Link } from 'react-router-dom';
import logoImg from '../assets/IIA.png'

export default function Header() {
  return (
    <header className="site-header">
      <div className="Header">
        <img src={logoImg} className="base" alt="" />
        <h1>Is It AI?</h1>
      </div>
    
      <div>
        <nav className="nav-links">
          <Link to="/" alt="Check Page" hover="Check">
            Check
          </Link>
          <Link to="/about" alt="About Page" hover="About">
            About
          </Link>
          <Link to="/faq" alt="Frequently Asked Questions" hover="FAQ">
            FAQ
          </Link>
        </nav>
      </div>
    </header>
  );
}