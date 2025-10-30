import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SalonDashboard } from '../components/SalonDashboard';
import { SalonDetailView } from '../components/SalonDetailView';

export const SalonPage: React.FC = () => {
  const { salonId } = useParams<{ salonId: string }>();
  const navigate = useNavigate();

  if (salonId) {
    return (
      <SalonDetailView 
        salonId={salonId} 
        onBack={() => navigate('/salons')}
      />
    );
  }

  return <SalonDashboard />;
};
