import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../state/AuthContext'

function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('demo@wwh.app')
  const [password, setPassword] = useState('123456')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fromPath = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/dashboard'

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      await login(email, password)
      navigate(fromPath, { replace: true })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid min-h-screen bg-slate-950 text-white lg:grid-cols-2">
      <section className="hidden p-14 lg:flex lg:flex-col lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-teal-300">Wealth Wellness Hub</p>
          <h1 className="mt-4 max-w-md font-display text-4xl">One wallet view for TradFi and Web3 confidence.</h1>
        </div>
        <div className="glass-panel border-white/15 bg-white/10 p-6 text-sm text-slate-100/90">
          Personalized guidance, wallet sync, and asset-level transparency in one flow.
        </div>
      </section>

      <section className="grid place-items-center px-4 py-8">
        <form onSubmit={handleSubmit} className="w-full max-w-md rounded-3xl bg-white p-8 text-slate-900 shadow-2xl">
          <h2 className="font-display text-2xl">Welcome back</h2>
          <p className="mt-1 text-sm text-slate-500">Log in to continue to your portfolio shell.</p>

          <label className="mt-6 block text-sm font-medium">Email</label>
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            required
            className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2 outline-none ring-teal-500 transition focus:ring"
          />

          <label className="mt-4 block text-sm font-medium">Password</label>
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            required
            className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2 outline-none ring-teal-500 transition focus:ring"
          />

          {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>

          <p className="mt-4 text-sm text-slate-500">
            No account?{' '}
            <Link className="font-semibold text-slate-900 underline" to="/register">
              Create one
            </Link>
          </p>
        </form>
      </section>
    </div>
  )
}

export default LoginPage
