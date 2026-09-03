export function Field({ label, children, error }) {
  return (
    <label className="block mb-4">
      <span className="block text-sm font-medium text-ink-700 mb-1.5">{label}</span>
      {children}
      {error && <span className="block text-xs text-rose-600 mt-1">{error}</span>}
    </label>
  )
}

export function Input(props) {
  return (
    <input
      {...props}
      className={`w-full px-3 py-2 border border-ink-100 rounded-lg text-sm text-ink-900 placeholder:text-ink-400
        focus:outline-none focus:ring-2 focus:ring-gold-500/40 focus:border-gold-500 transition-colors ${props.className || ''}`}
    />
  )
}

export function Select(props) {
  return (
    <select
      {...props}
      className={`w-full px-3 py-2 border border-ink-100 rounded-lg text-sm text-ink-900
        focus:outline-none focus:ring-2 focus:ring-gold-500/40 focus:border-gold-500 transition-colors bg-white ${props.className || ''}`}
    />
  )
}

export function Button({ children, variant = 'primary', className = '', ...props }) {
  const variants = {
    primary: 'bg-ink-800 text-white hover:bg-ink-900',
    gold: 'bg-gold-500 text-white hover:bg-gold-600',
    ghost: 'text-ink-600 hover:bg-ink-50',
    outline: 'border border-ink-100 text-ink-700 hover:bg-ink-50',
  }
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
        transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  )
}

export function EmptyState({ icon: Icon, title, message, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {Icon && (
        <div className="w-12 h-12 rounded-full bg-ink-50 flex items-center justify-center mb-4 text-ink-400">
          <Icon size={22} />
        </div>
      )}
      <p className="font-medium text-ink-800">{title}</p>
      {message && <p className="text-sm text-ink-400 mt-1 max-w-xs">{message}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export function Spinner({ className = '' }) {
  return <div className={`w-6 h-6 border-2 border-gold-500 border-t-transparent rounded-full animate-spin ${className}`} />
}

export function LoadingPage() {
  return (
    <div className="flex items-center justify-center py-24">
      <Spinner />
    </div>
  )
}
