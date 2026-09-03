import { useEffect, useState } from 'react'
import { Award, Download } from 'lucide-react'
import { certificatesApi } from '../services/resources'
import { Card, Badge } from '../components/ui'
import { EmptyState, LoadingPage } from '../components/form'
import { useToast } from '../context/ToastContext'

export default function EmployeeCertificates() {
  const [certs, setCerts] = useState(null)
  const [downloading, setDownloading] = useState(null)
  const toast = useToast()

  useEffect(() => {
    certificatesApi.list().then((r) => setCerts(r.data))
  }, [])

  if (certs === null) return <LoadingPage />

  const download = async (certificate) => {
    setDownloading(certificate.id)
    try {
      const response = await certificatesApi.download(certificate.id)
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = `${certificate.certificate_id}.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not download certificate')
    } finally { setDownloading(null) }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-2xl text-ink-900">My Certificates</h1>
        <p className="text-sm text-ink-400 mt-0.5">Certificates you've earned for reaching learning targets</p>
      </div>

      {certs.length === 0 ? (
        <Card><EmptyState icon={Award} title="No certificates yet" message="Keep learning — your certificate will appear here once you reach your target." /></Card>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {certs.map((c) => (
            <Card key={c.id} className="p-5">
              <div className="h-28 rounded-lg border border-gold-200 bg-gradient-to-br from-ink-900 to-ink-700 p-4 mb-4 text-white relative overflow-hidden">
                <div className="absolute right-4 top-4 w-10 h-10 rounded-full bg-gold-500 text-ink-900 flex items-center justify-center font-display font-bold text-xs">LD</div>
                <p className="text-[10px] uppercase tracking-widest text-gold-400">CertifyLD</p>
                <p className="font-display text-lg mt-3">Certificate of Achievement</p>
                <p className="text-[10px] text-white/60 mt-1">Issued in your name</p>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div>
                  <p className="font-mono text-sm text-ink-800">{c.certificate_id}</p>
                  <p className="text-xs text-ink-400">Issued {c.issue_date}</p>
                </div>
              </div>
              <p className="text-sm text-ink-600 mb-4">{c.achievement_type === 'COURSE_COMPLETION' ? 'Course completed successfully.' : `${c.achieved_hours}h completed, exceeding your ${c.target_hours}h target.`}</p>
              <div className="flex items-center justify-between">
                <Badge tone={c.email_sent ? 'success' : 'warning'}>{c.email_sent ? 'Emailed' : 'Email Pending'}</Badge>
                <button
                  type="button"
                  onClick={() => download(c)}
                  disabled={downloading === c.id}
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-700 hover:text-gold-600"
                >
                  <Download size={15} /> {downloading === c.id ? 'Downloading...' : 'Download'}
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
