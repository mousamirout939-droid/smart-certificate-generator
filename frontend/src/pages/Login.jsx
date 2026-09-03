import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Award, ArrowRight } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { Input } from '../components/form'

export default function Login() {
  const [registering, setRegistering] = useState(false)
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, register, user } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const location = useLocation()

  if (user) {
    navigate(user.role === 'admin' ? '/dashboard' : '/employee/dashboard', { replace: true })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const me = registering
        ? await register({ full_name: fullName, email, password })
        : await login(email, password)
      const dest = location.state?.from?.pathname || (me.role === 'admin' ? '/dashboard' : '/employee/dashboard')
      navigate(dest, { replace: true })
    } catch (err) {
      toast.error(err.response?.data?.detail || (registering ? 'Could not create account' : 'Invalid email or password'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-ink-900">
      {/* Left: brand panel */}
      <div className="hidden lg:flex flex-1 flex-col justify-between p-14 relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, #b8860b 1px, transparent 0)',
            backgroundSize: '28px 28px',
          }}
        />
        <div className="relative flex items-center gap-3">
          <div className="w-10 h-10 rounded-full border-2 border-gold-500 flex items-center justify-center">
            <Award size={20} className="text-gold-500" />
          </div>
          <span className="font-display text-xl text-white tracking-tight">CertifyLD</span>
        </div>

        <div className="relative">
          <p className="font-display text-4xl text-white leading-tight max-w-md">
            Every learning hour, <span className="text-gold-500">accounted for.</span>
          </p>
          <p className="text-ink-100/60 mt-4 max-w-sm text-sm leading-relaxed">
            Track progress toward learning targets and issue verified certificates automatically,
            the moment they're earned.
          </p>
        </div>

        <p className="relative text-xs text-ink-100/40">Learning & Development Platform</p>
      </div>

      {/* Right: form */}
      <div className="flex-1 flex items-center justify-center bg-cream p-6">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-2.5 mb-8 justify-center">
            <Award size={22} className="text-gold-500" />
            <span className="font-display text-xl text-ink-900">CertifyLD</span>
          </div>

          <h1 className="font-display text-2xl text-ink-900 mb-1">{registering ? 'Start learning' : 'Welcome back'}</h1>
          <p className="text-sm text-ink-400 mb-8">{registering ? 'Create your learner account and choose a course.' : 'Sign in to continue to your dashboard.'}</p>

          <form onSubmit={handleSubmit}>
            {registering && <label className="block mb-4"><span className="block text-sm font-medium text-ink-700 mb-1.5">Full name</span><Input required value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Your name" /></label>}
            <label className="block mb-4">
              <span className="block text-sm font-medium text-ink-700 mb-1.5">Email</span>
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoFocus
              />
            </label>
            <label className="block mb-6">
              <span className="block text-sm font-medium text-ink-700 mb-1.5">Password</span>
              <Input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
              />
            </label>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-ink-900 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-ink-800 transition-colors disabled:opacity-60"
            >
              {loading ? (registering ? 'Creating account...' : 'Signing in...') : (registering ? 'Create learner account' : 'Sign in')}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <button type="button" onClick={() => setRegistering(!registering)} className="w-full mt-4 text-sm text-gold-700 hover:text-gold-800">
            {registering ? 'Already have an account? Sign in' : 'New here? Create a learner account'}
          </button>

          <div className="mt-8 p-4 bg-ink-50 rounded-lg text-xs text-ink-400 leading-relaxed">
            <p className="font-medium text-ink-600 mb-1">Demo credentials</p>
            Admin: admin@example.com<br />
            Employee: rahul.sharma@example.com<br />
            Password: Password123!
          </div>
        </div>
      </div>
    </div>
  )
}
