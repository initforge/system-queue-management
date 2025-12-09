// API Services Export - Simplified
import apiService from '../../api';
import ScheduleApiService from './schedule';

// Schedule service instance
const scheduleApi = new ScheduleApiService();

// Named exports
export {
  apiService as default,
  apiService as ApiService,
  scheduleApi as ScheduleAPI,
  apiService as AuthAPI,
  apiService as TicketAPI,
  apiService as StaffAPI
};

// export { default as DepartmentService } from './departments';
// export { default as UserService } from './users';
// export { default as FeedbackService } from './feedback';