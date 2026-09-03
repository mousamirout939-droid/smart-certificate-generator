import { useEffect, useState } from 'react'
import { Plus, GraduationCap } from 'lucide-react'
import { learningApi, employeesApi, coursesApi } from '../services/resources'
import { Card, Badge } from '../components/ui'
import { Button, Input, Field, Select, EmptyState, LoadingPage } from '../components/form'
import { Modal } from '../components/Modal'
import { useToast } from '../context/ToastContext'

export default function LearningRecords() {
  const [records, setRecords] = useState(null)
  const [employees, setEmployees] = useState([])
  const [courses, setCourses] = useState([])
  const [showAdd, setShowAdd] = useState(false)
  const toast = useToast()

  const load = async () => {
    const [r, e, c] = await Promise.all([
      learningApi.list(),
      employeesApi.list({ page_size: 100 }),
      coursesApi.list(),
    ])
    setRecords(r.data)
    setEmployees(e.data.items)
    setCourses(c.data)
  }

  useEffect(() => { load() }, [])

  const employeeName = (id) => employees.find((e) => e.id === id)?.full_name || `#${id}`
  const courseName = (id) => courses.find((c) => c.id === id)?.title || `#${id}`

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl text-ink-900">Learning Records</h1>
          <p className="text-sm text-ink-400 mt-0.5">Log completed learning hours for employees</p>
        </div>
        <Button variant="gold" onClick={() => setShowAdd(true)}>
          <Plus size={16} /> Add Record
        </Button>
      </div>

      <Card>
        {records === null ? (
          <LoadingPage />
        ) : records.length === 0 ? (
          <EmptyState icon={GraduationCap} title="No learning records yet" message="Add the first learning record to start tracking progress." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink-100 text-left text-xs text-ink-400 uppercase tracking-wide">
                <th className="px-5 py-3 font-medium">Employee</th>
                <th className="px-5 py-3 font-medium">Course</th>
                <th className="px-5 py-3 font-medium">Hours</th>
                <th className="px-5 py-3 font-medium">Completion</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="border-b border-ink-100/60 last:border-0 hover:bg-ink-50/50">
                  <td className="px-5 py-3.5 text-ink-700">{employeeName(r.employee_id)}</td>
                  <td className="px-5 py-3.5 text-ink-600">{courseName(r.course_id)}</td>
                  <td className="px-5 py-3.5 text-ink-600">{r.learning_hours}h</td>
                  <td className="px-5 py-3.5 text-ink-600">{r.completion_percentage}%</td>
                  <td className="px-5 py-3.5"><Badge tone={r.status === 'completed' ? 'success' : 'default'}>{r.status}</Badge></td>
                  <td className="px-5 py-3.5 text-ink-400">{r.completion_date || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <AddRecordModal
        open={showAdd}
        onClose={() => setShowAdd(false)}
        onCreated={() => { setShowAdd(false); load() }}
        employees={employees}
        courses={courses}
      />
    </div>
  )
}

function AddRecordModal({ open, onClose, onCreated, employees, courses }) {
  const [form, setForm] = useState({ employee_id: '', course_id: '', learning_hours: '', completion_percentage: 100, completion_date: '' })
  const [saving, setSaving] = useState(false)
  const toast = useToast()

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await learningApi.create({
        employee_id: Number(form.employee_id),
        course_id: Number(form.course_id),
        learning_hours: Number(form.learning_hours),
        completion_percentage: Number(form.completion_percentage),
        completion_date: form.completion_date || null,
      })
      toast.success('Learning record added — progress recalculated')
      setForm({ employee_id: '', course_id: '', learning_hours: '', completion_percentage: 100, completion_date: '' })
      onCreated()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add learning record')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Add Learning Record">
      <form onSubmit={submit}>
        <Field label="Employee">
          <Select required value={form.employee_id} onChange={update('employee_id')}>
            <option value="">Select employee…</option>
            {employees.map((e) => <option key={e.id} value={e.id}>{e.full_name} ({e.employee_code})</option>)}
          </Select>
        </Field>
        <Field label="Course">
          <Select required value={form.course_id} onChange={update('course_id')}>
            <option value="">Select course…</option>
            {courses.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
          </Select>
        </Field>
        <div className="grid grid-cols-2 gap-x-4">
          <Field label="Learning hours"><Input type="number" min="0.5" step="0.5" required value={form.learning_hours} onChange={update('learning_hours')} /></Field>
          <Field label="Completion %"><Input type="number" min="0" max="100" required value={form.completion_percentage} onChange={update('completion_percentage')} /></Field>
        </div>
        <Field label="Completion date"><Input type="date" value={form.completion_date} onChange={update('completion_date')} /></Field>
        <div className="flex justify-end gap-3 mt-2">
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="gold" disabled={saving}>{saving ? 'Adding…' : 'Add Record'}</Button>
        </div>
      </form>
    </Modal>
  )
}
