import { useState } from 'react';
import { ChevronDown, ChevronUp, Wifi, WifiOff } from 'lucide-react';
import SensorCard, { getSensorStatus, getSensorIcon } from './SensorCard';

const DeviceCard = ({ device, data, isOnline = true }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!data || !data.sensors) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <WifiOff className="w-6 h-6 text-red-500" />
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{device}</h2>
              <p className="text-sm text-red-600">Aucune donnée disponible</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const { sensors, timestamp } = data;
  const lastUpdate = new Date(timestamp);

  const sensorConfigs = [
    { key: 'temperature', label: 'Température', unit: '°C' },
    { key: 'humidity', label: 'Humidité', unit: '%' },
    { key: 'co', label: 'Monoxyde de carbone', unit: 'ppm' },
    { key: 'lpg', label: 'Gaz LPG', unit: 'ppm' },
    { key: 'smoke', label: 'Fumée', unit: 'ppm' },
    { key: 'light', label: 'Éclairage', unit: null },
    { key: 'motion', label: 'Mouvement', unit: null }
  ];

  const getOverallStatus = () => {
    const statuses = sensorConfigs.map(config =>
      getSensorStatus(config.key, sensors[config.key])
    );

    if (statuses.includes('danger')) return 'danger';
    if (statuses.includes('warning')) return 'warning';
    return 'normal';
  };

  const overallStatus = getOverallStatus();

  const getStatusColor = (status) => {
    switch (status) {
      case 'danger':
        return 'border-red-500 bg-red-50';
      case 'warning':
        return 'border-yellow-500 bg-yellow-50';
      default:
        return 'border-green-500 bg-green-50';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'danger':
        return 'Alerte';
      case 'warning':
        return 'Attention';
      default:
        return 'Normal';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg border-l-4 ${getStatusColor(overallStatus)} transition-all duration-300`}>
      {/* En-tête du dispositif */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {isOnline ? (
              <Wifi className="w-6 h-6 text-green-500" />
            ) : (
              <WifiOff className="w-6 h-6 text-red-500" />
            )}
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Dispositif IoT
              </h2>
              <p className="text-sm text-gray-600">{device}</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className={`text-sm font-medium ${
                overallStatus === 'danger' ? 'text-red-600' :
                overallStatus === 'warning' ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {getStatusText(overallStatus)}
              </p>
              <p className="text-xs text-gray-500">
                {lastUpdate.toLocaleTimeString()}
              </p>
            </div>

            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-gray-600" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Contenu des capteurs */}
      {isExpanded && (
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {sensorConfigs.map(config => {
              const value = sensors[config.key];
              const status = getSensorStatus(config.key, value);
              const Icon = getSensorIcon(config.key);

              return (
                <SensorCard
                  key={config.key}
                  title={config.label}
                  value={value}
                  unit={config.unit}
                  icon={Icon}
                  status={status}
                />
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default DeviceCard;