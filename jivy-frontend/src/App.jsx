import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./components/Auth/Login";
import DoctorDashboard from "./components/Doctor/DoctorDashboard";
import OpsDashboard from "./components/Ops/OpsDashboard";
import AdminDashboard from "./components/Admin/AdminDashboard";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/doctor" element={<DoctorDashboard />} />
        <Route path="/ops" element={<OpsDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
