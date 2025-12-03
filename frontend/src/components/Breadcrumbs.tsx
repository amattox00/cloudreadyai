import { Link, useLocation, useParams } from "react-router-dom";

export default function Breadcrumbs() {
  const loc = useLocation();
  const parts = loc.pathname.split("/").filter(Boolean);
  const { portfolioId } = useParams();

  const pathFor = (i: number) => "/" + parts.slice(0, i + 1).join("/");

  return (
    <nav className="text-sm text-gray-600">
      <Link to="/" className="hover:underline">Home</Link>
      {parts.map((p, i) => (
        <span key={i}>
          <span className="mx-2">/</span>
          <Link to={pathFor(i)} className="hover:underline">
            {p === portfolioId ? `Portfolio ${portfolioId}` : p}
          </Link>
        </span>
      ))}
    </nav>
  );
}
