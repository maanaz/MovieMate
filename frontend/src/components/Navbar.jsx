import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FaFilm, FaTv, FaPlus, FaChartBar, FaMagic, FaHome } from 'react-icons/fa'
import './Navbar.css'

const Navbar = () => {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <FaFilm className="brand-icon" />
          <span>MovieMate</span>
        </Link>
        
        <div className="navbar-links">
          <Link to="/" className={isActive('/') ? 'active' : ''}>
            <FaHome /> Home
          </Link>
          <Link to="/movies" className={isActive('/movies') ? 'active' : ''}>
            <FaFilm /> Movies
          </Link>
          <Link to="/tv-shows" className={isActive('/tv-shows') ? 'active' : ''}>
            <FaTv /> TV Shows
          </Link>
          <Link to="/add" className={isActive('/add') ? 'active' : ''}>
            <FaPlus /> Add Content
          </Link>
          <Link to="/recommendations" className={isActive('/recommendations') ? 'active' : ''}>
            <FaMagic /> Recommendations
          </Link>
          <Link to="/statistics" className={isActive('/statistics') ? 'active' : ''}>
            <FaChartBar /> Statistics
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default Navbar


