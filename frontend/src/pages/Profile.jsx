import { useAuth } from '../context/AuthContext'
import { Card } from '../components/ui'
import { User } from 'lucide-react'

export default function Profile() {
  const { user } = useAuth()

  return (
    <div className="max-w-lg">
      <div className="mb-6">
        <h1 className="font-display text-2xl text-ink-900">Profile</h1>
        <p className="text-sm text-ink-400 mt-0.5">Your account details</p>
      </div>

      <Card className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-gold-50 text-gold-600 flex items-center justify-center">
            <User size={24} />
          </div>
          <div>
            <p className="font-medium text-ink-800">{user?.email}</p>
            <p className="text-sm text-ink-400 capitalize">{user?.role}</p>
          </div>
        </div>
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between border-t border-ink-100 pt-3">
            <dt className="text-ink-400">Account status</dt>
            <dd className="text-ink-700">{user?.is_active ? 'Active' : 'Inactive'}</dd>
          </div>
          <div className="flex justify-between border-t border-ink-100 pt-3">
            <dt className="text-ink-400">Role</dt>
            <dd className="text-ink-700 capitalize">{user?.role}</dd>
          </div>
        </dl>
      </Card>
    </div>
  )
}
