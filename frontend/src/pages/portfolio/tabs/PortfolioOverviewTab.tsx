export default function PortfolioOverviewTab() {
  return (
    <section className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="border rounded-xl p-4">Summary KPIs</div>
        <div className="border rounded-xl p-4">Recent Runs</div>
        <div className="border rounded-xl p-4">Open Actions</div>
      </div>
    </section>
  );
}
