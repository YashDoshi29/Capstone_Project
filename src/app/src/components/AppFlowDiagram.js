import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Paper, useTheme } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '@mui/material/styles';

const FlowContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  minHeight: '600px',
  padding: theme.spacing(4),
  position: 'relative',
  overflow: 'hidden',
  background: 'linear-gradient(135deg, rgba(26, 26, 26, 0.5) 0%, rgba(26, 26, 26, 0.3) 100%)',
  borderRadius: '20px',
  backdropFilter: 'blur(10px)',
}));

const FlowNode = styled(motion.div)(({ theme }) => ({
  position: 'absolute',
  width: '100px',
  minHeight: '80px',
  padding: theme.spacing(1.5),
  background: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
  borderRadius: '12px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  cursor: 'pointer',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 2,
  transform: 'translate(-50px, -40px)',
  '&:hover': {
    transform: 'translate(-50px, -45px)',
    boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
    background: 'rgba(255, 255, 255, 1)',
  },
}));

const FlowLine = styled(motion.div)(({ theme }) => ({
  position: 'absolute',
  background: 'repeating-linear-gradient(90deg, rgba(255,255,255,0.8) 0px, rgba(255,255,255,0.8) 4px, transparent 4px, transparent 8px)',
  transformOrigin: 'left',
  zIndex: 1,
  height: '2px',
  top: '50%',
}));

const MovingLight = styled(motion.div)(({ theme }) => ({
  position: 'absolute',
  width: '12px',
  height: '12px',
  background: 'rgba(255, 255, 255, 0.9)',
  borderRadius: '50%',
  boxShadow: '0 0 15px 5px rgba(255, 255, 255, 0.5)',
  zIndex: 3,
}));

const NodeContent = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  color: '#1a1a1a',
}));

const NodeTitle = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  fontSize: '0.8rem',
  marginBottom: theme.spacing(0.5),
  color: '#1a1a1a',
}));

const NodeSubtitle = styled(Typography)(({ theme }) => ({
  fontSize: '0.6rem',
  color: '#666',
  marginBottom: theme.spacing(0.25),
}));

const AppFlowDiagram = () => {
  const theme = useTheme();
  const [activeSection, setActiveSection] = useState(null);
  const [lightPosition, setLightPosition] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const animationTimeout = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setLightPosition((prev) => (prev + 0.3) % 100);
    }, 20);

    if (!hasAnimated) {
      animationTimeout.current = setTimeout(() => {
        setHasAnimated(true);
      }, 2500);
    }

    return () => {
      clearInterval(interval);
      if (animationTimeout.current) {
        clearTimeout(animationTimeout.current);
      }
    };
  }, [hasAnimated]);

  const sections = [
    {
      id: 'users',
      title: 'Users',
      position: { x: 100, y: 200 },
      components: ['Authentication', 'Profile', 'Input'],
      tools: ['Auth0', 'Profiles']
    },
    {
      id: 'input',
      title: 'Input Sources',
      position: { x: 300, y: 200 },
      components: ['Data Sources', 'Upload'],
      tools: ['Processing']
    },
    {
      id: 'synthetic',
      title: 'Synthetic Data',
      position: { x: 500, y: 100 },
      components: ['Generation', 'Simulation'],
      tools: ['CTGAN', 'Bayesian']
    },
    {
      id: 'real',
      title: 'Real Transactions',
      position: { x: 500, y: 300 },
      components: ['Processing', 'Validation'],
      tools: ['APIs', 'Validation']
    },
    {
      id: 'classification',
      title: 'Classification',
      position: { x: 700, y: 200 },
      components: ['Analysis', 'Patterns'],
      tools: ['LSTM', 'BERT']
    },
    {
      id: 'dashboard',
      title: 'Dashboard',
      position: { x: 900, y: 100 },
      components: ['Overview', 'Metrics'],
      tools: ['Visualization']
    },
    {
      id: 'optimization',
      title: 'Optimization',
      position: { x: 900, y: 300 },
      components: ['Analysis', 'Planning'],
      tools: ['AI Models']
    },
    {
      id: 'investment',
      title: 'Investment',
      position: { x: 1100, y: 200 },
      components: ['Analysis', 'Portfolio'],
      tools: ['FinBERT', 'GPT-3.5']
    },
    {
      id: 'output',
      title: 'Output',
      position: { x: 1300, y: 200 },
      components: ['Guidance', 'Chatbot'],
      tools: ['APIs', 'Interface']
    }
  ];

  const connections = [
    { from: 'users', to: 'input', type: 'horizontal' },
    { from: 'input', to: 'synthetic', type: 'diagonal-up' },
    { from: 'input', to: 'real', type: 'diagonal-down' },
    { from: 'synthetic', to: 'classification', type: 'diagonal-down' },
    { from: 'real', to: 'classification', type: 'diagonal-up' },
    { from: 'classification', to: 'dashboard', type: 'diagonal-up' },
    { from: 'classification', to: 'optimization', type: 'diagonal-down' },
    { from: 'dashboard', to: 'investment', type: 'diagonal-down' },
    { from: 'optimization', to: 'investment', type: 'diagonal-up' },
    { from: 'investment', to: 'output', type: 'horizontal' }
  ];

  const getLightPosition = (connection) => {
    const fromSection = sections.find(s => s.id === connection.from);
    const toSection = sections.find(s => s.id === connection.to);
    const totalLength = Math.sqrt(
      Math.pow(toSection.position.x - fromSection.position.x, 2) +
      Math.pow(toSection.position.y - fromSection.position.y, 2)
    );
    const currentPosition = (lightPosition / 100) * totalLength;
    
    return {
      x: fromSection.position.x + (currentPosition / totalLength) * (toSection.position.x - fromSection.position.x),
      y: fromSection.position.y + (currentPosition / totalLength) * (toSection.position.y - fromSection.position.y),
      opacity: 1
    };
  };

  const getLineAnimation = (connection) => {
    if (!hasAnimated) {
      return {
        initial: { scaleX: 0 },
        animate: { scaleX: 1 },
        transition: { 
          duration: 1.5,
          delay: connection.from === 'users' ? 0 : 
                 connection.from === 'input' ? 0.5 : 
                 connection.from === 'synthetic' || connection.from === 'real' ? 1 : 
                 connection.from === 'classification' ? 1.5 : 2
        }
      };
    }
    return {
      initial: { scaleX: 1 },
      animate: { scaleX: 1 }
    };
  };

  return (
    <FlowContainer>
      <Box sx={{ position: 'relative', height: '500px', width: '100%', overflow: 'hidden' }}>
        {connections.map((connection, index) => {
          const fromSection = sections.find(s => s.id === connection.from);
          const toSection = sections.find(s => s.id === connection.to);
          
          return (
            <React.Fragment key={`${connection.from}-${connection.to}`}>
              <FlowLine
                {...getLineAnimation(connection)}
                style={{
                  width: connection.type.includes('diagonal') ? 
                    `${Math.sqrt(Math.pow(toSection.position.x - fromSection.position.x, 2) + Math.pow(toSection.position.y - fromSection.position.y, 2))}px` :
                    `${toSection.position.x - fromSection.position.x}px`,
                  left: fromSection.position.x,
                  transform: connection.type.includes('diagonal') ? 
                    `rotate(${Math.atan2(toSection.position.y - fromSection.position.y, toSection.position.x - fromSection.position.x)}rad) translateY(-1px)` : 
                    'translateY(-1px)'
                }}
              />
              <MovingLight
                animate={getLightPosition(connection)}
                transition={{ duration: 0.1 }}
                style={{
                  top: '50%',
                  transform: 'translateY(-80%)',
                  zIndex: 3
                }}
              />
            </React.Fragment>
          );
        })}

        {sections.map((section, index) => (
          <FlowNode
            key={section.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: 1, 
              scale: 1,
              transition: {
                delay: !hasAnimated ? index * 0.2 : 0
              }
            }}
            onClick={() => setActiveSection(activeSection === section.id ? null : section.id)}
            style={{
              left: section.position.x,
              top: section.position.y,
              zIndex: 10
            }}
          >
            <NodeContent>
              <NodeTitle>{section.title}</NodeTitle>
              <AnimatePresence>
                {activeSection === section.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {section.components.map((component, idx) => (
                      <NodeSubtitle key={idx}>{component}</NodeSubtitle>
                    ))}
                    <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5, justifyContent: 'center' }}>
                      {section.tools.map((tool, idx) => (
                        <Paper
                          key={idx}
                          sx={{
                            padding: '2px 6px',
                            background: 'rgba(0,0,0,0.05)',
                            borderRadius: '4px',
                            fontSize: '0.6rem',
                          }}
                        >
                          {tool}
                        </Paper>
                      ))}
                    </Box>
                  </motion.div>
                )}
              </AnimatePresence>
            </NodeContent>
          </FlowNode>
        ))}
      </Box>
    </FlowContainer>
  );
};

export default AppFlowDiagram; 