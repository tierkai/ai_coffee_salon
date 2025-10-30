import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { HomePage } from './pages/HomePage';
import { SalonPage } from './pages/SalonPage';
import { Footer } from './components/Footer';
import './App.css';

function AppContent() {
  const location = useLocation();
  const isSalonDetailPage = location.pathname.startsWith('/salon/');

  return (
    <div className="App">
      {!isSalonDetailPage && <Navigation />}
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/salons" element={<SalonPage />} />
          <Route path="/salon/:salonId" element={<SalonPage />} />
        </Routes>
      </main>
      {!isSalonDetailPage && <Footer />}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
