import { useEffect, useState } from 'react'
import { Search, Award, Download, Send } from 'lucide-react'
import { certificatesApi } from '../services/resources'
import { Card, Badge } from '../components/ui'
import { Button, Input, EmptyState, LoadingPage } from '../components/form'
import { useToast } from '../context/ToastContext'

export default function Certificates() {
  const [certs, setCerts] = useState(null)
  const [search, setSearch] = useState('')
  const toast = useToast()

  const load = () => certificatesApi.list({ certificate_id: search || undefined }).then((r) => setCerts(r.data))

  useEffect(() => { load() }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    load()
  }

  const handleResend = async (id) => {
    try {
      await certificatesApi.resend(id)
      toast.success('Resend attempted')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to resend')
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-2xl text-ink-900">Certificates</h1>
        <p className="text-sm text-ink-400 mt-0.5">All issued certificates across the organization</p>
      </div>

      <form onSubmit={handleSearch} className="mb-4 flex gap-2 max-w-md">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
          <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search certificate ID…" className="pl-9" />
        </div>
        <Button variant="outline" type="submit">Search</Button>
      </form>

      <Card>
        {certs === null ? (
          <LoadingPage />
        ) : certs.length === 0 ? (
          <EmptyState icon={Award} title="No certificates found" message="Certificates will appear here once employees reach their learning targets." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink-100 text-left text-xs text-ink-400 uppercase tracking-wide">
                <th className="px-5 py-3 font-medium">Certificate ID</th>
                <th className="px-5 py-3 font-medium">Employee ID</th>
                <th className="px-5 py-3 font-medium">Hours</th>
                <th className="px-5 py-3 font-medium">Issue Date</th>
                <th className="px-5 py-3 font-medium">Email</th>
                <th className="px-5 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {certs.map((c) => (
                <tr key={c.id} className="border-b border-ink-100/60 last:border-0 hover:bg-ink-50/50">
                  <td className="px-5 py-3.5 font-mono text-ink-700">{c.certificate_id}</td>
                  <td className="px-5 py-3.5 text-ink-600">#{c.employee_id}</td>
                  <td className="px-5 py-3.5 text-ink-600">{c.achieved_hours}h / {c.target_hours}h</td>
                  <td className="px-5 py-3.5 text-ink-400">{c.issue_date}</td>
                  <td className="px-5 py-3.5">
                    <Badge tone={c.email_sent ? 'success' : 'warning'}>{c.email_sent ? 'Sent' : 'Pending'}</Badge>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-end gap-3">
                      {!c.email_sent && (
                        <button onClick={() => handleResend(c.id)} title="Resend email" className="text-ink-400 hover:text-ink-700">
                          <Send size={15} />
                        </button>
                      )}
                      <a href={certificatesApi.downloadUrl(c.id)} target="_blank" rel="noreferrer" title="Download" className="text-ink-400 hover:text-ink-700">
                        <Download size={15} />
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
