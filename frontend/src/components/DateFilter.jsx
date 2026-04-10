import { format, subDays } from 'date-fns'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const QUICK = [
  { label: 'Yesterday', days: 1 },
  { label: '3d ago', days: 3 },
  { label: '7d ago', days: 7 },
  { label: '30d ago', days: 30 },
]

export default function DateFilter({ selectedDate, onChange }) {
  const today = format(new Date(), 'yyyy-MM-dd')
  const minDate = format(subDays(new Date(), 30), 'yyyy-MM-dd')

  const shift = (n) => {
    const d = new Date(selectedDate + 'T00:00:00')
    d.setDate(d.getDate() + n)
    const next = format(d, 'yyyy-MM-dd')
    if (next >= minDate && next <= today) onChange(next)
  }

  return (
    <div className="flex flex-wrap items-center gap-2 ml-auto">
      <span className="text-sm text-gray-500">Date:</span>

      <button onClick={() => shift(-1)} className="p-1 text-gray-500 hover:text-gray-200 transition-colors">
        <ChevronLeft size={16} />
      </button>

      <input
        type="date"
        value={selectedDate}
        min={minDate}
        max={today}
        onChange={(e) => onChange(e.target.value)}
        className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-2 py-1
                   focus:outline-none focus:border-blue-500 transition-colors"
      />

      <button
        onClick={() => shift(1)}
        disabled={selectedDate >= today}
        className="p-1 text-gray-500 hover:text-gray-200 disabled:opacity-30 transition-colors"
      >
        <ChevronRight size={16} />
      </button>

      <div className="flex gap-1 border-l border-gray-700 pl-2 ml-1">
        {QUICK.map((q) => {
          const qDate = format(subDays(new Date(), q.days), 'yyyy-MM-dd')
          return (
            <button
              key={q.label}
              onClick={() => onChange(qDate)}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                selectedDate === qDate
                  ? 'bg-blue-700 text-blue-100'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
              }`}
            >
              {q.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
