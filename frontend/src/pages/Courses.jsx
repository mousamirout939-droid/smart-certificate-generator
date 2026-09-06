import { useEffect, useState } from 'react'
import { Plus, Search, BookOpen, Trash2 } from 'lucide-react'
import { coursesApi } from '../services/resources'
import { Card, Badge } from '../components/ui'
import { Button, Input, Select, Field, EmptyState, LoadingPage } from '../components/form'
import { Modal, ConfirmDialog } from '../components/Modal'
import { useToast } from '../context/ToastContext'

export default function Courses() {
  const [courses, setCourses] = useState(null)
  const [search, setSearch] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [deactivateTarget, setDeactivateTarget] = useState(null)
  const toast = useToast()

  const load = () => coursesApi.list({ search: search || undefined }).then((r) => setCourses(r.data))

  useEffect(() => { load() }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    load()
  }

  const handleDeactivate = async () => {
    try {
      await coursesApi.deactivate(deactivateTarget.id)
      toast.success(`${deactivateTarget.title} deactivated`)
      setDeactivateTarget(null)
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to deactivate course')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl text-ink-900">Courses</h1>
          <p className="text-sm text-ink-400 mt-0.5">Manage the course catalog</p>
        </div>
        <Button variant="gold" onClick={() => setShowAdd(true)}>
          <Plus size={16} /> Add Course
        </Button>
      </div>

      <form onSubmit={handleSearch} className="mb-4 flex gap-2 max-w-md">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
          <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search courses…" className="pl-9" />
        </div>
        <Button variant="outline" type="submit">Search</Button>
      </form>

      {courses === null ? (
        <LoadingPage />
      ) : courses.length === 0 ? (
        <Card><EmptyState icon={BookOpen} title="No courses found" message="Add your first course to get started." /></Card>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((c) => (
            <Card key={c.id} className="p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-mono text-ink-400">{c.course_code}</p>
                  <h3 className="font-medium text-ink-800 mt-0.5">{c.title}</h3>
                </div>
                {c.is_active && (
                  <button onClick={() => setDeactivateTarget(c)} className="text-ink-300 hover:text-rose-600">
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
              {c.description && <p className="text-sm text-ink-400 mt-2 line-clamp-2">{c.description}</p>}
              <div className="flex items-center gap-2 mt-4">
                {c.category && <Badge>{c.category}</Badge>}
                <Badge tone="gold">{c.duration_hours}h</Badge>
                <Badge tone={c.price > 0 ? 'default' : 'success'}>{c.price > 0 ? `$${c.price.toFixed(2)}` : 'Free'}</Badge>
                {!c.is_active && <Badge tone="default">Inactive</Badge>}
              </div>
            </Card>
          ))}
        </div>
      )}

      <AddCourseModal open={showAdd} onClose={() => setShowAdd(false)} onCreated={() => { setShowAdd(false); load() }} />

      <ConfirmDialog
        open={!!deactivateTarget}
        onClose={() => setDeactivateTarget(null)}
        onConfirm={handleDeactivate}
        title="Deactivate course?"
        message={`${deactivateTarget?.title} will no longer be available for new learning records.`}
        confirmLabel="Deactivate"
        danger
      />
    </div>
  )
}

function AddCourseModal({ open, onClose, onCreated }) {
  const [form, setForm] = useState({ course_code: '', title: '', category: '', description: '', duration_hours: 10, price: 0, payment_mode: 'not_required', quiz_questions: '' })
  const [saving, setSaving] = useState(false)
  const toast = useToast()

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      let quiz_questions = []
      if (form.quiz_questions.trim()) quiz_questions = JSON.parse(form.quiz_questions)
      await coursesApi.create({ ...form, duration_hours: Number(form.duration_hours), price: Number(form.price), quiz_questions })
      toast.success('Course added')
      setForm({ course_code: '', title: '', category: '', description: '', duration_hours: 10, price: 0, payment_mode: 'not_required', quiz_questions: '' })
      onCreated()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add course')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Add Course">
      <form onSubmit={submit}>
        <div className="grid grid-cols-2 gap-x-4">
          <Field label="Course code"><Input required value={form.course_code} onChange={update('course_code')} placeholder="CRS-009" /></Field>
          <Field label="Duration (hours)"><Input type="number" min="0" required value={form.duration_hours} onChange={update('duration_hours')} /></Field>
          <Field label="Price (USD, 0 = free)"><Input type="number" min="0" step="0.01" required value={form.price} onChange={update('price')} /></Field>
          <Field label="Payment mode"><Select value={form.payment_mode} onChange={update('payment_mode')}><option value="not_required">Not required</option><option value="online">Online</option><option value="offline">Offline</option></Select></Field>
        </div>
        <Field label="Title"><Input required value={form.title} onChange={update('title')} /></Field>
        <Field label="Category"><Input value={form.category} onChange={update('category')} placeholder="e.g. Technology" /></Field>
        <Field label="Description">
          <textarea
            value={form.description}
            onChange={update('description')}
            rows={3}
            className="w-full px-3 py-2 border border-ink-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gold-500/40 focus:border-gold-500"
          />
        </Field>
        <Field label="Quiz questions (JSON, minimum 5)">
          <textarea value={form.quiz_questions} onChange={update('quiz_questions')} rows={5} placeholder={'[{"id":"q1","question":"...","options":["A","B"],"correct_option":"A"}]'} className="w-full px-3 py-2 border border-ink-100 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/40 focus:border-gold-500" />
        </Field>
        <div className="flex justify-end gap-3 mt-2">
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="gold" disabled={saving}>{saving ? 'Adding…' : 'Add Course'}</Button>
        </div>
      </form>
    </Modal>
  )
}
