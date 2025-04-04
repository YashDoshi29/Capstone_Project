import React from 'react';
import Button from '@mui/material/Button';
import { motion } from 'framer-motion';
import { Brain, Database, Sparkles } from 'lucide-react';

const ModelSelector = ({ selectedModel, onSelectModel }) => {
  return (
    <motion.div
      className="bg-black/50 backdrop-blur-md p-6 rounded-xl border border-white/20 mb-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <div className="flex items-center justify-center gap-3 mb-6">
        <Sparkles className="h-5 w-5 text-white" />
        <h2 className="text-xl font-semibold text-white">Select Generation Model</h2>
        <Sparkles className="h-5 w-5 text-white" />
      </div>
      <div className="flex gap-6 justify-center">
        <motion.div className="flex-1" whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }}>
          <Button
            variant={selectedModel === 'GAN' ? 'contained' : 'outlined'}
            className={`w-full py-6 ${
              selectedModel === 'GAN'
                ? 'bg-purple-600 hover:bg-purple-700 text-white border border-purple-500'
                : 'bg-black/40 hover:bg-black/50 border-white/30 text-white'
            }`}
            onClick={() => onSelectModel('GAN')}
          >
            <div className="flex flex-col items-center gap-3">
              <Database className={`h-8 w-8 ${selectedModel === 'GAN' ? 'text-white' : 'text-purple-300'}`} />
              <span className="text-lg">GAN Model</span>
              <p className="text-xs opacity-70 mt-1">Generative Adversarial Network</p>
            </div>
          </Button>
        </motion.div>
        <motion.div className="flex-1" whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }}>
          <Button
            variant={selectedModel === 'LLM' ? 'contained' : 'outlined'}
            className={`w-full py-6 ${
              selectedModel === 'LLM'
                ? 'bg-purple-600 hover:bg-purple-700 text-white border border-purple-500'
                : 'bg-black/40 hover:bg-black/50 border-white/30 text-white'
            }`}
            onClick={() => onSelectModel('LLM')}
          >
            <div className="flex flex-col items-center gap-3">
              <Brain className={`h-8 w-8 ${selectedModel === 'LLM' ? 'text-white' : 'text-purple-300'}`} />
              <span className="text-lg">LLM Model</span>
              <p className="text-xs opacity-70 mt-1">Large Language Model</p>
            </div>
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ModelSelector;
