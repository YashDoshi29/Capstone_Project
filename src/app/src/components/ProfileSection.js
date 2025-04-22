import React from 'react';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import { Settings, Edit } from 'lucide-react';
import { motion } from 'framer-motion';

const ProfileSection = ({ username = 'User' }) => {
  return (
    <motion.div
      className="bg-black/50 backdrop-blur-md p-6 flex items-center justify-between rounded-xl border border-white/20 mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center gap-4">
        <motion.div
          whileHover={{ scale: 1.05 }}
          transition={{ type: 'spring', stiffness: 300, damping: 10 }}
        >
          <Avatar
            src="/placeholder.svg"
            alt={username}
            sx={{
              width: 56,
              height: 56,
              border: '2px solid rgba(124, 58, 237, 0.7)',
              boxShadow: '0 0 10px rgba(124, 58, 237, 0.3)',
            }}
          >
            {username.charAt(0)}
          </Avatar>
        </motion.div>
        <div>
          <h2 className="text-lg font-medium">{username}</h2>
          <p className="text-sm text-gray-300">Financial Profile</p>
        </div>
      </div>
      <div className="flex gap-3">
        <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
          <Button
            variant="outlined"
            size="small"
            className="bg-black/40 border-white/30 text-white hover:bg-black/60"
          >
            <Edit className="h-4 w-4" />
          </Button>
        </motion.div>
        <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
          <Button
            variant="outlined"
            size="small"
            className="bg-black/40 border-white/30 text-white hover:bg-black/60"
          >
            <Settings className="h-4 w-4" />
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ProfileSection;
