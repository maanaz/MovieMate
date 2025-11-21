import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Movies from './pages/Movies'
import TVShows from './pages/TVShows'
import AddContent from './pages/AddContent'
import ContentDetail from './pages/ContentDetail'
import Statistics from './pages/Statistics'
import Recommendations from './pages/Recommendations'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/movies" element={<Movies />} />
            <Route path="/tv-shows" element={<TVShows />} />
            <Route path="/add" element={<AddContent />} />
            <Route path="/content/:id" element={<ContentDetail />} />
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/recommendations" element={<Recommendations />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </Router>
  )
}

export default App


