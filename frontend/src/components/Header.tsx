interface HeaderProps {
  route: "public" | "admin";
}

export function Header({ route }: HeaderProps) {
  return (
    <header className="topbar">
      <a className="brand" href="/public" aria-label="Public dashboard">
        <span className="brand-mark">UD</span>
        <span>User Dashboard</span>
      </a>
      {route === "admin" ? (
        <nav className="nav-tabs" aria-label="Admin navigation">
          <a href="/public">Public</a>
          <a className="active" href="/admin">
            Admin
          </a>
        </nav>
      ) : null}
    </header>
  );
}
