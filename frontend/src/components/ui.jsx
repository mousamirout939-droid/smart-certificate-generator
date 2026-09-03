export function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-xl border border-ink-100 shadow-card ${className}`}>
      {children}
    </div>
  )
}

export function StatCard({ label, value, icon: Icon, accent = 'ink' }) {
  const accents = {
    ink: 'bg-ink-50 text-ink-700',
    gold: 'bg-gold-50 text-gold-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    rose: 'bg-rose-50 text-rose-600',
  }
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-ink-400 uppercase tracking-wide">{label}</p>
          <p className="text-2xl font-display font-semibold text-ink-900 mt-1.5">{value}</p>
        </div>
        {Icon && (
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${accents[accent]}`}>
            <Icon size={18} />
          </div>
        )}
      </div>
    </Card>
  )
}

export function Badge({ children, tone = 'default' }) {
  const tones = {
    default: 'bg-ink-100 text-ink-600',
    success: 'bg-emerald-50 text-emerald-700',
    warning: 'bg-amber-50 text-amber-700',
    danger: 'bg-rose-50 text-rose-700',
    gold: 'bg-gold-50 text-gold-600',
  }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  )
}

export function ProgressBar({ value, max = 100, tone = 'gold' }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const tones = {
    gold: 'bg-gold-500',
    emerald: 'bg-emerald-500',
  }
  return (
    <div className="w-full h-2 bg-ink-100 rounded-full overflow-hidden">
      <div
        className={`h-full ${tones[tone]} rounded-full transition-all duration-500`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
