import { useState, useEffect } from 'react';
import { useIoTData } from '../hooks/useIoTData';
import StatusBar from './StatusBar';
import DeviceCard from './DeviceCard';
import ChartComponent from './ChartComponent';
import { BarChart3, Settings, Download } from 'lucide-react';

const Dashboard = () => {
  const { data, status, loading, error, lastUpdate, refresh } = useIoTData(3000);
  const [selectedDevice, setSelectedDevice] = useState('all');
  const [selectedSensors, setSelectedSensors] = useState(['temperature', 'humidity']);

  // Grouper les données par dispositif
  const groupDataByDevice = () => {
    if (!data || data.length === 0) return {};

    const grouped = {};
    data.forEach(item => {
      if (!grouped[item.device_id]) {
        grouped[item.device_id] = [];
      }
      grouped[item.device_id].push(item);
    });

    // Trier chaque groupe par timestamp (plus récent en premier)
    Object.keys(grouped).forEach(device => {
      grouped[device].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    });

    return grouped;
  };

  const groupedData = groupDataByDevice();
  const devices = Object.keys(groupedData);

  // Obtenir les données à afficher dans le graphique
  const getChartData = () => {
    if (selectedDevice === 'all') {
      return data.slice(-20); // 20 derniers points de tous les dispositifs
    }
    return groupedData[selectedDevice]?.slice(-20) || [];
  };

  // Obtenir les capteurs disponibles
  const availableSensors = data.length > 0 && data[0].sensors
    ? Object.keys(data[0].sensors).filter(sensor => typeof data[0].sensors[sensor] === 'number')
    : [];

  const handleSensorToggle = (sensor) => {
    setSelectedSensors(prev =>
      prev.includes(sensor)
        ? prev.filter(s => s !== sensor)
        : [...prev, sensor]
    );
  };

  const getOverallStats = () => {
    if (!data || data.length === 0) return null;

    const totalDevices = devices.length;
    const totalSamples = data.length;
    const lastSample = data[data.length - 1];

    // Calculer les alertes (exemple simple)
    let alerts = 0;
    data.forEach(item => {
      if (item.sensors.temperature > 30 || item.sensors.co > 0.01) {
        alerts++;
      }
    });

    return {
      totalDevices,
      totalSamples,
      alerts,
      lastSample
    };
  };

  const stats = getOverallStats();

  if (loading && data.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement du dashboard IoT...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
                <BarChart3 className="w-8 h-8 text-blue-600" />
                <span>Dashboard IoT Telemetry</span>
              </h1>
              <p className="text-gray-600 mt-2">
                Surveillance en temps réel des capteurs environnementaux
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => window.location.reload()}
                className="flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <Settings className="w-4 h-4" />
                <span className="text-sm">Configuration</span>
              </button>
            </div>
          </div>
        </div>

        {/* Barre de statut */}
        <StatusBar
          status={status}
          lastUpdate={lastUpdate}
          onRefresh={refresh}
          isLoading={loading}
          error={error}
        />

        {/* Statistiques générales */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-blue-600">{stats.totalDevices}</h3>
              <p className="text-gray-600">Dispositifs</p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-green-600">{stats.totalSamples}</h3>
              <p className="text-gray-600">Échantillons</p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-red-600">{stats.alerts}</h3>
              <p className="text-gray-600">Alertes</p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-purple-600">
                {status?.is_running ? 'Actif' : 'Arrêté'}
              </h3>
              <p className="text-gray-600">État</p>
            </div>
          </div>
        )}

        {/* Contrôles du graphique */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* Sélecteur de dispositif */}
            <div className="flex items-center space-x-3">
              <label className="text-sm font-medium text-gray-700">Dispositif:</label>
              <select
                value={selectedDevice}
                onChange={(e) => setSelectedDevice(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Tous les dispositifs</option>
                {devices.map(device => (
                  <option key={device} value={device}>{device}</option>
                ))}
              </select>
            </div>

            {/* Sélecteur de capteurs */}
            <div className="flex items-center space-x-3">
              <label className="text-sm font-medium text-gray-700">Capteurs:</label>
              <div className="flex flex-wrap gap-2">
                {availableSensors.map(sensor => (
                  <button
                    key={sensor}
                    onClick={() => handleSensorToggle(sensor)}
                    className={`px-3 py-1 text-xs rounded-full transition-colors ${
                      selectedSensors.includes(sensor)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {sensor}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Graphique */}
        <div className="mb-6">
          <ChartComponent
            data={getChartData()}
            sensors={selectedSensors}
          />
        </div>

        {/* Cartes des dispositifs */}
        <div className="space-y-6">
          {devices.length > 0 ? devices.map(device => {
            const deviceData = groupedData[device];
            const latestData = deviceData[0]; // Plus récent en premier

            return (
              <DeviceCard
                key={device}
                device={device}
                data={latestData}
                isOnline={true}
              />
            );
          }) : (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <p className="text-gray-600">Aucun dispositif détecté</p>
              <p className="text-sm text-gray-500 mt-2">
                Vérifiez que le simulateur IoT est en cours d'exécution
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Dashboard IoT Telemetry - Données en temps réel</p>
          {lastUpdate && (
            <p>Dernière mise à jour: {lastUpdate.toLocaleString()}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;