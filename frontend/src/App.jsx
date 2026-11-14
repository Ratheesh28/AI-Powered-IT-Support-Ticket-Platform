import Analytics from "./pages/Analytics";
import TicketHistory from "./pages/TicketHistory";
import CreateTicket from "./pages/CreateTicket";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">

        <Sidebar />

        <Routes>
          <Route path="/" element={<Dashboard />} />

          <Route
  path="/create-ticket"
  element={<CreateTicket />}
/>

<Route
  path="/tickets"
  element={<TicketHistory />}
/>

<Route
  path="/analytics"
  element={<Analytics />}
/>

        </Routes>

      </div>
    </BrowserRouter>
  );
}

export default App;
