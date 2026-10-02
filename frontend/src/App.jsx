import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import Analyze from './pages/Analyze'
import Results from './pages/Results'
import HowItWorks from './pages/HowItWorks'
import About from './pages/About'

/**
 * App shell: navigation + routed pages.
 * Results stay available via AnalysisContext after a successful analysis.
 */
export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main id="main-content" className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/results" element={<Results />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
