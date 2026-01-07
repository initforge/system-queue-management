import React from 'react';
import { motion } from 'framer-motion';
import WeeklySchedule from './components/WeeklySchedule';
import PersonalSchedule from './components/PersonalSchedule';
import { useAuth } from '../../shared/AuthContext';

const ScheduleManagement = ({ role = 'manager', staffId = null }) => {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Main Schedule Grid */}
      {role === 'manager' ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <WeeklySchedule
            departmentId={user?.department_id}
            managerId={user?.id}
            onScheduleChange={(hasChanges) => {
              // Handle schedule changes if needed
            }}
          />
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <PersonalSchedule />
        </motion.div>
      )}
    </div>
  );
};

export default ScheduleManagement;