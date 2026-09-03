import { useEffect, useState } from 'react'
import { CheckCircle2, ShieldCheck, XCircle } from 'lucide-react'
import { useParams } from 'react-router-dom'
import api from '../services/api'

export default function CertificateVerify() {
  const { certificateId } = useParams()
  const [result, setResult] = useState(null)
  useEffect(() => { api.get(`/api/certificates/verify/${certificateId}`).then((response) => setResult(response.data)).catch(() => setResult({ valid: false })) }, [certificateId])

  return (
    <main className="min-h-screen bg-cream flex items-center justify-center p-6">
      <section className="bg-white border border-ink-100 rounded-xl shadow-card p-8 max-w-md w-full text-center">
        <ShieldCheck className="mx-auto text-gold-500" size={42} />
        <h1 className="font-display text-2xl text-ink-900 mt-4">Certificate verification</h1>
        {!result ? <p className="text-sm text-ink-400 mt-3">Checking certificate...</p> : result.valid ? <><CheckCircle2 className="mx-auto mt-5 text-emerald-600" size={30} /><p className="font-medium text-emerald-700 mt-2">Valid certificate</p><p className="text-ink-700 mt-4">{result.learner_name}</p><p className="text-sm text-ink-400 mt-1">{result.certificate_id}</p><p className="text-sm text-ink-400 mt-1">Issued {result.issue_date}</p></> : <><XCircle className="mx-auto mt-5 text-rose-600" size={30} /><p className="font-medium text-rose-700 mt-2">Certificate not found</p></>}
      </section>
    </main>
  )
}