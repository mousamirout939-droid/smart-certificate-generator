import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Award, Download, Send, Sparkles } from 'lucide-react'
import { employeesApi, learningApi, certificatesApi } from '../services/resources'
import { Card, Badge, ProgressBar } from '../components/ui'
import { Button, LoadingPage } from '../components/form'
import { useToast } from '../context/ToastContext'

export default function EmployeeDetail() {
  const { id } = useParams()
  const [progress, setProgress] = useState(null)
  const [records, setRecords] = useState([])
  const [certificates, setCertificates] = useState([])
  const [generating, setGenerating] = useState(false)
  const toast = useToast()

  const load = async () => {
    const [p, r, c] = await Promise.all([
      employeesApi.get(id),
      learningApi.byEmployee(id),
      certificatesApi.list({ employee_id: id }),
    ])
    setProgress(p.data)
    setRecords(r.data)
    setCertificates(c.data)
  }

  useEffect(() => { load() }, [id])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      await certificatesApi.generate(id)
      toast.success('Certificate generated')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate certificate')
    } finally {
      setGenerating(false)
    }
  }

  const handleResend = async (certId) => {
    try {
      await certificatesApi.resend(certId)
      toast.success('Email resend attempted')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to resend email')
    }
  }

  if (!progress) return <LoadingPage />

  const { employee, progress_percentage, remaining_hours, is_eligible } = progress
  const hasCertificate = certificates.length > 0

  return (
    <div>
      <Link to="/employees" className="inline-flex items-center gap-1.5 text-sm text-ink-400 hover:text-ink-700 mb-4">
        <ArrowLeft size={15} /> Back to employees
      </Link>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl text-ink-900">{employee.full_name}</h1>
          <p className="text-sm text-ink-400 mt-0.5">{employee.employee_code} · {employee.department || 'Unassigned'} · {employee.email}</p>
        </div>
        <Badge tone={employee.status === 'active' ? 'success' : 'default'}>{employee.status}</Badge>
      </div>

      <div className="grid lg:grid-cols-3 gap-4 mb-6">
        <Card className="p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-ink-800">Learning progress</h3>
            <span className="text-sm text-ink-400">{employee.total_learning_hours}h of {employee.target_hours}h</span>
          </div>
          <ProgressBar value={employee.total_learning_hours} max={employee.target_hours} />
          <div className="flex items-center justify-between mt-3 text-sm">
            <span className="text-ink-400">{progress_percentage}% complete</span>
            <span className="text-ink-400">{remaining_hours > 0 ? `${remaining_hours}h remaining` : 'Target reached'}</span>
          </div>
        </Card>

        <Card className="p-5 flex flex-col justify-between">
          <div>
            <h3 className="font-medium text-ink-800 mb-2">Certificate eligibility</h3>
            {is_eligible ? (
              <div className="flex items-center gap-2 text-emerald-700 text-sm">
                <Sparkles size={16} /> Eligible for certificate
              </div>
            ) : (
              <p className="text-sm text-ink-400">Not yet eligible</p>
            )}
          </div>
          {is_eligible && !hasCertificate && (
            <Button variant="gold" onClick={handleGenerate} disabled={generating} className="mt-4 w-full">
              {generating ? 'Generating…' : 'Generate Certificate'}
            </Button>
          )}
        </Card>
      </div>

      {hasCertificate && (
        <Card className="p-5 mb-6">
          <h3 className="font-medium text-ink-800 mb-4">Certificates</h3>
          <div className="space-y-3">
            {certificates.map((c) => (
              <div key={c.id} className="flex items-center justify-between border border-ink-100 rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-gold-50 text-gold-600 flex items-center justify-center">
                    <Award size={16} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-ink-800 font-mono">{c.certificate_id}</p>
                    <p className="text-xs text-ink-400">Issued {c.issue_date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge tone={c.email_sent ? 'success' : 'warning'}>{c.email_sent ? 'Emailed' : 'Email Pending'}</Badge>
                  {!c.email_sent && (
                    <button onClick={() => handleResend(c.id)} title="Resend email" className="text-ink-400 hover:text-ink-700">
                      <Send size={16} />
                    </button>
                  )}
                  <a href={certificatesApi.downloadUrl(c.id)} target="_blank" rel="noreferrer" title="Download" className="text-ink-400 hover:text-ink-700">
                    <Download size={16} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card className="p-5">
        <h3 className="font-medium text-ink-800 mb-4">Learning records</h3>
        {records.length === 0 ? (
          <p className="text-sm text-ink-400">No learning records yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-ink-400 uppercase tracking-wide border-b border-ink-100">
                <th className="py-2 font-medium">Course ID</th>
                <th className="py-2 font-medium">Hours</th>
                <th className="py-2 font-medium">Completion</th>
                <th className="py-2 font-medium">Status</th>
                <th className="py-2 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="border-b border-ink-100/60 last:border-0">
                  <td className="py-2.5 text-ink-600">#{r.course_id}</td>
                  <td className="py-2.5 text-ink-600">{r.learning_hours}h</td>
                  <td className="py-2.5 text-ink-600">{r.completion_percentage}%</td>
                  <td className="py-2.5"><Badge tone={r.status === 'completed' ? 'success' : 'default'}>{r.status}</Badge></td>
                  <td className="py-2.5 text-ink-400">{r.completion_date || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
