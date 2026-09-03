import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, CheckCircle2, LockKeyhole, ArrowRight } from 'lucide-react'
import { coursesApi } from '../services/resources'
import { Card, Badge, ProgressBar } from '../components/ui'
import { Button, LoadingPage } from '../components/form'
import { useToast } from '../context/ToastContext'

export default function EmployeeCourses() {
  const [courses, setCourses] = useState(null)
  const [enrollments, setEnrollments] = useState([])
  const toast = useToast()
  const navigate = useNavigate()

  const load = async () => {
    const [courseResponse, enrollmentResponse] = await Promise.all([
      coursesApi.list(), coursesApi.myEnrollments(),
    ])
    setCourses(courseResponse.data.filter((course) => course.is_active))
    setEnrollments(enrollmentResponse.data)
  }

  useEffect(() => { load().catch(() => toast.error('Could not load the course catalog')) }, [])

  const enrollmentFor = (courseId) => enrollments.find((item) => item.course_id === courseId)

  const enroll = async (course) => {
    try {
      const response = await coursesApi.enroll(course.id)
      if (response.data.checkout_required) {
        toast.info('This course is paid. Payment checkout is not configured yet.')
      } else {
        toast.success(`You are enrolled in ${course.title}`)
        load()
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not enroll in this course')
    }
  }

  if (!courses) return <LoadingPage />

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-2xl text-ink-900">Choose your next course</h1>
        <p className="text-sm text-ink-400 mt-0.5">Learn at your pace. Complete enough learning to earn your certificate.</p>
      </div>
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {courses.map((course) => {
          const enrollment = enrollmentFor(course.id)
          return (
            <Card key={course.id} className="p-5 flex flex-col">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-mono text-ink-400">{course.course_code}</p>
                  <h2 className="font-medium text-ink-800 mt-1">{course.title}</h2>
                </div>
                {course.price > 0 ? <LockKeyhole size={17} className="text-gold-600" /> : <BookOpen size={17} className="text-ink-400" />}
              </div>
              <p className="text-sm text-ink-400 mt-3 line-clamp-3 flex-1">{course.description || 'Build practical skills with this guided learning course.'}</p>
              <div className="flex items-center gap-2 mt-4">
                {course.category && <Badge>{course.category}</Badge>}
                <Badge tone="gold">{course.duration_hours}h</Badge>
                <Badge tone={course.price > 0 ? 'default' : 'success'}>{course.price > 0 ? `$${course.price.toFixed(2)}` : 'Free'}</Badge>
              </div>
              {enrollment ? (
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-ink-400 mb-1"><span>{enrollment.status === 'completed' ? 'Completed' : 'Enrolled'}</span><span>{enrollment.payment_status}</span></div>
                  <ProgressBar value={enrollment.status === 'completed' ? 100 : 5} max={100} />
                  {enrollment.status !== 'completed' && <Button className="w-full mt-3" variant="outline" onClick={() => navigate(`/employee/courses/${course.id}`)}>Continue course <ArrowRight size={15} /></Button>}
                  {enrollment.status === 'completed' && <p className="text-xs text-emerald-700 mt-3 flex items-center gap-1"><CheckCircle2 size={14} /> Course complete. Keep learning toward your certificate.</p>}
                </div>
              ) : (
                <Button className="w-full mt-4" variant={course.price > 0 ? 'outline' : 'gold'} onClick={() => enroll(course)}>{course.price > 0 ? 'Purchase access' : 'Enroll for free'}</Button>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
