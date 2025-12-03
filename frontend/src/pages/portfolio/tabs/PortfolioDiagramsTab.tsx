import { Link, useParams } from "react-router-dom";

export default function PortfolioDiagramsTab() {
  const { portfolioId } = useParams();
  return (
    <section className="space-y-4">
      <div className="border rounded-xl p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Diagrams</h2>
          <Link to="/diagrams" className="text-sm underline">Open Global Diagrams Tool</Link>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Generate or package diagrams scoped to <strong>{portfolioId}</strong>.
        </p>
      </div>
    </section>
  );
}
