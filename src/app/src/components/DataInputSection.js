import React from 'react';
import { motion } from 'framer-motion';
import TextField from '@mui/material/TextField';
import { CalendarClock, Users, CreditCard, User as UserIcon } from 'lucide-react';

const DataInputSection = ({ userData, onDataChange }) => {
  const handleChange = (e, field) => {
    onDataChange(field, e.target.value);
  };

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };

  const item = { hidden: { y: 20, opacity: 0 }, show: { y: 0, opacity: 1 } };

  // Use sx prop for dark TextField styling
  const textFieldStyles = {
    input: {
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      color: '#ffffff',
    },
    fieldset: {
      borderColor: 'rgba(255, 255, 255, 0.3)',
    },
    '&:hover fieldset': {
      borderColor: '#7c3aed', // Accent color on hover
    },
  };

  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-2 gap-6"
      variants={container}
      initial="hidden"
      animate="show"
    >
      {/* Age Field */}
      <motion.div variants={item}>
        <div className="flex items-center gap-3 mb-2">
          <CalendarClock className="h-5 w-5 text-white" />
          <span className="text-lg font-medium">Age</span>
        </div>
        <TextField
          id="age"
          type="number"
          placeholder="Enter your age"
          value={userData.age}
          onChange={(e) => handleChange(e, 'age')}
          variant="outlined"
          fullWidth
          sx={textFieldStyles}
        />
      </motion.div>

      {/* Gender Field */}
      <motion.div variants={item}>
        <div className="flex items-center gap-3 mb-2">
          <UserIcon className="h-5 w-5 text-white" />
          <span className="text-lg font-medium">Gender</span>
        </div>
        <TextField
          id="gender"
          placeholder="Enter your gender"
          value={userData.gender}
          onChange={(e) => handleChange(e, 'gender')}
          variant="outlined"
          fullWidth
          sx={textFieldStyles}
        />
      </motion.div>

      {/* Household Size Field */}
      <motion.div variants={item}>
        <div className="flex items-center gap-3 mb-2">
          <Users className="h-5 w-5 text-white" />
          <span className="text-lg font-medium">Household Size</span>
        </div>
        <TextField
          id="householdSize"
          type="number"
          placeholder="Enter household size"
          value={userData.householdSize}
          onChange={(e) => handleChange(e, 'householdSize')}
          variant="outlined"
          fullWidth
          sx={textFieldStyles}
        />
      </motion.div>

      {/* Annual Income Field */}
      <motion.div variants={item}>
        <div className="flex items-center gap-3 mb-2">
          <CreditCard className="h-5 w-5 text-white" />
          <span className="text-lg font-medium">Annual Income</span>
        </div>
        <TextField
          id="annualIncome"
          type="number"
          placeholder="Enter annual income"
          value={userData.annualIncome}
          onChange={(e) => handleChange(e, 'annualIncome')}
          variant="outlined"
          fullWidth
          sx={textFieldStyles}
        />
      </motion.div>
    </motion.div>
  );
};

export default DataInputSection;
