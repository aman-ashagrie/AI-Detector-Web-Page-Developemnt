import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import logoImg from './assets/IIA.png'
import Check from './pages/Check'
import About from './pages/About'
import FAQ from './pages/FAQ'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <BrowserRouter>
      <main className="home">
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

        <div className="content-area">
          <Routes>
            <Route path="/" element={<Check />} />
            <Route path="/about" element={<About />} />
            <Route path="/faq" element={<FAQ />} />
          </Routes>
        </div>

      </main>
    </BrowserRouter>
  )
}

export default App