import { RefreshCw } from 'lucide-react'
import { useEffect, useState } from 'react'
import AddAssetModal from '../features/assets/AddAssetModal'
import AssetCard from '../features/assets/AssetCard'
import { createAsset, listAssets } from '../services/assetsService'
import { useAuth } from '../state/AuthContext'
import type { Asset, AssetCreateInput } from '../types/models'

const MOCK_ASSETS: Asset[] = [
  {
    id: 9001,
    user_id: 1,
    name: 'Apple Inc.',
    asset_type: 'stock',
    value: 28600,
    currency: 'USD',
    category: 'Tech',
    description: 'Static fallback asset',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 9002,
    user_id: 1,
    name: 'Main ETH Wallet',
    asset_type: 'crypto',
    value: 13400,
    currency: 'USD',
    category: 'Web3',
    description: 'Static fallback asset',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

function changeFromId(id: number): number {
  return ((id * 31) % 700) / 100 - 3
}

function AssetsPage() {
  const { token } = useAuth()
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    const fetchAssets = async () => {
      if (!token) {
        return
      }
      setLoading(true)
      setError('')
      try {
        const response = await listAssets(token)
        setAssets(response.data.assets)
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Failed to load assets')
        setAssets(MOCK_ASSETS)
      } finally {
        setLoading(false)
      }
    }

    void fetchAssets()
  }, [token])

  const handleCreate = async (payload: AssetCreateInput) => {
    if (!token) {
      return
    }
    setSubmitting(true)
    setError('')

    try {
      await createAsset(token, payload)
      const response = await listAssets(token)
      setAssets(response.data.assets)
      window.dispatchEvent(new Event('wwh:assets-updated'))
      setModalOpen(false)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Failed to add asset')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="space-y-4">
      <div className="glass-panel flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">My Assets</h1>
          <p className="text-sm text-slate-500">Track traditional and digital holdings in one stream.</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
          >
            + Add Asset
          </button>
          <button
            type="button"
            onClick={() => {
              setSyncing(true)
              window.setTimeout(() => setSyncing(false), 1500)
            }}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
          >
            <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
            {syncing ? 'Syncing...' : 'Sync Wallet'}
          </button>
        </div>
      </div>

      {error ? <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">{error}</p> : null}

      {loading ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-24 rounded-2xl border border-slate-200 bg-slate-100" />
          ))}
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {assets.map((asset) => (
            <AssetCard key={asset.id} asset={asset} changePercent={changeFromId(asset.id)} />
          ))}
        </div>
      )}

      {!loading && assets.length === 0 ? (
        <div className="glass-panel p-8 text-center text-slate-500">No assets yet. Add your first one to get started.</div>
      ) : null}

      <AddAssetModal open={modalOpen} submitting={submitting} onClose={() => setModalOpen(false)} onSubmit={handleCreate} />
    </section>
  )
}

export default AssetsPage
