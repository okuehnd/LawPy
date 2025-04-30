import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import QueryPage from './QueryPage';
import ResultsPage from './ResultsPage';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<QueryPage />} /> 
        <Route path="/results" element={<ResultsPage/>}/>
      </Routes>
    </Router>
  )};

export default App;