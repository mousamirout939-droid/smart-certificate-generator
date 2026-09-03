import { useEffect, useState } from 'react'
import { Users, Clock, Award, Mail, TrendingUp } from 'lucide-react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { dashboardApi, automationApi } from '../services/resources'
import { Card, StatCard, Badge } from '../components/ui'
import { Button } from '../components/form'
import { LoadingPage } from '../components/form'
import { useToast } from '../context/ToastContext'

const GOLD = '#b8860b'
const INK = '#232f4d'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [running, setRunning] = useState(false)
  const toast = useToast()

  const load = () => dashboardApi.get().then((r) => setData(r.data))

  useEffect(() => { load() }, [])

  const runAutomation = async () => {
    setRunning(true)
    try {
      const res = await automationApi.run()
      const { certificates_created, certificates_skipped_existing } = res.data
      toast.success(
        `Automation complete: ${certificates_created} certificate(s) created, ${certificates_skipped_existing} already existed.`
      )
      await load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Automation run failed')
    } finally {
      setRunning(false)
    }
  }

  if (!data) return <LoadingPage />

  const eligiblePie = [
    { name: 'Eligible', value: data.charts.eligible_vs_non_eligible.eligible },
    { name: 'Not yet eligible', value: data.charts.eligible_vs_non_eligible.non_eligible },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl text-ink-900">Dashboard</h1>
          <p className="text-sm text-ink-400 mt-0.5">Overview of learning progress and certifications</p>
        </div>
        <Button variant="gold" onClick={runAutomation} disabled={running}>
          {running ? 'Running…' : 'Run Automation Now'}
        </Button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <StatCard label="Total Employees" value={data.cards.total_employees} icon={Users} accent="ink" />
        <StatCard label="Total Learning Hours" value={data.cards.total_learning_hours} icon={Clock} accent="ink" />
        <StatCard label="Eligible" value={data.cards.employees_eligible} icon={TrendingUp} accent="emerald" />
        <StatCard label="Certificates Issued" value={data.cards.certificates_generated} icon={Award} accent="gold" />
        <StatCard label="Pending Email" value={data.cards.certificates_pending_email} icon={Mail} accent="rose" />
      </div>

      <div className="grid lg:grid-cols-5 gap-4 mb-6">
        <Card className="p-5 lg:col-span-3">
          <h3 className="font-medium text-ink-800 mb-4">Learning progress by employee</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.charts.learning_progress}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e3e8f0" />
              <XAxis dataKey="employee" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="hours" fill={GOLD} radius={[4, 4, 0, 0]} name="Hours completed" />
              <Bar dataKey="target" fill={INK} fillOpacity={0.15} radius={[4, 4, 0, 0]} name="Target" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-5 lg:col-span-2">
          <h3 className="font-medium text-ink-800 mb-4">Eligible vs. not yet eligible</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={eligiblePie} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                <Cell fill={GOLD} />
                <Cell fill="#e3e8f0" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <Card className="p-5">
          <h3 className="font-medium text-ink-800 mb-4">Newly eligible employees</h3>
          {data.recent_activity.newly_eligible.length === 0 ? (
            <p className="text-sm text-ink-400">No employees currently eligible.</p>
          ) : (
            <ul className="space-y-3">
              {data.recent_activity.newly_eligible.map((e) => (
                <li key={e.id} className="flex items-center justify-between text-sm">
                  <span className="text-ink-700">{e.name}</span>
                  <Badge tone="success">{e.hours}h / {e.target}h</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="p-5">
          <h3 className="font-medium text-ink-800 mb-4">Recently generated certificates</h3>
          {data.recent_activity.recent_certificates.length === 0 ? (
            <p className="text-sm text-ink-400">No certificates generated yet.</p>
          ) : (
            <ul className="space-y-3">
              {data.recent_activity.recent_certificates.map((c) => (
                <li key={c.certificate_id} className="flex items-center justify-between text-sm">
                  <span className="text-ink-700 font-mono text-xs">{c.certificate_id}</span>
                  <Badge tone={c.email_sent ? 'success' : 'warning'}>
                    {c.email_sent ? 'Emailed' : 'Email pending'}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  )
}
