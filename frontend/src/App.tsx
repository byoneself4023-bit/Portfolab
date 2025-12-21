import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import PortfolioCreate from './pages/PortfolioCreate';
import PortfolioDetail from './pages/PortfolioDetail';
import Simulation from './pages/Simulation';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Home />} />
        <Route path="/portfolio/create" element={<PortfolioCreate />} />
        <Route path="/portfolio/:id" element={<PortfolioDetail />} />
        <Route path="*" element={<Navigate to="/" />} />
        <Route path="/portfolio/:id/simulation" element={<Simulation />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;