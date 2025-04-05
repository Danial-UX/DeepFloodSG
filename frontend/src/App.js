import './App.css';
import axios from 'axios';
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Main from './mainpage/Main';
import Login from './authentication/Login';
import Register from './authentication/Register';
import Exploration from './exploration/Exploration';
import ProtectedRoute from './components/ProtectedRoute';
import NotFound from './authentication/404';

axios.defaults.withCredentials = true;

function App() {
  useEffect(() => {
    document.title = 'DeepFloodSG';
  }, []);

  return (
    <div>
      <Router>
        <Routes>
          <Route path='*' element={<NotFound />} />
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/main" element={
            <ProtectedRoute>
              <Main />
            </ProtectedRoute>
          } />
          <Route path="/exploration" element={
            <ProtectedRoute>
              <Exploration/>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
