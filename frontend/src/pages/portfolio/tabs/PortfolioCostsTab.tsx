export default function PortfolioCostsTab() {
  return (
    <section className="space-y-4">
      <div className="border rounded-xl p-4">
        <h2 className="font-semibold">Cost Estimates</h2>
        <p className="text-sm text-gray-600 mt-2">
          Hook this panel to /v1/cost endpoints for this portfolio’s runs.
        </p>
      </div>
    </section>
  );
}
