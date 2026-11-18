import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  PlusCircle,
  Ticket,
  ChartNoAxesCombined,
  Headset,
  Menu,
  X,
} from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/create-ticket", label: "Create Ticket", icon: PlusCircle },
  { to: "/tickets", label: "Ticket History", icon: Ticket },
  { to: "/analytics", label: "Analytics", icon: ChartNoAxesCombined },
];

function Sidebar() {
  const [open, setOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      <header className="mobile-topbar">
        <button
          type="button"
          className="icon-button"
          aria-label="Open navigation"
          aria-expanded={open}
          onClick={() => setOpen(true)}
        >
          <Menu size={20} />
        </button>
        <div className="mobile-brand">
          <Headset size={18} />
          <span>Ticket Intelligence</span>
        </div>
      </header>

      {open && (
        <button
          type="button"
          className="sidebar-backdrop"
          aria-label="Close navigation"
          onClick={() => setOpen(false)}
        />
      )}

      <aside className={`sidebar ${open ? "is-open" : ""}`}>
        <div className="sidebar-logo">
          <div className="brand-mark" aria-hidden="true">
            <Headset size={18} />
          </div>
          <div className="brand-copy">
            <p>AI-Powered IT Support</p>
            <h2>Ticket Intelligence</h2>
          </div>
          {open && (
            <button
              type="button"
              className="icon-button sidebar-close"
              aria-label="Close navigation"
              onClick={() => setOpen(false)}
            >
              <X size={18} />
            </button>
          )}
        </div>

        <p className="sidebar-section-label">Workspace</p>

        <nav className="sidebar-nav" aria-label="Primary">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  `nav-item${isActive ? " active" : ""}`
                }
              >
                <Icon size={18} />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <p>AI-Powered IT Support Ticket Intelligence Platform</p>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
