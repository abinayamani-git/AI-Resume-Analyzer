import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { FileCheck2, Menu, X } from 'lucide-react'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/analyze', label: 'Analyze Resume' },
  { to: '/how-it-works', label: 'How It Works' },
  { to: '/about', label: 'About' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <header className={`navbar ${open ? 'open' : ''}`}>
        <div className="container navbar-inner">
          <Link to="/" className="brand" onClick={() => setOpen(false)} aria-label="AI Resume Analyzer home">
            <span className="brand-mark" aria-hidden="true">
              <FileCheck2 size={18} />
            </span>
            AI Resume Analyzer
          </Link>

          <nav id="mobile-nav" aria-label="Primary">
            <ul className="nav-links">
              {links.map((link) => (
                <li key={link.to}>
                  <NavLink
                    to={link.to}
                    end={link.end}
                    onClick={() => setOpen(false)}
                    className={({ isActive }) => (isActive ? 'active' : undefined)}
                  >
                    {link.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>

          <div className="nav-actions">
            <Link to="/analyze" className="btn btn-primary" onClick={() => setOpen(false)}>
              Analyze Resume
            </Link>
          </div>

          <button
            type="button"
            className="nav-toggle"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? 'Close menu' : 'Open menu'}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </header>
    </>
  )
}
