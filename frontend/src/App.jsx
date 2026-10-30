import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Check from './pages/Check'
import About from './pages/About'
import FAQ from './pages/FAQ'
import Header from './pages/Header'
import Footer from './pages/Footer'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <BrowserRouter>
      <Header/>      
      <main className="home">
        

        <div className="content-area">
          <Routes>
            <Route path="/" element={<Check />} />
            <Route path="/about" element={<About />} />
            <Route path="/faq" element={<FAQ />} />
          </Routes>
        </div>
      </main>
      <Footer/>
    </BrowserRouter>
  )
}

export default App