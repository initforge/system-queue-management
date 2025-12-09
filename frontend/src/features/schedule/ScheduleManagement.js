import React, { useState } from 'react';
import { motion } from 'framer-motion';
import WeeklySchedule from './components/WeeklySchedule';
import PersonalSchedule from './components/PersonalSchedule';
import { useAuth } from '../../shared/AuthContext';
import { 
  ExpandablePanel, 
  LeaveRequestPanel,
  StaffLeaveRequestPanel,
  StaffShiftExchangePanel,
  StaffStatisticsPanel,
  ManagerStatisticsPanel
} from './ExpandablePanels';

const ScheduleManagement = ({ role = 'manager', staffId = null }) => {
  const { user } = useAuth();
  const [expandedPanel, setExpandedPanel] = useState(null);

  // Manager panels
  const managerPanels = [
    {
      id: 'leave',
      icon: '📋',
      title: 'Phê duyệt đơn nghỉ phép',
      component: <LeaveRequestPanel />
    },
    {
      id: 'reports',
      icon: '📊',
      title: 'Thống kê',
      component: <ManagerStatisticsPanel />
    }
  ];

  // Staff panels
  const staffPanels = [
    {
      id: 'leave-request',
      icon: '📝',
      title: 'Xin nghỉ phép',
      component: <StaffLeaveRequestPanel />
    },
    {
      id: 'my-stats',
      icon: '📈',
      title: 'Thống kê cá nhân',
      component: <StaffStatisticsPanel staffId={staffId || user?.id} />
    }
  ];

  const panels = role === 'manager' ? managerPanels : staffPanels;

  const togglePanel = (panelId) => {
    setExpandedPanel(expandedPanel === panelId ? null : panelId);
  };

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

      {/* Feature Panels */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="space-y-4"
      >
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          {role === 'manager' ? 'Công cụ quản lý' : 'Tiện ích cho nhân viên'}
        </h3>
        
        <div className={`grid grid-cols-1 ${panels.length === 2 ? 'md:grid-cols-2' : 'md:grid-cols-3'} gap-6`}>
          {panels.map((panel, index) => (
            <motion.div
              key={panel.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
            >
              <ExpandablePanel
                icon={panel.icon}
                title={panel.title}
                isExpanded={expandedPanel === panel.id}
                onToggle={() => togglePanel(panel.id)}
              >
                {panel.component}
              </ExpandablePanel>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default ScheduleManagement;