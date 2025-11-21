import React from 'react'
import { Link } from 'react-router-dom'
import { FaStar, FaClock, FaVideo } from 'react-icons/fa'
import { motion } from 'framer-motion'
import './ContentCard.css'

const cardVariants = {
  hidden: { opacity: 0, y: 8, scale: 0.995 },
  enter: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.35, ease: 'easeOut' } },
  hover: { scale: 1.03, transition: { duration: 0.18 } },
}

const ContentCard = ({ content }) => {
  const statusColors = {
    watching: '#4CAF50',
    completed: '#2196F3',
    wishlist: '#FF9800',
    paused: '#9E9E9E',
  }

  const statusColor = statusColors[content?.status] || '#9E9E9E'

  const cardInner = (
    <>
      <div className="card-image">
        {content.poster_url ? (
          <img src={content.poster_url} alt={content.title} />
        ) : (
          <div className="placeholder-image">
            <FaVideo />
          </div>
        )}
        <div className="card-status" style={{ backgroundColor: statusColor }}>
          {content.status || 'unknown'}
        </div>
      </div>
      
      <div className="card-content">
        <h3 className="card-title">{content.title}</h3>
        {content.director && (
          <p className="card-director">{content.director}</p>
        )}
        {content.release_date && (
          <p className="card-date">{new Date(content.release_date).getFullYear()}</p>
        )}
        
        <div className="card-footer">
          {content.rating_value && (
            <div className="card-rating">
              <FaStar className="star-icon" />
              <span>{content.rating_value}/10</span>
            </div>
          )}
          {content.runtime && (
            <div className="card-runtime">
              <FaClock />
              <span>{content.runtime} min</span>
            </div>
          )}
        </div>
        
        {content.genre && content.genre.length > 0 && (
          <div className="card-genres">
            {content.genre.slice(0, 3).map((g, idx) => (
              <span key={g?.id ?? g?.name ?? idx} className="genre-tag">{g?.name ?? g}</span>
            ))}
          </div>
        )}
      </div>
    </>
  )

  return (
    <motion.div variants={cardVariants} initial="hidden" animate="enter" whileHover="hover" className="content-card-wrapper">
      {content?.id ? (
        <Link to={`/content/${content.id}`} className="content-card">
          {cardInner}
        </Link>
      ) : (
        <div className="content-card external-card">
          {cardInner}
          <div className="external-cta">
            <a className="btn-add" href={`/add?tmdb_id=${content.tmdb_id || ''}&type=${content.content_type || ''}`}>Add</a>
          </div>
        </div>
      )}
    </motion.div>
  )

}

export default ContentCard


