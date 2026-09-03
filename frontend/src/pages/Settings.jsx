import { useEffect, useState } from 'react'
import { settingsApi, automationApi } from '../services/resources'
import { Card, Badge } from '../components/ui'
import { Button, Input, Field, LoadingPage } from '../components/form'
import { useToast } from '../context/ToastContext'

export default function Settings() {
  const [settings, setSettings] = useState(null)
  const [status, setStatus] = useState(null)
  const [saving, setSaving] = useState(false)
  const toast = useToast()

  const load = async () => {
    const [s, st] = await Promise.all([settingsApi.get(), automationApi.status()])
    setSettings(s.data)
    setStatus(st.data)
  }

  useEffect(() => { load() }, [])

  const update = (field) => (e) => setSettings((s) => ({ ...s, [field]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const res = await settingsApi.update({
        certificate_target_hours: Number(settings.certificate_target_hours),
        automation_interval_minutes: Number(settings.automation_interval_minutes),
        organization_name: settings.organization_name,
        certificate_signature_name: settings.certificate_signature_name,
      })
      setSettings(res.data)
      toast.success('Settings saved')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  if (!settings || !status) return <LoadingPage />

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h1 className="font-display text-2xl text-ink-900">Settings</h1>
        <p className="text-sm text-ink-400 mt-0.5">Configure certificate targets, automation, and branding</p>
      </div>

      <Card className="p-5 mb-4">
        <h3 className="font-medium text-ink-800 mb-3">Automation status</h3>
        <div className="flex items-center gap-3 text-sm">
          <Badge tone={status.enabled ? 'success' : 'default'}>{status.enabled ? 'Enabled' : 'Disabled'}</Badge>
          <span className="text-ink-400">Runs every {status.interval_minutes} minutes</span>
        </div>
        {status.last_run_at && (
          <p className="text-xs text-ink-400 mt-2">Last run: {new Date(status.last_run_at).toLocaleString()} — {status.last_run_summary}</p>
        )}
        <div className="mt-3">
          <Badge tone={settings.smtp_configured ? 'success' : 'warning'}>
            {settings.smtp_configured ? 'Email delivery configured' : 'Email delivery not configured'}
          </Badge>
        </div>
      </Card>

      <Card className="p-5">
        <form onSubmit={submit}>
          <Field label="Default certificate target hours">
            <Input type="number" min="1" value={settings.certificate_target_hours} onChange={update('certificate_target_hours')} />
          </Field>
          <Field label="Automation interval (minutes)">
            <Input type="number" min="1" value={settings.automation_interval_minutes} onChange={update('automation_interval_minutes')} />
          </Field>
          <Field label="Organization name">
            <Input value={settings.organization_name} onChange={update('organization_name')} />
          </Field>
          <Field label="Certificate signature name">
            <Input value={settings.certificate_signature_name} onChange={update('certificate_signature_name')} />
          </Field>
          <Button type="submit" variant="gold" disabled={saving}>{saving ? 'Saving…' : 'Save Settings'}</Button>
        </form>
      </Card>
    </div>
  )
}
