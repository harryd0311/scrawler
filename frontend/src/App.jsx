import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { format, subDays } from 'date-fns'
import { Newspaper, RefreshCw, Star, Zap } from 'lucide-react'
import ArticleCard from './components/ArticleCard'
import CategoryFilter from './components/CategoryFilter'
import DateFilter from './components/DateFilter'

const CATEGORIES = ['All', 'AI', 'WebDev', 'SpringBoot', 'AWS', 'Azure', 'DevOps', 'General']

const VIEWS = [
  { id: 'today', label: "Today's News" },
  { id: 'history', label: '30-Day History' },
  { id: 'favorites', label: 'Favorites' },
]

export default function App() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(false)
  const [crawling, setCrawling] = useState(false)
  const [view, setView] = useState('today')
  const [category, setCategory] = useState('All')
  const [selectedDate, setSelectedDate] = useState(format(subDays(new Date(), 1), 'yyyy-MM-dd'))
  const [stats, setStats] = useState({ total: 0, starred: 0, today: 0, by_category: {} })

  const fetchArticles = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (view === 'today') params.date_filter = format(new Date(), 'yyyy-MM-dd')
      if (view === 'history') params.date_filter = selectedDate
      if (view === 'favorites') params.starred = true
      if (category !== 'All') params.category = category

      const { data } = await axios.get('/api/articles', { params })
      setArticles(data)
    } catch (err) {
      console.error('Failed to fetch articles:', err)
    } finally {
      setLoading(false)
    }
  }, [view, category, selectedDate])

  const fetchStats = useCallback(async () => {
    try {
      const { data } = await axios.get('/api/stats')
      setStats(data)
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }, [])

  useEffect(() => {
    fetchArticles()
  }, [fetchArticles])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  const handleStar = async (id) => {
    try {
      const { data } = await axios.patch(`/api/articles/${id}/star`)
      setArticles((prev) =>
        prev.map((a) => (a.id === id ? { ...a, is_starred: data.is_starred } : a))
      )
      fetchStats()
    } catch (err) {
      console.error('Failed to toggle star:', err)
    }
  }

  const handleCrawl = async () => {
    setCrawling(true)
    try {
      await axios.post('/api/crawl')
      await Promise.all([fetchArticles(), fetchStats()])
    } catch (err) {
      console.error('Crawl failed:', err)
    } finally {
      setCrawling(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* ── Header ── */}
      <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2 shrink-0">
            <Newspaper className="text-blue-400" size={22} />
            <span className="text-lg font-bold tracking-tight text-white">TechNews Daily</span>
          </div>

          {/* Stats */}
          <div className="hidden sm:flex items-center gap-4 text-sm text-gray-400">
            <StatBadge label="Today" value={stats.today} color="text-blue-400" />
            <StatBadge label="Total" value={stats.total} color="text-gray-200" />
            <StatBadge label="Starred" value={stats.starred} color="text-yellow-400" icon={<Star size={12} fill="currentColor" />} />
          </div>

          {/* Crawl button */}
          <button
            onClick={handleCrawl}
            disabled={crawling}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900
                       text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors shrink-0"
          >
            <RefreshCw size={14} className={crawling ? 'animate-spin' : ''} />
            {crawling ? 'Crawling…' : 'Refresh'}
          </button>
        </div>

        {/* View tabs */}
        <nav className="max-w-7xl mx-auto px-4 flex gap-0 border-t border-gray-800">
          {VIEWS.map((v) => (
            <button
              key={v.id}
              onClick={() => setView(v.id)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                view === v.id
                  ? 'border-blue-400 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              {v.id === 'favorites' && <Star size={13} fill={view === 'favorites' ? 'currentColor' : 'none'} />}
              {v.id === 'today' && <Zap size={13} />}
              {v.label}
            </button>
          ))}
        </nav>
      </header>

      {/* ── Filters ── */}
      <div className="max-w-7xl mx-auto px-4 py-4 flex flex-wrap items-center gap-3 border-b border-gray-800/50">
        <CategoryFilter categories={CATEGORIES} selected={category} onChange={setCategory} />
        {view === 'history' && (
          <DateFilter selectedDate={selectedDate} onChange={setSelectedDate} />
        )}
      </div>

      {/* ── Main content ── */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-400" />
          </div>
        ) : articles.length === 0 ? (
          <EmptyState view={view} onCrawl={handleCrawl} crawling={crawling} />
        ) : (
          <>
            <p className="text-xs text-gray-600 mb-4">{articles.length} articles</p>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {articles.map((article) => (
                <ArticleCard key={article.id} article={article} onStar={handleStar} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  )
}

function StatBadge({ label, value, color, icon }) {
  return (
    <span className="flex items-center gap-1">
      {icon && <span className={color}>{icon}</span>}
      <span>{label}:</span>
      <span className={`font-semibold ${color}`}>{value}</span>
    </span>
  )
}

function EmptyState({ view, onCrawl, crawling }) {
  const messages = {
    today: "No articles for today yet.",
    history: "No articles found for this date.",
    favorites: "You haven't starred any articles yet.",
  }
  return (
    <div className="flex flex-col items-center justify-center h-64 text-gray-500 gap-4">
      <Newspaper size={48} className="opacity-20" />
      <p>{messages[view]}</p>
      {view !== 'favorites' && (
        <button
          onClick={onCrawl}
          disabled={crawling}
          className="text-sm text-blue-400 hover:text-blue-300 underline underline-offset-2 transition-colors"
        >
          {crawling ? 'Crawling…' : 'Click to crawl now'}
        </button>
      )}
    </div>
  )
}
