import { QueryClient } from '@tanstack/react-query'
import { createConfig, http } from 'wagmi'
import { injected } from 'wagmi/connectors'
import { arbitrum, base, mainnet, optimism, polygon } from 'wagmi/chains'

export const queryClient = new QueryClient()

export const walletConfig = createConfig({
  chains: [mainnet, base, polygon, arbitrum, optimism],
  connectors: [injected()],
  transports: {
    [mainnet.id]: http(),
    [base.id]: http(),
    [polygon.id]: http(),
    [arbitrum.id]: http(),
    [optimism.id]: http(),
  },
})
