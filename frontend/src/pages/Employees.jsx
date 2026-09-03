import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Plus, ChevronLeft, ChevronRight, UserX, Users as UsersIcon } from 'lucide-react'
import { employeesApi } from '../services/resources'
import { Card, Badge, ProgressBar } from '../components/ui'
import { Button, Input, Field, EmptyState, LoadingPage } from '../components/form'
import { Modal, ConfirmDialog } from '../components/Modal'
import { useToast } from '../context/ToastContext'

const PAGE_SIZE = 10

export default function Employees() {
  const [items, setItems] = useState(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [deactivateTarget, setDeactivateTarget] = useState(null)
  const toast = useToast()

  const load = () => {
    employeesApi.list({ search: search || undefined, page, page_size: PAGE_SIZE }).then((r) => {
      setItems(r.data.items)
      setTotal(r.data.total)
    })
  }

  useEffect(() => { load() }, [page])

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    load()
  }

  const handleDeactivate = async () => {
    try {
      await employeesApi.deactivate(deactivateTarget.id)
      toast.success(`${deactivateTarget.full_name} deactivated`)
      setDeactivateTarget(null)
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to deactivate employee')
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl text-ink-900">Employees</h1>
          <p className="text-sm text-ink-400 mt-0.5">{total} employees on record</p>
        </div>
        <Button variant="gold" onClick={() => setShowAdd(true)}>
          <Plus size={16} /> Add Employee
        </Button>
      </div>

      <form onSubmit={handleSearch} className="mb-4 flex gap-2 max-w-md">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search name, email, or code…"
            className="pl-9"
          />
        </div>
        <Button variant="outline" type="submit">Search</Button>
      </form>

      <Card>
        {items === null ? (
          <LoadingPage />
        ) : items.length === 0 ? (
          <EmptyState icon={UsersIcon} title="No employees found" message="Try a different search, or add your first employee." />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-ink-100 text-left text-xs text-ink-400 uppercase tracking-wide">
                    <th className="px-5 py-3 font-medium">Employee</th>
                    <th className="px-5 py-3 font-medium">Department</th>
                    <th className="px-5 py-3 font-medium">Progress</th>
                    <th className="px-5 py-3 font-medium">Status</th>
                    <th className="px-5 py-3 font-medium"></th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((emp) => {
                    const pct = Math.min(100, Math.round((emp.total_learning_hours / emp.target_hours) * 100))
                    return (
                      <tr key={emp.id} className="border-b border-ink-100/60 last:border-0 hover:bg-ink-50/50">
                        <td className="px-5 py-3.5">
                          <Link to={`/employees/${emp.id}`} className="font-medium text-ink-800 hover:text-gold-600">
                            {emp.full_name}
                          </Link>
                          <p className="text-xs text-ink-400">{emp.employee_code} · {emp.email}</p>
                        </td>
                        <td className="px-5 py-3.5 text-ink-600">{emp.department || '—'}</td>
                        <td className="px-5 py-3.5 w-44">
                          <div className="flex items-center gap-2">
                            <ProgressBar value={emp.total_learning_hours} max={emp.target_hours} />
                            <span className="text-xs text-ink-400 whitespace-nowrap">{pct}%</span>
                          </div>
                          <p className="text-xs text-ink-400 mt-1">{emp.total_learning_hours}h / {emp.target_hours}h</p>
                        </td>
                        <td className="px-5 py-3.5">
                          <Badge tone={emp.status === 'active' ? 'success' : 'default'}>{emp.status}</Badge>
                        </td>
                        <td className="px-5 py-3.5 text-right">
                          {emp.status === 'active' && (
                            <button
                              onClick={() => setDeactivateTarget(emp)}
                              className="text-ink-400 hover:text-rose-600"
                              title="Deactivate"
                            >
                              <UserX size={16} />
                            </button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between px-5 py-3 border-t border-ink-100 text-sm text-ink-400">
              <span>Page {page} of {totalPages}</span>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="p-1.5 rounded-lg border border-ink-100 disabled:opacity-40 hover:bg-ink-50"
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="p-1.5 rounded-lg border border-ink-100 disabled:opacity-40 hover:bg-ink-50"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </Card>

      <AddEmployeeModal open={showAdd} onClose={() => setShowAdd(false)} onCreated={() => { setShowAdd(false); load() }} />

      <ConfirmDialog
        open={!!deactivateTarget}
        onClose={() => setDeactivateTarget(null)}
        onConfirm={handleDeactivate}
        title="Deactivate employee?"
        message={`${deactivateTarget?.full_name} will no longer be able to log in or appear in active automation runs.`}
        confirmLabel="Deactivate"
        danger
      />
    </div>
  )
}

function AddEmployeeModal({ open, onClose, onCreated }) {
  const [form, setForm] = useState({
    employee_code: '', full_name: '', email: '', department: '', designation: '', target_hours: 50, password: '',
  })
  const [saving, setSaving] = useState(false)
  const toast = useToast()

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await employeesApi.create({ ...form, target_hours: Number(form.target_hours) })
      toast.success('Employee added')
      setForm({ employee_code: '', full_name: '', email: '', department: '', designation: '', target_hours: 50, password: '' })
      onCreated()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add employee')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Add Employee">
      <form onSubmit={submit}>
        <div className="grid grid-cols-2 gap-x-4">
          <Field label="Employee code"><Input required value={form.employee_code} onChange={update('employee_code')} placeholder="EMP-006" /></Field>
          <Field label="Full name"><Input required value={form.full_name} onChange={update('full_name')} /></Field>
        </div>
        <Field label="Email"><Input type="email" required value={form.email} onChange={update('email')} /></Field>
        <div className="grid grid-cols-2 gap-x-4">
          <Field label="Department"><Input value={form.department} onChange={update('department')} /></Field>
          <Field label="Designation"><Input value={form.designation} onChange={update('designation')} /></Field>
        </div>
        <div className="grid grid-cols-2 gap-x-4">
          <Field label="Target hours"><Input type="number" min="1" required value={form.target_hours} onChange={update('target_hours')} /></Field>
          <Field label="Initial password"><Input type="password" required minLength={6} value={form.password} onChange={update('password')} /></Field>
        </div>
        <div className="flex justify-end gap-3 mt-2">
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="gold" disabled={saving}>{saving ? 'Adding…' : 'Add Employee'}</Button>
        </div>
      </form>
    </Modal>
  )
}
