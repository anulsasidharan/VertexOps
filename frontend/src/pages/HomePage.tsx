import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Dashboard</h1>
      <p className="text-slate-400">
        Manage corpus documents and vector indexes from the sidebar, or jump in:
      </p>
      <ul className="list-inside list-disc text-indigo-400">
        <li>
          <Link className="hover:underline" to="/documents">
            Documents
          </Link>
        </li>
        <li>
          <Link className="hover:underline" to="/indexes">
            Indexes
          </Link>
        </li>
      </ul>
    </div>
  );
}
