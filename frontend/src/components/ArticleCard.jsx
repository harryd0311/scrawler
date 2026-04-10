import { Star, ExternalLink } from 'lucide-react'

const BADGE = {
  AI:         'bg-purple-950 text-purple-300 border-purple-700',
  WebDev:     'bg-blue-950 text-blue-300 border-blue-700',
  SpringBoot: 'bg-green-950 text-green-300 border-green-700',
  AWS:        'bg-orange-950 text-orange-300 border-orange-700',
  Azure:      'bg-sky-950 text-sky-300 border-sky-700',
  DevOps:     'bg-slate-800 text-slate-300 border-slate-600',
  General:    'bg-gray-800 text-gray-400 border-gray-600',
}

const CATEGORY_LABELS = {
  SpringBoot: 'Spring/Java',
}

export default function ArticleCard({ article, onStar }) {
  const badge = BADGE[article.category] || BADGE.General

  return (
    <article className="flex flex-col gap-3 bg-gray-900 border border-gray-800 rounded-xl p-4
                        hover:border-gray-700 transition-colors">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${badge}`}>
          {CATEGORY_LABELS[article.category] || article.category}
        </span>
        <button
          onClick={() => onStar(article.id)}
          title={article.is_starred ? 'Remove from favorites' : 'Add to favorites'}
          className={`p-1 rounded transition-colors ${
            article.is_starred
              ? 'text-yellow-400 hover:text-yellow-300'
              : 'text-gray-600 hover:text-gray-300'
          }`}
        >
          <Star size={16} fill={article.is_starred ? 'currentColor' : 'none'} />
        </button>
      </div>

      {/* Title */}
      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-white font-semibold leading-snug hover:text-blue-400 transition-colors"
        style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}
      >
        {article.title}
      </a>

      {/* Summary */}
      {article.summary && (
        <p
          className="text-gray-400 text-sm leading-relaxed"
          style={{ display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}
        >
          {article.summary}
        </p>
      )}

      {/* Footer */}
      <div className="mt-auto flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-1.5 min-w-0">
          <span className="text-gray-400 font-medium truncate">{article.source}</span>
          <span>·</span>
          <span className="shrink-0">{article.published_date}</span>
          {article.score > 0 && (
            <>
              <span>·</span>
              <span className="text-emerald-500 shrink-0">▲ {article.score}</span>
            </>
          )}
        </div>
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 shrink-0 text-gray-600 hover:text-gray-300 transition-colors"
        >
          <ExternalLink size={13} />
        </a>
      </div>
    </article>
  )
}
