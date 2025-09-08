import { useState, useEffect } from 'react'
import { api, type AuthStatus } from '@/lib/api'
import { cn } from '@/lib/utils'
import { RefreshCw, LogOut, Check, X } from 'lucide-react'

export default function AuthStatusComponent() {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchAuthStatus = async () => {
    setLoading(true)
    try {
      const status = await api.getAuthStatus()
      setAuthStatus(status)
    } catch (error) {
      console.error('Failed to fetch auth status:', error)
      setAuthStatus({
        authenticated: false,
        message: 'Failed to check authentication'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAuthStatus()
  }, [])

  const handleRefresh = () => {
    fetchAuthStatus()
  }

  const handleLogout = () => {
    // In a real app, this would clear the OAuth credentials
    alert('Logout functionality not implemented in demo')
  }

  if (loading) {
    return (
      <div className="flex items-center gap-4">
        <div className="animate-pulse bg-gray-200 h-10 w-64 rounded-full" />
      </div>
    )
  }

  return (
    <div className="flex items-center gap-4">
      <div className={cn(
        "flex items-center gap-2 px-4 py-2 rounded-full border-2",
        authStatus?.authenticated 
          ? "bg-green-50 border-green-300 text-green-800"
          : "bg-red-50 border-red-300 text-red-800"
      )}>
        {authStatus?.authenticated ? (
          <Check className="w-4 h-4" />
        ) : (
          <X className="w-4 h-4" />
        )}
        <span className="font-medium">
          {authStatus?.authenticated 
            ? `Claude authenticated (${authStatus.subscription_type || 'Unknown'} subscription)`
            : 'Not authenticated'
          }
        </span>
      </div>
      
      <button
        onClick={handleRefresh}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        title="Refresh"
      >
        <RefreshCw className="w-5 h-5" />
      </button>
      
      <button
        onClick={handleLogout}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        title="Logout"
      >
        <LogOut className="w-5 h-5" />
      </button>
    </div>
  )
}