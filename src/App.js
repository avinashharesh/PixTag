// src/App.js
import React, { useContext } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import './App.css';
import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';
import QueriesPage from './pages/QueriesPage';
import Navbar from './components/Navbar';
import { AuthContext } from './AuthContext';

function App() {
  const { isLogged } = useContext(AuthContext);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/home"
            element={
              isLogged ? (
                <>
                  <Navbar />
                  <HomePage />
                </>
              ) : (
                <Navigate to="/" />
              )
            }
          />
          <Route
            path="/queries"
            element={
              isLogged ? (
                <>
                  <Navbar />
                  <QueriesPage />
                </>
              ) : (
                <Navigate to="/" />
              )
            }
          />
          <Route path="/" element={<AuthPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
