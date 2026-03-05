import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../state/AuthContext'

function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('Demo User')
  const [email, setEmail] = useState('demo@wwh.app')
  const [password, setPassword] = useState('123456')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      await register(name, email, password)
      navigate('/dashboard', { replace: true })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-frame px-4 py-8">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl">
        <p className="text-xs uppercase tracking-[0.2em] text-teal-600">Create profile</p>
        <h1 className="mt-2 font-display text-2xl text-slate-900">Start your Wealth Wellness Hub</h1>

        <label className="mt-6 block text-sm font-medium text-slate-700">Name</label>
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2 outline-none ring-teal-500 transition focus:ring"
        />

        <label className="mt-4 block text-sm font-medium text-slate-700">Email</label>
        <input
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          type="email"
          required
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2 outline-none ring-teal-500 transition focus:ring"
        />

        <label className="mt-4 block text-sm font-medium text-slate-700">Password</label>
        <input
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          type="password"
          required
          minLength={6}
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2 outline-none ring-teal-500 transition focus:ring"
        />

        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {loading ? 'Creating account...' : 'Create account'}
        </button>

        <p className="mt-4 text-sm text-slate-500">
          Already have an account?{' '}
          <Link className="font-semibold text-slate-900 underline" to="/login">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  )
}

export default RegisterPage
