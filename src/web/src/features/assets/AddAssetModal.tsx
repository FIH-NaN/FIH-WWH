import { useState } from 'react'
import type { AssetCreateInput, AssetType } from '../../types/models'

type Props = {
  open: boolean
  submitting: boolean
  onClose: () => void
  onSubmit: (payload: AssetCreateInput) => Promise<void>
}

const ASSET_TYPES: AssetType[] = ['cash', 'stock', 'bond', 'fund', 'crypto', 'real_estate', 'other']

const ASSET_TYPE_LABELS: Record<AssetType, string> = {
  cash: 'Cash',
  stock: 'Stock',
  bond: 'Bond',
  fund: 'Fund',
  crypto: 'Crypto',
  property: 'Property',
  real_estate: 'Real Estate',
  digital_asset: 'Digital Asset',
  deposit_account: 'Deposit Account',
  etf: 'ETF',
  mutual_fund: 'Mutual Fund',
  commodity: 'Commodity',
  other: 'Other',
}

const initialState: AssetCreateInput = {
  name: '',
  asset_type: 'stock',
  value: 0,
  currency: 'USD',
  category: '',
  description: '',
}

function AddAssetModal({ open, submitting, onClose, onSubmit }: Props) {
  const [form, setForm] = useState<AssetCreateInput>(initialState)

  if (!open) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-900/40 p-4" onClick={onClose}>
      <form
        className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
        onSubmit={async (event) => {
          event.preventDefault()
          await onSubmit(form)
          setForm(initialState)
        }}
      >
        <h3 className="font-display text-xl text-slate-900">Add Asset</h3>
        <p className="mt-1 text-sm text-slate-500">Add manual holdings to your Wealth Wallet.</p>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label className="text-sm font-medium text-slate-700">Name</label>
            <input
              required
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Type</label>
            <select
              value={form.asset_type}
              onChange={(event) => setForm((prev) => ({ ...prev, asset_type: event.target.value as AssetType }))}
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
            >
              {ASSET_TYPES.map((type) => (
                <option key={type} value={type}>
                  {ASSET_TYPE_LABELS[type] ?? type.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Value</label>
            <input
              required
              min={0}
              step="0.01"
              type="number"
              value={form.value}
              onChange={(event) => setForm((prev) => ({ ...prev, value: Number(event.target.value) }))}
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Currency</label>
            <input
              value={form.currency}
              onChange={(event) => setForm((prev) => ({ ...prev, currency: event.target.value.toUpperCase() }))}
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Category</label>
            <input
              value={form.category}
              onChange={(event) => setForm((prev) => ({ ...prev, category: event.target.value }))}
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="text-sm font-medium text-slate-700">Description</label>
            <textarea
              value={form.description}
              onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
              rows={3}
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <button type="button" className="rounded-xl border border-slate-300 px-4 py-2" onClick={onClose}>
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-xl bg-slate-900 px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {submitting ? 'Adding...' : 'Add Asset'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default AddAssetModal
