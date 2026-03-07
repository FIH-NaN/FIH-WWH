import { useEffect, useState } from 'react'
import { connectAccount, disconnectAccount, getSyncStatus, listAccounts, triggerSync } from '../services/accountsService'
import { useAuth } from '../state/AuthContext'
import type { AccountConnection, AccountProvider } from '../types/models'

function SettingsPage() {
  const { token } = useAuth()
  const [accounts, setAccounts] = useState<AccountConnection[]>([])
  const [provider, setProvider] = useState<AccountProvider>('evm')
  const [walletAddress, setWalletAddress] = useState('')
  const [network, setNetwork] = useState('ethereum')
  const [plaidAccessToken, setPlaidAccessToken] = useState('')
  const [feedback, setFeedback] = useState('')
  const [busy, setBusy] = useState(false)

  const refreshAccounts = async () => {
    if (!token) {
      return
    }
    const response = await listAccounts(token)
    setAccounts(response.data.accounts)
  }

  useEffect(() => {
    void refreshAccounts()
  }, [token])

  const handleConnect = async () => {
    if (!token) {
      return
    }
    setBusy(true)
    setFeedback('')
    try {
      if (provider === 'evm') {
        await connectAccount(token, {
          provider: 'evm',
          type: 'crypto_wallet',
          credentials: { walletAddress, network },
        })
      } else {
        await connectAccount(token, {
          provider: 'plaid',
          type: 'bank',
          credentials: { accessToken: plaidAccessToken },
        })
      }
      setFeedback('Account connected successfully.')
      await refreshAccounts()
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Failed to connect account')
    } finally {
      setBusy(false)
    }
  }

  const handleSync = async (accountId: number) => {
    if (!token) {
      return
    }
    setBusy(true)
    setFeedback('')
    try {
      const triggered = await triggerSync(token, accountId)
      const jobId = triggered.data.job_id
      for (let i = 0; i < 25; i += 1) {
        const statusResponse = await getSyncStatus(token, jobId)
        const status = statusResponse.data.status
        if (status === 'success') {
          const warnings = statusResponse.data.warnings.length > 0 ? ` Warnings: ${statusResponse.data.warnings.join(' | ')}` : ''
          setFeedback(
            `GoldRush sync complete (${statusResponse.data.sync_mode}). New assets: ${statusResponse.data.new_assets_count}, updated: ${statusResponse.data.updated_assets_count}, chains scanned: ${statusResponse.data.chains_scanned}, tokens imported: ${statusResponse.data.tokens_imported}.${warnings}`
          )
          await refreshAccounts()
          window.dispatchEvent(new Event('wwh:assets-updated'))
          break
        }
        if (status === 'failed') {
          setFeedback(statusResponse.data.error_message ?? 'Sync failed')
          break
        }
        await new Promise((resolve) => window.setTimeout(resolve, 1200))
      }
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Failed to sync account')
    } finally {
      setBusy(false)
    }
  }

  const handleDisconnect = async (accountId: number) => {
    if (!token) {
      return
    }
    setBusy(true)
    setFeedback('')
    try {
      await disconnectAccount(token, accountId)
      setFeedback('Account disconnected.')
      await refreshAccounts()
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Failed to disconnect account')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="space-y-4">
      <div className="glass-panel p-6">
        <h1 className="font-display text-2xl text-slate-900">Wallet Connections</h1>
        <p className="mt-2 text-sm text-slate-600">Bind an EVM wallet or Plaid account for one-click portfolio sync.</p>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <label className="text-sm text-slate-700">
            Provider
            <select
              className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
              value={provider}
              onChange={(event) => setProvider(event.target.value as AccountProvider)}
            >
              <option value="evm">EVM Wallet</option>
              <option value="plaid">Plaid</option>
            </select>
          </label>

          {provider === 'evm' ? (
            <>
              <label className="text-sm text-slate-700">
                Wallet Address
                <input
                  value={walletAddress}
                  onChange={(event) => setWalletAddress(event.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
                  placeholder="0x..."
                />
              </label>
              <label className="text-sm text-slate-700">
                Network
                <select
                  value={network}
                  onChange={(event) => setNetwork(event.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
                >
                  <option value="ethereum">Ethereum</option>
                  <option value="base">Base</option>
                  <option value="polygon">Polygon</option>
                  <option value="arbitrum">Arbitrum</option>
                  <option value="optimism">Optimism</option>
                </select>
              </label>
            </>
          ) : (
            <label className="text-sm text-slate-700 sm:col-span-2">
              Plaid Access Token (sandbox)
              <input
                value={plaidAccessToken}
                onChange={(event) => setPlaidAccessToken(event.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
                placeholder="access-sandbox-..."
              />
            </label>
          )}
        </div>

        <button
          type="button"
          onClick={handleConnect}
          disabled={busy}
          className="mt-4 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {busy ? 'Processing...' : 'Connect Account'}
        </button>
      </div>

      {feedback ? <p className="rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-700">{feedback}</p> : null}

      <div className="glass-panel p-6">
        <h2 className="font-display text-xl text-slate-900">Connected Accounts</h2>
        <div className="mt-4 space-y-3">
          {accounts.length === 0 ? <p className="text-sm text-slate-500">No connected accounts yet.</p> : null}
          {accounts.map((account) => (
            <div key={account.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900">{account.name}</p>
                  <p className="text-xs text-slate-500">
                    {account.provider.toUpperCase()} {account.network ? `• ${account.network}` : ''}
                  </p>
                  {account.last_synced ? <p className="text-xs text-slate-500">Last synced: {account.last_synced}</p> : null}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleSync(account.id)}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700"
                  >
                    Sync
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDisconnect(account.id)}
                    className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-medium text-rose-700"
                  >
                    Disconnect
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default SettingsPage
