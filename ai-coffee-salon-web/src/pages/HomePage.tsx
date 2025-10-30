import React from 'react';
import { HeroSection } from '../components/HeroSection';
import { ArchitectureSection } from '../components/ArchitectureSection';
import { ProtocolsSection } from '../components/ProtocolsSection';
import { AgentsSection } from '../components/AgentsSection';
import { AboutSection } from '../components/AboutSection';

export const HomePage: React.FC = () => {
  return (
    <>
      <HeroSection />
      <ArchitectureSection />
      <ProtocolsSection />
      <AgentsSection />
      <AboutSection />
    </>
  );
};
