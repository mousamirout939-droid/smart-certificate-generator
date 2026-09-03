import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, BookOpen, GraduationCap, Award, Settings as SettingsIcon,
  LogOut, User, Menu, X,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

const adminNav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/employees', label: 'Employees', icon: Users },
  { to: '/courses', label: 'Courses', icon: BookOpen },
  { to: '/learning', label: 'Learning Records', icon: GraduationCap },
  { to: '/certificates', label: 'Certificates', icon: Award },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
]

const employeeNav = [
  { to: '/employee/dashboard', label: 'My Dashboard', icon: LayoutDashboard },
  { to: '/employee/courses', label: 'Course Catalog', icon: BookOpen },
  { to: '/employee/certificates', label: 'My Certificates', icon: Award },
  { to: '/profile', label: 'Profile', icon: User },
]

export default function AppLayout() {
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()
  const nav = user?.role === 'admin' ? adminNav : employeeNav

  return (
    <div className="min-h-screen bg-ink-50 flex">
      {/* Sidebar */}
      <aside
        className={`fixed lg:static z-40 inset-y-0 left-0 w-64 bg-ink-900 text-ink-100 transform transition-transform duration-200 ease-out
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 flex flex-col`}
      >
        <div className="h-16 flex items-center gap-2.5 px-6 border-b border-white/10">
          <div className="w-8 h-8 rounded-full border-2 border-gold-500 flex items-center justify-center">
            <Award size={16} className="text-gold-500" />
          </div>
          <span className="font-display text-lg tracking-tight">CertifyLD</span>
        </div>

        <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto scrollbar-thin">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-white/10 text-white font-medium'
                    : 'text-ink-100/70 hover:text-white hover:bg-white/5'
                }`
              }
            >
              <Icon size={17} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-white/10">
          <div className="px-3 py-2 mb-1">
            <p className="text-sm text-white truncate">{user?.email}</p>
            <p className="text-xs text-ink-100/50 capitalize">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-ink-100/70 hover:text-white hover:bg-white/5 transition-colors"
          >
            <LogOut size={17} />
            Log out
          </button>
        </div>
      </aside>

      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-ink-100 flex items-center px-4 lg:px-8 sticky top-0 z-20">
          <button className="lg:hidden mr-3 text-ink-700" onClick={() => setMobileOpen(true)}>
            <Menu size={22} />
          </button>
          <div className="flex-1" />
          <button
            onClick={() => navigate(user?.role === 'admin' ? '/dashboard' : '/profile')}
            className="flex items-center gap-2 text-sm text-ink-700 hover:text-ink-900"
          >
            <div className="w-8 h-8 rounded-full bg-gold-50 text-gold-600 flex items-center justify-center font-medium text-xs">
              {user?.email?.[0]?.toUpperCase()}
            </div>
          </button>
        </header>
        <main className="flex-1 p-4 lg:p-8 max-w-[1400px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
