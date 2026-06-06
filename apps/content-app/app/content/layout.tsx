import { ContentTabs } from '@/components/content-tabs';

export default function ContentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-full">
      <ContentTabs />
      <div className="flex-1 overflow-y-auto">{children}</div>
    </div>
  );
}
