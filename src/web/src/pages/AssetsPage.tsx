import { AlertTriangle, Building2, Loader2, Plus, RefreshCw, Wallet } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { usePlaidLink } from 'react-plaid-link'
import { useAccount, useChainId, useConnect, useDisconnect } from 'wagmi'
import { connectAccount, createPlaidLinkToken, getSyncStatus, getWalletHoldings, getWalletsSummary, seedPlaidCurrentMonthDemo, triggerSync } from '../services/accountsService'
import AddAssetModal from '../features/assets/AddAssetModal'
import { createAsset, listAssets } from '../services/assetsService'
import { useAuth } from '../state/AuthContext'
import type { Asset, AssetCreateInput, SyncMode, SyncStatusPayload, WalletHoldingsPayload, WalletSummary } from '../types/models'

function formatUsd(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(value)
}

function shortAddress(address?: string | null): string {
  if (!address) return 'Not available'
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

function chainIdToNetwork(chainId: number): string {
  if (chainId === 137) return 'polygon'
  if (chainId === 42161) return 'arbitrum'
  if (chainId === 10) return 'optimism'
  if (chainId === 8453) return 'base'
  return 'ethereum'
}

function AssetsPage() {
  const { token } = useAuth()
  const { address, isConnected } = useAccount()
  const { connectors, connect, isPending } = useConnect()
  const { disconnect } = useDisconnect()
  const chainId = useChainId()

  const [wallets, setWallets] = useState<WalletSummary[]>([])
  const [activeWalletId, setActiveWalletId] = useState<number | null>(null)
  const [walletHoldings, setWalletHoldings] = useState<WalletHoldingsPayload | null>(null)
  const [walletsLoading, setWalletsLoading] = useState(true)
  const [holdingsLoading, setHoldingsLoading] = useState(false)
  const [error, setError] = useState('')
  const [feedback, setFeedback] = useState('')
  const [syncing, setSyncing] = useState(false)
  const [syncMode, setSyncMode] = useState<SyncMode>('quick')
  const [syncStatus, setSyncStatus] = useState<SyncStatusPayload | null>(null)
  const [bindingWallet, setBindingWallet] = useState(false)
  const [bindingBank, setBindingBank] = useState(false)
  const [seedingDemo, setSeedingDemo] = useState(false)
  const [plaidLinkToken, setPlaidLinkToken] = useState('')
  const [manualAssets, setManualAssets] = useState<Asset[]>([])
  const [manualAssetsLoading, setManualAssetsLoading] = useState(false)
  const [addAssetOpen, setAddAssetOpen] = useState(false)
  const [addingAsset, setAddingAsset] = useState(false)
  const boundAddressesRef = useRef<Set<string>>(new Set())

  const activeWallet = useMemo(
    () => wallets.find((wallet) => wallet.account_id === activeWalletId) ?? null,
    [wallets, activeWalletId],
  )

  const loadWalletSummary = async () => {
    if (!token) return
    setWalletsLoading(true)
    try {
      const response = await getWalletsSummary(token)
      const list = response.data.wallets
      setWallets(list)
      if (list.length > 0) {
        setActiveWalletId((current) => current ?? list[0].account_id)
      } else {
        setActiveWalletId(null)
        setWalletHoldings(null)
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Failed to load wallet summary')
      setWallets([])
      setActiveWalletId(null)
      setWalletHoldings(null)
    } finally {
      setWalletsLoading(false)
    }
  }

  const loadManualAssets = async () => {
    if (!token) return
    setManualAssetsLoading(true)
    try {
      const response = await listAssets(token)
      const all = response.data.assets
      const filtered = all.filter((asset) => {
        const category = String(asset.category ?? '').toLowerCase()
        const description = String(asset.description ?? '').toLowerCase()
        const isSyncedCategory = category === 'plaid' || category === 'evm'
        const isSyncedDescription = description.startsWith('synced from')
        return !(isSyncedCategory || isSyncedDescription)
      })
      setManualAssets(filtered)
    } catch {
      setManualAssets([])
    } finally {
      setManualAssetsLoading(false)
    }
  }

  const loadWalletHoldings = async (walletId: number) => {
    if (!token) return
    setHoldingsLoading(true)
    try {
      const response = await getWalletHoldings(token, walletId)
      setWalletHoldings(response.data)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Failed to load wallet holdings')
      setWalletHoldings(null)
    } finally {
      setHoldingsLoading(false)
    }
  }

  useEffect(() => {
    void loadWalletSummary()
    void loadManualAssets()
  }, [token])

  useEffect(() => {
    if (activeWalletId) {
      void loadWalletHoldings(activeWalletId)
    }
  }, [activeWalletId, token])

  const refreshPlaidLinkToken = async () => {
    if (!token) return
    const response = await createPlaidLinkToken(token)
    setPlaidLinkToken(response.data.link_token)
  }

  useEffect(() => {
    if (!token || plaidLinkToken) {
      return
    }
    void refreshPlaidLinkToken()
  }, [token, plaidLinkToken])

  const pollSyncStatus = async (jobId: number) => {
    if (!token) return null

    for (let i = 0; i < 25; i += 1) {
      const response = await getSyncStatus(token, jobId)
      const payload = response.data
      setSyncStatus(payload)
      if (payload.status === 'success' || payload.status === 'failed') {
        return payload
      }
      await new Promise((resolve) => window.setTimeout(resolve, 1200))
    }

    return null
  }

  const handleSync = async (accountId?: number, mode: SyncMode = syncMode) => {
    if (!token) return
    setSyncing(true)
    setError('')
    setSyncStatus(null)

    try {
      const syncResponse = await triggerSync(token, accountId, mode)
      const finalStatus = await pollSyncStatus(syncResponse.data.job_id)
      if (finalStatus?.status === 'failed') {
        setError(finalStatus.error_message ?? 'Sync failed')
      } else {
        setFeedback(
          `Sync ${finalStatus?.status ?? 'completed'} (${mode}). New: ${finalStatus?.new_assets_count ?? 0}, Updated: ${finalStatus?.updated_assets_count ?? 0}, Chains: ${finalStatus?.chains_scanned ?? 0}.`,
        )
      }

      await loadWalletSummary()
      await loadManualAssets()
      if (activeWalletId) {
        await loadWalletHoldings(activeWalletId)
      }
      window.dispatchEvent(new Event('wwh:assets-updated'))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Failed to sync wallet accounts')
    } finally {
      setSyncing(false)
    }
  }

  const handlePlaidSuccess = async (publicToken: string, institutionName?: string) => {
    if (!token) return

    setBindingBank(true)
    setError('')
    setFeedback('')
    try {
      const linked = await connectAccount(token, {
        provider: 'plaid',
        type: 'bank',
        credentials: {
          publicToken,
          name: institutionName ?? 'Plaid Linked Account',
        },
      })

      const first = linked.data.accounts[0]
      setFeedback('Bank account connected. Running a quick sync...')
      await handleSync(first?.id, 'quick')
      setPlaidLinkToken('')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Failed to connect bank account')
    } finally {
      setBindingBank(false)
    }
  }

  const handleSeedPlaidDemo = async () => {
    if (!token) return

    setSeedingDemo(true)
    setError('')
    setFeedback('')
    try {
      const response = await seedPlaidCurrentMonthDemo(token)
      const seeded = response.data
      setFeedback(
        `Demo seeded via ${seeded.connection_name}. Current month Income ${formatUsd(seeded.current_month_income)}, Expense ${formatUsd(seeded.current_month_expense)}.`,
      )

      await loadWalletSummary()
      await loadManualAssets()
      setActiveWalletId(seeded.connection_id)
      await loadWalletHoldings(seeded.connection_id)
      window.dispatchEvent(new Event('wwh:assets-updated'))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Failed to seed Plaid demo data')
    } finally {
      setSeedingDemo(false)
    }
  }

  const handleAddManualAsset = async (payload: AssetCreateInput) => {
    if (!token) return
    setAddingAsset(true)
    setError('')
    try {
      await createAsset(token, payload)
      setAddAssetOpen(false)
      setFeedback('Manual asset added successfully.')
      await loadManualAssets()
      window.dispatchEvent(new Event('wwh:assets-updated'))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Failed to add manual asset')
    } finally {
      setAddingAsset(false)
    }
  }

  const { open: openPlaidLink, ready: plaidReady } = usePlaidLink({
    token: plaidLinkToken || null,
    onSuccess: (publicToken, metadata) => {
      const institutionName = metadata?.institution?.name ?? undefined
      void handlePlaidSuccess(publicToken, institutionName)
    },
    onExit: (linkError) => {
      if (linkError) {
        setError(linkError.display_message ?? linkError.error_message ?? 'Plaid Link exited with an error')
      }
    },
  })

  useEffect(() => {
    const bindConnectedWallet = async () => {
      if (!token || !isConnected || !address) {
        return
      }

      const key = address.toLowerCase()
      if (boundAddressesRef.current.has(key)) {
        return
      }

      setBindingWallet(true)
      setError('')
      try {
        const network = chainIdToNetwork(chainId)
        const connected = await connectAccount(token, {
          provider: 'evm',
          type: 'crypto_wallet',
          credentials: {
            walletAddress: key,
            network,
            name: `MetaMask ${shortAddress(key)}`,
          },
        })

        const first = connected.data.accounts[0]
        boundAddressesRef.current.add(key)
        setFeedback('Wallet connected. Running a deep sync...')
        await handleSync(first?.id, 'deep')
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Failed to bind wallet')
      } finally {
        setBindingWallet(false)
      }
    }

    void bindConnectedWallet()
  }, [token, isConnected, address, chainId])

  const walletConnectors = useMemo(() => {
    const seen = new Set<string>()
    return connectors.filter((connector) => {
      const key = `${connector.id}:${connector.name}`
      if (seen.has(key)) {
        return false
      }
      seen.add(key)
      return true
    })
  }, [connectors])

  const totalPortfolioUsd = useMemo(() => wallets.reduce((sum, item) => sum + item.total_value_usd, 0), [wallets])

  return (
    <section className="space-y-4">
      <div className="glass-panel p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">My Assets</h1>
            <p className="text-sm text-slate-500">Unified cards for onchain wallets and linked bank accounts.</p>
            <p className="mt-1 text-xs text-slate-500">Portfolio total: {formatUsd(totalPortfolioUsd)}</p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {walletConnectors.map((connector) => (
              <button
                key={connector.uid}
                type="button"
                onClick={() => connect({ connector })}
                disabled={isPending || bindingWallet}
                className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
              >
                {isPending ? 'Connecting...' : `Connect ${connector.name}`}
              </button>
            ))}
            {isConnected ? (
              <button
                type="button"
                onClick={() => disconnect()}
                className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700"
              >
                Disconnect Wallet
              </button>
            ) : null}

            <button
              type="button"
              onClick={() => openPlaidLink()}
              disabled={!plaidReady || bindingBank || syncing || seedingDemo}
              className="inline-flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Building2 size={14} />
              {!plaidLinkToken ? 'Preparing Bank Link...' : plaidReady ? 'Connect Bank' : 'Loading Plaid...'}
            </button>

            <button
              type="button"
              onClick={() => void handleSeedPlaidDemo()}
              disabled={seedingDemo || syncing || bindingBank}
              className="inline-flex items-center gap-2 rounded-xl border border-cyan-200 bg-cyan-50 px-4 py-2 text-sm font-medium text-cyan-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Plus size={14} />
              {seedingDemo ? 'Seeding Demo...' : 'Seed Plaid Demo Data'}
            </button>

            <select
              className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700"
              value={syncMode}
              onChange={(event) => setSyncMode(event.target.value as SyncMode)}
            >
              <option value="quick">Quick Sync</option>
              <option value="deep">Deep Sync</option>
            </select>
            <button
              type="button"
              onClick={() => handleSync(activeWalletId ?? undefined)}
              disabled={syncing || wallets.length === 0 || seedingDemo}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
            >
              <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
              {syncing ? 'Syncing...' : 'Sync Active Wallet'}
            </button>

            <button
              type="button"
              onClick={() => setAddAssetOpen(true)}
              className="inline-flex items-center gap-2 rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-700"
            >
              <Plus size={14} />
              Add Manual Asset
            </button>
          </div>
        </div>
      </div>

      {error ? <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">{error}</p> : null}
      {feedback ? <p className="rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{feedback}</p> : null}
      {syncStatus?.warnings?.length ? (
        <p className="rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-700">
          Warnings: {syncStatus.warnings.join(' | ')}
        </p>
      ) : null}

      {import.meta.env.DEV ? (
        <div className="rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-800">
          <p className="font-semibold">Plaid Sandbox Test Hint</p>
          <p className="mt-1">Use these credentials inside the Plaid Link popup:</p>
          <p className="font-mono text-xs mt-1">username: user_transactions_dynamic</p>
          <p className="font-mono text-xs">password: pass_good</p>
          <a
            href="https://plaid.com/docs/sandbox/test-credentials/"
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-block underline"
          >
            Plaid sandbox credentials docs
          </a>
        </div>
      ) : null}

      <div className="glass-panel p-4">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-900">Your Wallet Cards</p>
          <span className="text-xs text-slate-500">{wallets.length} wallets</span>
        </div>

        {walletsLoading ? (
          <div className="flex gap-3 overflow-x-auto pb-2">
            {Array.from({ length: 3 }).map((_, idx) => (
              <div key={idx} className="h-36 min-w-[260px] rounded-2xl border border-slate-200 bg-slate-100" />
            ))}
          </div>
        ) : wallets.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-slate-500">
            No accounts connected yet. Use Connect Wallet or Connect Bank to create your first card.
          </div>
        ) : (
          <div className="flex gap-3 overflow-x-auto pb-2">
            {wallets.map((wallet) => {
              const isActive = wallet.account_id === activeWalletId
              return (
                <button
                  key={wallet.account_id}
                  type="button"
                  onClick={() => setActiveWalletId(wallet.account_id)}
                  className={`min-w-[280px] rounded-2xl border p-4 text-left transition ${
                    isActive
                      ? 'border-teal-400 bg-gradient-to-br from-teal-50 to-cyan-50 shadow-lg'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-500">{wallet.name}</p>
                      <p className="mt-1 text-sm font-semibold text-slate-900">{shortAddress(wallet.wallet_address)}</p>
                    </div>
                    <Wallet size={18} className="text-slate-500" />
                  </div>
                  <p className="mt-4 text-2xl font-semibold text-slate-900">{formatUsd(wallet.total_value_usd)}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {wallet.token_count} tokens • {wallet.active_chain_count} chains
                  </p>
                  {wallet.last_error ? (
                    <p className="mt-2 inline-flex items-center gap-1 rounded-full bg-rose-50 px-2 py-1 text-xs text-rose-700">
                      <AlertTriangle size={12} /> {wallet.last_error}
                    </p>
                  ) : null}
                </button>
              )
            })}
          </div>
        )}
      </div>

      <div className="glass-panel p-4">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-900">Asset Information</p>
            <p className="text-xs text-slate-500">
              {activeWallet ? `${activeWallet.name} (${shortAddress(activeWallet.wallet_address)})` : 'Select a wallet card'}
            </p>
          </div>
          {holdingsLoading ? <Loader2 size={16} className="animate-spin text-slate-500" /> : null}
        </div>

        {!activeWallet ? (
          <p className="text-sm text-slate-500">No active wallet selected.</p>
        ) : holdingsLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, idx) => (
              <div key={idx} className="h-10 rounded-xl bg-slate-100" />
            ))}
          </div>
        ) : walletHoldings?.chains.length ? (
          <div className="space-y-3">
            {walletHoldings.chains.map((chain) => (
              <div key={`${chain.chain_name}-${chain.chain_id ?? 'na'}`} className="rounded-xl border border-slate-200 bg-white p-3">
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-900">{chain.chain_name}</p>
                  <p className="text-sm font-medium text-slate-700">{formatUsd(chain.subtotal_usd)}</p>
                </div>
                <div className="space-y-1">
                  {chain.tokens.map((token) => (
                    <div key={token.external_holding_id} className="flex items-center justify-between rounded-lg px-2 py-1 hover:bg-slate-50">
                      <div>
                        <p className="text-sm font-medium text-slate-800">{token.name}</p>
                        <p className="text-xs text-slate-500">{token.symbol} • {token.amount.toFixed(6)}</p>
                      </div>
                      <p className="text-sm font-medium text-slate-700">{formatUsd(token.value_usd)}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No holdings available for this wallet.</p>
        )}
      </div>

      <div className="glass-panel p-4">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-900">Manual Assets</p>
            <p className="text-xs text-slate-500">Use this section to add Real Estate or other non-Plaid assets.</p>
          </div>
          {manualAssetsLoading ? <Loader2 size={16} className="animate-spin text-slate-500" /> : null}
        </div>

        {manualAssets.length === 0 ? (
          <p className="text-sm text-slate-500">No manual assets yet. Click Add Manual Asset to add Real Estate, Stocks, Bonds, or Others.</p>
        ) : (
          <div className="space-y-2">
            {manualAssets.map((asset) => (
              <div key={`${asset.user_id}-${asset.id}`} className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-3 py-2">
                <div>
                  <p className="text-sm font-medium text-slate-900">{asset.name}</p>
                  <p className="text-xs text-slate-500">{asset.asset_type.replace(/_/g, ' ')}</p>
                </div>
                <p className="text-sm font-semibold text-slate-800">{formatUsd(asset.value)}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <AddAssetModal
        open={addAssetOpen}
        submitting={addingAsset}
        onClose={() => {
          if (addingAsset) return
          setAddAssetOpen(false)
        }}
        onSubmit={handleAddManualAsset}
      />
    </section>
  )
}

export default AssetsPage
