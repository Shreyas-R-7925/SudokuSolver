import React from 'react'
import {SolveSudoku} from './components'; 
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import './index.css';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SolveSudoku />} />              
      </Routes>
    </BrowserRouter>
  )
}

export default App