const ACTIVE_STYLES = {
  All:        'bg-gray-600 text-white',
  AI:         'bg-purple-700 text-purple-100',
  WebDev:     'bg-blue-700 text-blue-100',
  SpringBoot: 'bg-green-700 text-green-100',
  AWS:        'bg-orange-700 text-orange-100',
  Azure:      'bg-sky-700 text-sky-100',
  DevOps:     'bg-slate-600 text-slate-100',
  General:    'bg-gray-700 text-gray-200',
}

const CATEGORY_LABELS = {
  SpringBoot: 'Spring / Java',
}

export default function CategoryFilter({ categories, selected, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onChange(cat)}
          className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
            selected === cat
              ? ACTIVE_STYLES[cat] || 'bg-gray-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
          }`}
        >
          {CATEGORY_LABELS[cat] || cat}
        </button>
      ))}
    </div>
  )
}
