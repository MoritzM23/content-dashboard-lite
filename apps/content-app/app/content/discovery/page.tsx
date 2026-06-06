import { DiscoveryView } from '@/components/discovery-view';
import { loadContentIntel } from '@/lib/data';

export const dynamic = 'force-dynamic';

export default async function DiscoveryPage() {
  const intel = await loadContentIntel();
  return (
    <DiscoveryView
      discovery={intel?.discovery ?? null}
      marketCreators={intel?.market_creators ?? []}
      marketTopReels={intel?.market_top_reels ?? []}
      marketAnalysis={intel?.market_analysis ?? null}
    />
  );
}
