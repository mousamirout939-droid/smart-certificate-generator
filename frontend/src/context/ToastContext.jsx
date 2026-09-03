import { createContext, useContext, useState, useCallback } from 'react'
import { CheckCircle2, XCircle, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

let idCounter = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const remove = useCallback((id) => {
    setToasts((t) => t.filter((toast) => toast.id !== id))
  }, [])

  const push = useCallback((message, type = 'info') => {
    const id = ++idCounter
    setToasts((t) => [...t, { id, message, type }])
    setTimeout(() => remove(id), 4500)
  }, [remove])

  const toast = {
    success: (msg) => push(msg, 'success'),
    error: (msg) => push(msg, 'error'),
    info: (msg) => push(msg, 'info'),
  }

  const icons = {
    success: <CheckCircle2 size={18} className="text-emerald-600 flex-shrink-0" />,
    error: <XCircle size={18} className="text-rose-600 flex-shrink-0" />,
    info: <Info size={18} className="text-ink-600 flex-shrink-0" />,
  }

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 w-80">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="flex items-start gap-2 bg-white border border-ink-100 shadow-card rounded-lg px-4 py-3 text-sm text-ink-800 animate-[fadeIn_0.15s_ease-out]"
          >
            {icons[t.type]}
            <span className="flex-1">{t.message}</span>
            <button onClick={() => remove(t.id)} className="text-ink-400 hover:text-ink-700">
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
