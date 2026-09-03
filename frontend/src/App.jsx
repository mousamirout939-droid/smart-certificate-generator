import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ToastProvider } from './context/ToastContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './layouts/AppLayout'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Employees from './pages/Employees'
import EmployeeDetail from './pages/EmployeeDetail'
import Courses from './pages/Courses'
import LearningRecords from './pages/LearningRecords'
import Certificates from './pages/Certificates'
import Settings from './pages/Settings'
import Profile from './pages/Profile'
import EmployeeDashboard from './pages/EmployeeDashboard'
import EmployeeCertificates from './pages/EmployeeCertificates'
import EmployeeCourses from './pages/EmployeeCourses'
import EmployeeCourseDetail from './pages/EmployeeCourseDetail'
import CertificateVerify from './pages/CertificateVerify'

function RootRedirect() {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'admin' ? '/dashboard' : '/employee/dashboard'} replace />
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/verify/:certificateId" element={<CertificateVerify />} />

            <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              {/* Admin routes */}
              <Route path="/dashboard" element={<ProtectedRoute adminOnly><Dashboard /></ProtectedRoute>} />
              <Route path="/employees" element={<ProtectedRoute adminOnly><Employees /></ProtectedRoute>} />
              <Route path="/employees/:id" element={<ProtectedRoute adminOnly><EmployeeDetail /></ProtectedRoute>} />
              <Route path="/courses" element={<ProtectedRoute adminOnly><Courses /></ProtectedRoute>} />
              <Route path="/learning" element={<ProtectedRoute adminOnly><LearningRecords /></ProtectedRoute>} />
              <Route path="/certificates" element={<ProtectedRoute adminOnly><Certificates /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute adminOnly><Settings /></ProtectedRoute>} />

              {/* Shared */}
              <Route path="/profile" element={<Profile />} />

              {/* Employee routes */}
              <Route path="/employee/dashboard" element={<EmployeeDashboard />} />
              <Route path="/employee/courses" element={<EmployeeCourses />} />
              <Route path="/employee/courses/:id" element={<EmployeeCourseDetail />} />
              <Route path="/employee/certificates" element={<EmployeeCertificates />} />
            </Route>

            <Route path="/" element={<RootRedirect />} />
            <Route path="*" element={<RootRedirect />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
