import { useEffect, useState } from 'react'
import { Award, Download, Sparkles } from 'lucide-react'
import { dashboardApi, certificatesApi } from '../services/resources'
import { Card, ProgressBar } from '../components/ui'
import { Button, LoadingPage } from '../components/form'

export default function EmployeeDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    dashboardApi.get().then((r) => setData(r.data))
  }, [])

  if (!data) return <LoadingPage />

  const { employee, progress_percentage, remaining_hours, is_eligible, certificate } = data

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1 className="font-display text-2xl text-ink-900">Welcome back, {employee.full_name.split(' ')[0]}</h1>
        <p className="text-sm text-ink-400 mt-0.5">{employee.employee_code} · {employee.department || 'Unassigned'}</p>
      </div>

      {is_eligible && (
        <Card className="p-6 mb-6 bg-gradient-to-br from-ink-900 to-ink-700 border-none text-white relative overflow-hidden">
          <div
            className="absolute inset-0 opacity-10"
            style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #b8860b 1px, transparent 0)', backgroundSize: '24px 24px' }}
          />
          <div className="relative flex items-center gap-2 text-gold-500 mb-2">
            <Sparkles size={18} />
            <span className="text-sm font-medium">Target achieved</span>
          </div>
          <p className="relative font-display text-xl mb-4">🎉 Congratulations! You have achieved your learning target.</p>
          {certificate && (
            <div className="relative flex items-center justify-between bg-white/10 rounded-lg px-4 py-3">
              <div>
                <p className="text-xs text-white/60">Certificate ID</p>
                <p className="font-mono text-sm">{certificate.certificate_id}</p>
                <p className="text-xs text-white/60 mt-1">Issued {certificate.issue_date}</p>
              </div>
              <a href={certificatesApi.downloadUrl(certificate.id)} target="_blank" rel="noreferrer">
                <Button variant="gold"><Download size={16} /> Download Certificate</Button>
              </a>
            </div>
          )}
        </Card>
      )}

      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium text-ink-800">Learning progress</h3>
          <span className="text-sm text-ink-400">{employee.total_learning_hours}h / {employee.target_hours}h</span>
        </div>
        <ProgressBar value={employee.total_learning_hours} max={employee.target_hours} />
        <div className="flex items-center justify-between mt-3 text-sm">
          <span className="text-ink-400">{progress_percentage}% complete</span>
          {!is_eligible && <span className="text-ink-400">{remaining_hours}h remaining to reach your target</span>}
        </div>
      </Card>
    </div>
  )
}
