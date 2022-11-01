import React from 'react';
import { HashRouter as Router } from 'react-router-dom';
import { Routes, Route, Navigate } from 'react-router-dom';
import { NavigationProvider } from './contexts/navigation';
import routes from './routes';
import './themes/generated/theme.base.css';
import './themes/generated/theme.additional.css';

function Content() {
  return (
    <>
      <Routes>
        {routes.map(({ path, element }) => (
          <Route key={path} path={path} element={element} />
        ))}
        <Route path="*" element={<Navigate to="/home" />} />
      </Routes>
    </>
  );
}

function App() {
  return <Content />;
}

export default function Root() {
  return (
    <Router>
      <NavigationProvider>
        <App />
      </NavigationProvider>
    </Router>
  );
}
