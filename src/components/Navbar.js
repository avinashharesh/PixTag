// src/components/Navbar.js
import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthContext';

const Navbar = () => {
  const navigate = useNavigate();
  const { setIsLogged } = useContext(AuthContext);

  const handleLogout = () => {
    setIsLogged(false); // Set isLogged to false
    alert('Logged out successfully!');
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div>
        <Link to="/home">Home</Link>
        <Link to="/queries">Queries</Link>
      </div>
      <button onClick={handleLogout}>Logout</button>
    </nav>
  );
};

export default Navbar;
