import { Header } from "./components/Header";
import { AdminPage } from "./features/admin/AdminPage";
import { PublicPage } from "./features/public/PublicPage";

export function App() {
  const route = window.location.pathname === "/admin" ? "admin" : "public";

  return (
    <div className="app-shell">
      <Header route={route} />
      {route === "admin" ? <AdminPage /> : <PublicPage />}
    </div>
  );
}
