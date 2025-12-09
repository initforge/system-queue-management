import React from 'react';
import Card from './Card';

const StatCard = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color = 'blue',
  trend = null,
  className = '' 
}) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600'
  };
  
  const getTrendColor = (trend) => {
    if (!trend) return '';
    return trend.direction === 'up' ? 'text-green-600' : 'text-red-600';
  };
  
  const getTrendIcon = (trend) => {
    if (!trend) return null;
    return trend.direction === 'up' ? '↗️' : '↘️';
  };
  
  return (
    <Card className={className} hover>
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <span className="text-2xl">{icon}</span>
        </div>
        <div className="ml-4 flex-1">
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          <div className="text-sm font-medium text-gray-600">{title}</div>
          {subtitle && (
            <div className="text-xs text-gray-500 flex items-center gap-2">
              {subtitle}
              {trend && (
                <span className={`flex items-center ${getTrendColor(trend)}`}>
                  {getTrendIcon(trend)} {trend.value}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default StatCard;