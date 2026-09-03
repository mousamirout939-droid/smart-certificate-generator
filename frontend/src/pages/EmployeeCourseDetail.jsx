import { useEffect, useState } from 'react'
import { ArrowLeft, CheckCircle2, PlayCircle, ShieldCheck } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { coursesApi, certificatesApi } from '../services/resources'
import { Badge, Card, ProgressBar } from '../components/ui'
import { Button, LoadingPage } from '../components/form'
import { useToast } from '../context/ToastContext'

export default function EmployeeCourseDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [course, setCourse] = useState(null)
  const [enrollment, setEnrollment] = useState(null)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    const [courseResponse, enrollmentResponse] = await Promise.all([coursesApi.get(id), coursesApi.myEnrollments()])
    setCourse(courseResponse.data)
    setEnrollment(enrollmentResponse.data.find((item) => item.course_id === Number(id)))
  }
  useEffect(() => { load().catch((err) => toast.error(err.response?.data?.detail || 'Could not load this course')) }, [id])

  const markWatched = async (videoId) => {
    try { await coursesApi.markVideoWatched(id, videoId); await load() } catch (err) { toast.error(err.response?.data?.detail || 'Could not save lesson progress') }
  }

  const complete = async () => {
    setSaving(true)
    try {
      await coursesApi.complete(id)
      toast.success('Course complete. Your certificate is ready on My Certificates.')
      navigate('/employee/certificates')
    } catch (err) { toast.error(err.response?.data?.detail || 'Watch every lesson before completing the course') }
    finally { setSaving(false) }
  }

  if (!course || !enrollment) return <LoadingPage />
  const videos = course.videos || []
  const watched = new Set(enrollment.watched_video_ids || [])
  const completion = videos.length ? Math.round((watched.size / videos.length) * 100) : 0

  return (
    <div className="max-w-4xl">
      <button onClick={() => navigate('/employee/courses')} className="flex items-center gap-2 text-sm text-ink-400 hover:text-ink-800 mb-6"><ArrowLeft size={16} /> Back to catalog</button>
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div><p className="text-xs font-mono text-ink-400">{course.course_code}</p><h1 className="font-display text-3xl text-ink-900 mt-1">{course.title}</h1><p className="text-sm text-ink-400 mt-2 max-w-2xl">{course.description || 'Complete the lessons below to earn your verified certificate.'}</p></div>
        <Badge tone="success"><ShieldCheck size={14} /> Certificate eligible</Badge>
      </div>
      <Card className="p-5 mb-5">
        <div className="flex justify-between items-center mb-2"><span className="text-sm font-medium text-ink-800">Course completion</span><span className="text-sm text-ink-400">{watched.size} of {videos.length} lessons</span></div>
        <ProgressBar value={completion} />
      </Card>
      <div className="space-y-5">
        {videos.map((video, index) => (
          <Card key={video.id} className="overflow-hidden">
            <div className="aspect-video bg-ink-900 relative"><iframe className="w-full h-full" src={`https://www.youtube.com/embed/${video.youtube_id}?rel=0`} title={video.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerPolicy="strict-origin-when-cross-origin" allowFullScreen /><a href={`https://www.youtube.com/watch?v=${video.youtube_id}`} target="_blank" rel="noreferrer" className="absolute inset-x-0 bottom-0 bg-black/70 text-white text-center text-sm py-2 hover:bg-black/85">Open this lesson on YouTube if the embedded player does not start</a></div>
            <div className="p-5 flex flex-wrap items-center justify-between gap-4"><div><p className="text-xs text-ink-400">Lesson {index + 1} {video.duration && `· ${video.duration}`}</p><h2 className="font-medium text-ink-800 mt-1">{video.title}</h2><a className="text-xs text-gold-700 hover:underline mt-2 inline-block" href={`https://www.youtube.com/watch?v=${video.youtube_id}`} target="_blank" rel="noreferrer">Player not loading? Watch directly on YouTube</a></div>{watched.has(String(video.id)) ? <span className="flex items-center gap-1.5 text-sm text-emerald-700"><CheckCircle2 size={17} /> Watched</span> : <Button variant="outline" onClick={() => markWatched(video.id)}><PlayCircle size={16} /> Mark lesson watched</Button>}</div>
          </Card>
        ))}
      </div>
      <Card className="p-5 mt-6 flex flex-wrap items-center justify-between gap-4"><div><h2 className="font-medium text-ink-800">Ready to finish?</h2><p className="text-sm text-ink-400 mt-1">Watch every lesson, then receive a certificate in your account name.</p></div><Button variant="gold" disabled={saving || completion < 100} onClick={complete}>{saving ? 'Generating certificate...' : 'Complete course'}</Button></Card>
    </div>
  )
}