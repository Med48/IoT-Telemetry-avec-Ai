import { Thermometer, Droplets, Wind, Lightbulb, Activity } from 'lucide-react';

const SensorCard = ({ title, value, unit, icon: Icon, status = 'normal', trend }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'danger':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  const getStatusDot = (status) => {
    switch (status) {
      case 'warning':
        return 'bg-yellow-500';
      case 'danger':
        return 'bg-red-500';
      default:
        return 'bg-green-500';
    }
  };

  const formatValue = (value) => {
    if (typeof value === 'boolean') {
      return value ? 'Activé' : 'Désactivé';
    }
    if (typeof value === 'number') {
      return value.toFixed(2);
    }
    return value;
  };

  const getTrendIcon = (trend) => {
    if (!trend) return null;
    if (trend > 0) return '↗';
    if (trend < 0) return '↙';
    return '→';
  };

  return (
    <div className={`sensor-card border ${getStatusColor(status)}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {Icon && <Icon className="w-5 h-5" />}
          <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        </div>
        <span className={`inline-block w-3 h-3 rounded-full ${getStatusDot(status)}`}></span>
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold text-gray-900">
          {formatValue(value)}
        </span>
        {unit && (
          <span className="text-sm text-gray-500">{unit}</span>
        )}
        {trend !== undefined && (
          <span className={`text-sm ${trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600'}`}>
            {getTrendIcon(trend)}
          </span>
        )}
      </div>

      {typeof value === 'number' && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                status === 'danger' ? 'bg-red-500' :
                status === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(Math.max(value / 100 * 100, 0), 100)}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};

// Fonction utilitaire pour déterminer le statut d'un capteur
export const getSensorStatus = (sensorType, value) => {
  switch (sensorType) {
    case 'temperature':
      if (value > 30 || value < 10) return 'danger';
      if (value > 28 || value < 15) return 'warning';
      return 'normal';

    case 'humidity':
      if (value > 80 || value < 20) return 'danger';
      if (value > 70 || value < 30) return 'warning';
      return 'normal';

    case 'co':
    case 'lpg':
    case 'smoke':
      if (value > 0.01) return 'danger';
      if (value > 0.007) return 'warning';
      return 'normal';

    default:
      return 'normal';
  }
};

// Fonction utilitaire pour obtenir l'icône appropriée
export const getSensorIcon = (sensorType) => {
  switch (sensorType) {
    case 'temperature':
      return Thermometer;
    case 'humidity':
      return Droplets;
    case 'co':
    case 'lpg':
    case 'smoke':
      return Wind;
    case 'light':
      return Lightbulb;
    case 'motion':
      return Activity;
    default:
      return Activity;
  }
};

export default SensorCard;