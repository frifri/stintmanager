import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    // Check if the user is authenticated
    // This example checks if a JWT token exists in local storage
    const isAuthenticated = localStorage.getItem('token');

    // If not authenticated, redirect to login page, otherwise render the children components
    return isAuthenticated ? children : <Navigate to="/" replace />;
};

export default ProtectedRoute;