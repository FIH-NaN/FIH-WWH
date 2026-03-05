import { Bitcoin, Building2, Landmark, TrendingDown, TrendingUp } from 'lucide-react'
import { formatMoney, formatPercent } from '../../lib/format'
import type { Asset } from '../../types/models'

type Props = {
  asset: Asset
  changePercent: number
}

function AssetCard({ asset, changePercent }: Props) {
  const Icon = asset.asset_type === 'crypto' ? Bitcoin : asset.asset_type === 'stock' ? Building2 : Landmark
  const isUp = changePercent >= 0

  return (
    <article className="glass-panel flex items-center gap-4 p-4 transition hover:-translate-y-0.5 hover:shadow-xl">
      <div className="grid size-11 place-items-center rounded-xl bg-slate-100 text-slate-700">
        <Icon size={20} />
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate font-display text-base text-slate-900">{asset.name}</p>
        <div className="mt-1 flex items-center gap-2 text-xs">
          <span className="rounded-md bg-slate-100 px-2 py-1 text-slate-600">{asset.asset_type.toUpperCase()}</span>
          <span
            className={`rounded-md px-2 py-1 font-semibold ${
              asset.asset_type === 'crypto' ? 'bg-teal-100 text-teal-800' : 'bg-blue-100 text-blue-800'
            }`}
          >
            {asset.asset_type === 'crypto' ? 'Web3' : 'TradFi'}
          </span>
        </div>
      </div>

      <div className="text-right">
        <p className="font-display text-lg text-slate-900">{formatMoney(asset.value, asset.currency || 'USD')}</p>
        <p className={`mt-1 inline-flex items-center gap-1 text-xs font-semibold ${isUp ? 'text-positive' : 'text-negative'}`}>
          {isUp ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
          {formatPercent(changePercent)}
        </p>
      </div>
    </article>
  )
}

export default AssetCard
