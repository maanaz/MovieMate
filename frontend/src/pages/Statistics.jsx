import React, { useState, useEffect } from 'react'
import { contentAPI, watchHistoryAPI } from '../services/api'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import './Statistics.css'

const Statistics = () => {
  const [stats, setStats] = useState(null)
  const [watchStats, setWatchStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      const [contentStats, historyStats] = await Promise.all([
        contentAPI.getStatistics(),
        watchHistoryAPI.getStatistics(),
      ])
      setStats(contentStats.data)
      setWatchStats(historyStats.data)
    } catch (error) {
      console.error('Error loading statistics:', error)
    } finally {
      setLoading(false)
    }
  }

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']

  if (loading) {
    return <div className="loading">Loading statistics...</div>
  }

  const statusData = stats?.status_counts ? Object.entries(stats.status_counts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  })) : []

  return (
    <div className="statistics">
      <h1 className="page-title">Statistics</h1>

      <div className="stats-grid">
        {/* Overall Stats */}
        <div className="stat-card">
          <h2>Collection Overview</h2>
          <div className="stat-items">
            <div className="stat-item">
              <div className="stat-value">{stats?.total || 0}</div>
              <div className="stat-label">Total Items</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats?.movies || 0}</div>
              <div className="stat-label">Movies</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats?.tv_shows || 0}</div>
              <div className="stat-label">TV Shows</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats?.average_rating?.toFixed(1) || 'N/A'}</div>
              <div className="stat-label">Avg Rating</div>
            </div>
          </div>
        </div>

        {/* Status Distribution */}
        <div className="stat-card">
          <h2>Status Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Watch Time Stats */}
        {watchStats && (
          <>
            <div className="stat-card">
              <h2>Watch Time</h2>
              <div className="watch-time-stats">
                <div className="time-stat">
                  <div className="time-value">{watchStats.weekly_hours || 0}h</div>
                  <div className="time-label">This Week</div>
                  <div className="time-detail">({watchStats.weekly_minutes || 0} minutes)</div>
                </div>
                <div className="time-stat">
                  <div className="time-value">{watchStats.monthly_hours || 0}h</div>
                  <div className="time-label">This Month</div>
                  <div className="time-detail">({watchStats.monthly_minutes || 0} minutes)</div>
                </div>
              </div>
            </div>

            {/* Daily Watch Time Chart */}
            <div className="stat-card full-width">
              <h2>Daily Watch Time (Last 7 Days)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={watchStats.daily_breakdown || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="minutes" fill="#667eea" name="Watch Time (minutes)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Weekly Trend */}
            <div className="stat-card full-width">
              <h2>Watch Time Trend</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={watchStats.daily_breakdown || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="minutes" stroke="#667eea" strokeWidth={2} name="Watch Time" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Statistics


