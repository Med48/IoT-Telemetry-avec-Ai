import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ChartComponent = ({ data, sensors = ['temperature', 'humidity'] }) => {
  // Transformer les données pour Recharts
  const transformData = () => {
    if (!data || data.length === 0) return [];

    return data.map((item, index) => {
      const timestamp = new Date(item.timestamp);
      const point = {
        index,
        time: timestamp.toLocaleTimeString('fr-FR', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        }),
        device: item.device_id,
        fullTimestamp: timestamp
      };

      // Ajouter les valeurs des capteurs
      sensors.forEach(sensor => {
        if (item.sensors && item.sensors[sensor] !== undefined) {
          point[sensor] = item.sensors[sensor];
        }
      });

      return point;
    }).slice(-20); // Garder seulement les 20 derniers points
  };

  const chartData = transformData();

  // Configuration des couleurs pour chaque capteur
  const sensorColors = {
    temperature: '#ef4444',
    humidity: '#3b82f6',
    co: '#f59e0b',
    lpg: '#8b5cf6',
    smoke: '#6b7280'
  };

  // Configuration des unités
  const sensorUnits = {
    temperature: '°C',
    humidity: '%',
    co: 'ppm',
    lpg: 'ppm',
    smoke: 'ppm'
  };

  // Tooltip personnalisé
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900 mb-2">
            {data.time}
          </p>
          <p className="text-xs text-gray-600 mb-2">
            Dispositif: {data.device}
          </p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.dataKey}: {entry.value?.toFixed(2)} {sensorUnits[entry.dataKey] || ''}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Évolution des Capteurs
        </h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>Aucune donnée disponible pour le graphique</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Évolution des Capteurs
        </h3>
        <div className="text-sm text-gray-600">
          {chartData.length} points de données
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="time"
              stroke="#6b7280"
              fontSize={12}
              tick={{ fontSize: 11 }}
            />
            <YAxis
              stroke="#6b7280"
              fontSize={12}
              tick={{ fontSize: 11 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            {sensors.map(sensor => (
              <Line
                key={sensor}
                type="monotone"
                dataKey={sensor}
                stroke={sensorColors[sensor] || '#6b7280'}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                name={`${sensor.charAt(0).toUpperCase() + sensor.slice(1)} (${sensorUnits[sensor] || ''})`}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Légende personnalisée avec statistiques */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        {sensors.map(sensor => {
          const sensorData = chartData.map(point => point[sensor]).filter(val => val !== undefined);
          if (sensorData.length === 0) return null;

          const avg = sensorData.reduce((a, b) => a + b, 0) / sensorData.length;
          const min = Math.min(...sensorData);
          const max = Math.max(...sensorData);

          return (
            <div key={sensor} className="text-center p-3 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-medium text-gray-900 capitalize mb-1">
                {sensor}
              </h4>
              <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
                <div>
                  <p className="font-medium">Min</p>
                  <p>{min.toFixed(2)}</p>
                </div>
                <div>
                  <p className="font-medium">Moy</p>
                  <p>{avg.toFixed(2)}</p>
                </div>
                <div>
                  <p className="font-medium">Max</p>
                  <p>{max.toFixed(2)}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ChartComponent;