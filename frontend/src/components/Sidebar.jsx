
import {
    LayoutDashboard,
    PlusCircle,
    Ticket,
    ChartNoAxesCombined,
    Headset
  } from "lucide-react";
  
  import { NavLink } from "react-router-dom";
  
  function Sidebar() {
    return (
      <aside className="sidebar">
  
        <div className="sidebar-logo">
          <Headset size={26} />
          <h2>Ticket Intelligence</h2>
        </div>
  
        <nav className="sidebar-nav">
  
          <NavLink to="/" end className="nav-item">
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </NavLink>
  
          <NavLink to="/create-ticket" className="nav-item">
            <PlusCircle size={20} />
            <span>Create Ticket</span>
          </NavLink>
  
          <NavLink to="/tickets" className="nav-item">
            <Ticket size={20} />
            <span>Ticket History</span>
          </NavLink>
  
          <NavLink to="/analytics" className="nav-item">
            <ChartNoAxesCombined size={20} />
            <span>Analytics</span>
          </NavLink>
  
        </nav>
  
        <div className="sidebar-footer">
          <p>AI-Powered Support Platform</p>
        </div>
  
      </aside>
    );
  }
  
  export default Sidebar;
  