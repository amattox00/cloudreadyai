import { useState } from "react";
import Diagrams from "./Diagrams";

export default function App() {
  const [page, setPage] = useState<"home" | "diagrams">("home");

  return (
    <div>
      <nav style={{ padding: "1rem", borderBottom: "1px solid #ddd", marginBottom: "1rem" }}>
        <button onClick={() => setPage("home")} style={{ marginRight: 10 }}>
          Home
        </button>
        <button onClick={() => setPage("diagrams")}>
          Diagram Generator
        </button>
      </nav>

      {page === "home" && (
        <div style={{ padding: "1rem" }}>
          <h1>CloudReadyAI</h1>
          <p>Welcome! Select “Diagram Generator” above to create cloud diagrams.</p>
        </div>
      )}

      {page === "diagrams" && <Diagrams />}
    </div>
  );
}
