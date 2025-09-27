import { useState, useEffect } from 'react';

const Dashboard = () => {
  const [devicesData, setDevicesData] = useState(null);
  const [latestData, setLatestData] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Récupérer les données des dispositifs
        const devicesResponse = await fetch('http://localhost:5000/api/devices');
        const devicesResult = await devicesResponse.json();

        // Récupérer les dernières données
        const latestResponse = await fetch(`http://localhost:5000/api/latest?n=20`);
        const latestResult = await latestResponse.json();

        // Récupérer les données historiques des dernières 24h
        const historicalResponse = await fetch(`http://localhost:5000/api/historical?hours=24`);
        const historicalResult = await historicalResponse.json();

        if (devicesResult.success) {
          setDevicesData(devicesResult.devices);
        }

        if (latestResult.success) {
          setLatestData(latestResult.data);
        }

        if (historicalResult.success) {
          setHistoricalData(historicalResult.data);
        }

        setLoading(false);
      } catch (error) {
        console.error('Erreur de chargement:', error);
        setError('Erreur de connexion au serveur CSV');
        setLoading(false);
      }
    };

    fetchData();
    // Refresh every 30 seconds for CSV data
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Calculer les alertes basées sur les seuils
  const calculateAlerts = () => {
    if (!latestData.length) return { critical: 0, warning: 0, normal: 0 };

    let critical = 0, warning = 0, normal = 0;

    latestData.forEach(sample => {
      const temp = sample.sensors.temperature;
      const co = sample.sensors.co;
      const smoke = sample.sensors.smoke;

      if (temp > 30 || co > 0.01 || smoke > 0.02) {
        critical++;
      } else if (temp > 25 || co > 0.005 || smoke > 0.015) {
        warning++;
      } else {
        normal++;
      }
    });

    return { critical, warning, normal };
  };

  // Calculer les tendances (simulation simple)
  const calculateTrends = () => {
    if (!historicalData.length) return {};

    const recent = historicalData.slice(-50);
    const older = historicalData.slice(-100, -50);

    if (!recent.length || !older.length) return {};

    const recentAvg = {
      temp: recent.reduce((sum, d) => sum + d.sensors.temperature, 0) / recent.length,
      humidity: recent.reduce((sum, d) => sum + d.sensors.humidity, 0) / recent.length,
      co: recent.reduce((sum, d) => sum + d.sensors.co, 0) / recent.length
    };

    const olderAvg = {
      temp: older.reduce((sum, d) => sum + d.sensors.temperature, 0) / older.length,
      humidity: older.reduce((sum, d) => sum + d.sensors.humidity, 0) / older.length,
      co: older.reduce((sum, d) => sum + d.sensors.co, 0) / older.length
    };

    return {
      temperature: ((recentAvg.temp - olderAvg.temp) / olderAvg.temp * 100).toFixed(1),
      humidity: ((recentAvg.humidity - olderAvg.humidity) / olderAvg.humidity * 100).toFixed(1),
      co: ((recentAvg.co - olderAvg.co) / olderAvg.co * 100).toFixed(1)
    };
  };

  const alerts = calculateAlerts();
  const trends = calculateTrends();

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f3f4f6',
        padding: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#6b7280' }}>Chargement des données CSV...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f3f4f6',
        padding: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '32px',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          textAlign: 'center',
          maxWidth: '500px'
        }}>
          <h2 style={{ color: '#ef4444', marginBottom: '16px' }}>Erreur de connexion</h2>
          <p style={{ color: '#6b7280', marginBottom: '16px' }}>{error}</p>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>
            Vérifiez que le serveur CSV est démarré sur le port 5000
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6', padding: '24px' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>

        {/* En-tête */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            color: '#111827',
            marginBottom: '8px'
          }}>
            📊 Dashboard IoT - Données Historiques
          </h1>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>
            Analyse en temps réel des 405,184 échantillons IoT (Juillet 2020)
          </p>
        </div>

        {/* Métriques principales */}
        {devicesData && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '24px',
            marginBottom: '32px'
          }}>
            <div style={{
              backgroundColor: 'white',
              padding: '24px',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              borderLeft: '4px solid #3b82f6'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '32px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
                    {Object.keys(devicesData).length}
                  </h3>
                  <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Dispositifs Actifs</p>
                  <p style={{ color: '#10b981', fontSize: '12px', margin: '4px 0 0 0' }}>
                    📡 Tous connectés
                  </p>
                </div>
                <span style={{ fontSize: '40px' }}>🖥️</span>
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              padding: '24px',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              borderLeft: '4px solid #10b981'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: 0 }}>
                    {Object.values(devicesData).reduce((sum, device) => sum + device.statistics.total_samples, 0).toLocaleString()}
                  </h3>
                  <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Échantillons Analysés</p>
                  <p style={{ color: '#10b981', fontSize: '12px', margin: '4px 0 0 0' }}>
                    ✅ 100% qualité données
                  </p>
                </div>
                <span style={{ fontSize: '40px' }}>📈</span>
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              padding: '24px',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              borderLeft: '4px solid #f59e0b'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: 0 }}>
                    {alerts.warning + alerts.critical}
                  </h3>
                  <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Alertes Détectées</p>
                  <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>
                    🚨 {alerts.critical} critiques, ⚠️ {alerts.warning} warnings
                  </p>
                </div>
                <span style={{ fontSize: '40px' }}>⚠️</span>
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              padding: '24px',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              borderLeft: '4px solid #8b5cf6'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '32px', fontWeight: 'bold', color: '#8b5cf6', margin: 0 }}>
                    8 jours
                  </h3>
                  <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Période Historique</p>
                  <p style={{ color: '#8b5cf6', fontSize: '12px', margin: '4px 0 0 0' }}>
                    📅 12-20 Juillet 2020
                  </p>
                </div>
                <span style={{ fontSize: '40px' }}>⏱️</span>
              </div>
            </div>
          </div>
        )}

        {/* Tendances et Insights */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 'bold',
              color: '#111827',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              📊 Tendances Récentes
            </h3>
            <div style={{ space: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ color: '#6b7280', fontSize: '14px' }}>🌡️ Température</span>
                <span style={{
                  color: trends.temperature > 0 ? '#ef4444' : '#10b981',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  {trends.temperature > 0 ? '↗️' : '↘️'} {Math.abs(trends.temperature)}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ color: '#6b7280', fontSize: '14px' }}>💧 Humidité</span>
                <span style={{
                  color: trends.humidity > 0 ? '#3b82f6' : '#f59e0b',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  {trends.humidity > 0 ? '↗️' : '↘️'} {Math.abs(trends.humidity)}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#6b7280', fontSize: '14px' }}>💨 CO</span>
                <span style={{
                  color: trends.co > 0 ? '#ef4444' : '#10b981',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  {trends.co > 0 ? '↗️' : '↘️'} {Math.abs(trends.co)}%
                </span>
              </div>
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 'bold',
              color: '#111827',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              🎯 Statut des Capteurs
            </h3>
            <div style={{ space: '12px' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '8px',
                backgroundColor: '#dcfce7',
                borderRadius: '6px',
                marginBottom: '8px'
              }}>
                <span style={{ color: '#166534', fontSize: '14px' }}>✅ Normaux</span>
                <span style={{ color: '#166534', fontWeight: 'bold' }}>{alerts.normal}</span>
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '8px',
                backgroundColor: '#fef3c7',
                borderRadius: '6px',
                marginBottom: '8px'
              }}>
                <span style={{ color: '#92400e', fontSize: '14px' }}>⚠️ Attention</span>
                <span style={{ color: '#92400e', fontWeight: 'bold' }}>{alerts.warning}</span>
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '8px',
                backgroundColor: '#fecaca',
                borderRadius: '6px'
              }}>
                <span style={{ color: '#991b1b', fontSize: '14px' }}>🚨 Critiques</span>
                <span style={{ color: '#991b1b', fontWeight: 'bold' }}>{alerts.critical}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Cartes des dispositifs avec plus de détails */}
        {devicesData && (
          <div style={{ marginBottom: '32px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827', marginBottom: '16px' }}>
              🖥️ Analyse par Dispositif
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '24px'
            }}>
              {Object.entries(devicesData).map(([deviceId, deviceInfo], index) => {
                const colors = ['#3b82f6', '#10b981', '#8b5cf6'];
                const deviceColor = colors[index % colors.length];

                return (
                  <div key={deviceId} style={{
                    backgroundColor: 'white',
                    padding: '24px',
                    borderRadius: '12px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    borderLeft: `4px solid ${deviceColor}`
                  }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '16px'
                    }}>
                      <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>
                        🖥️ Dispositif {index + 1}
                      </h3>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <div style={{
                          width: '8px',
                          height: '8px',
                          backgroundColor: '#10b981',
                          borderRadius: '50%'
                        }}></div>
                        <span style={{ fontSize: '12px', color: '#10b981' }}>Actif</span>
                      </div>
                    </div>

                    <p style={{
                      fontSize: '11px',
                      color: '#6b7280',
                      fontFamily: 'monospace',
                      marginBottom: '16px',
                      wordBreak: 'break-all'
                    }}>
                      {deviceId}
                    </p>

                    {/* Statistiques du dispositif */}
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: '12px',
                      marginBottom: '16px'
                    }}>
                      <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#f8fafc', borderRadius: '6px' }}>
                        <p style={{ fontSize: '20px', fontWeight: 'bold', color: deviceColor, margin: 0 }}>
                          {deviceInfo.statistics.total_samples.toLocaleString()}
                        </p>
                        <p style={{ fontSize: '12px', color: '#6b7280', margin: '2px 0 0 0' }}>Échantillons</p>
                      </div>
                      <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#f8fafc', borderRadius: '6px' }}>
                        <p style={{ fontSize: '20px', fontWeight: 'bold', color: deviceColor, margin: 0 }}>
                          {Math.round((deviceInfo.statistics.total_samples / 405184) * 100)}%
                        </p>
                        <p style={{ fontSize: '12px', color: '#6b7280', margin: '2px 0 0 0' }}>Du total</p>
                      </div>
                    </div>

                    {/* Capteurs avec valeurs comparées aux moyennes */}
                    <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '16px', marginBottom: '16px' }}>
                      <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '12px' }}>
                        📊 Valeurs Actuelles vs Moyennes
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                        {Object.entries(deviceInfo.latest_data.sensors).map(([sensor, current]) => {
                          if (typeof current !== 'number') return null;
                          const average = deviceInfo.statistics.averages[sensor];
                          const diff = ((current - average) / average * 100).toFixed(1);
                          const isHigh = current > average;

                          return (
                            <div key={sensor} style={{
                              padding: '8px',
                              backgroundColor: '#f9fafb',
                              borderRadius: '4px'
                            }}>
                              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '2px' }}>
                                {sensor === 'temperature' ? '🌡️' : sensor === 'humidity' ? '💧' :
                                 sensor === 'co' ? '💨' : sensor === 'smoke' ? '🔥' : '📊'} {sensor}
                              </div>
                              <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#111827' }}>
                                {current.toFixed(sensor === 'temperature' || sensor === 'humidity' ? 1 : 4)}
                                {sensor === 'temperature' ? '°C' : sensor === 'humidity' ? '%' : ''}
                              </div>
                              <div style={{
                                fontSize: '11px',
                                color: isHigh ? '#ef4444' : '#10b981'
                              }}>
                                {isHigh ? '↗️' : '↘️'} {Math.abs(diff)}% vs moy.
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Dernière mise à jour */}
                    <div style={{ fontSize: '12px', color: '#6b7280', textAlign: 'center' }}>
                      Dernière mesure: {new Date(deviceInfo.latest_data.timestamp).toLocaleString('fr-FR')}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Dernières mesures avec analyse */}
        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', marginBottom: '16px' }}>
            📋 Dernières Mesures - Analyse Détaillée
          </h2>

          {latestData.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f9fafb' }}>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>
                      ⏰ Timestamp
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>
                      🖥️ Dispositif
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>
                      🌡️ Temp.
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>
                      💧 Humid.
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>
                      💨 CO
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>
                      🔥 Fumée
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>
                      ⚠️ Statut
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {latestData.slice(-8).reverse().map((sample, index) => {
                    const temp = sample.sensors.temperature;
                    const co = sample.sensors.co;
                    const smoke = sample.sensors.smoke;

                    let status = { text: '✅ Normal', color: '#10b981' };
                    if (temp > 30 || co > 0.01 || smoke > 0.02) {
                      status = { text: '🚨 Critique', color: '#ef4444' };
                    } else if (temp > 25 || co > 0.005 || smoke > 0.015) {
                      status = { text: '⚠️ Attention', color: '#f59e0b' };
                    }

                    return (
                      <tr key={index} style={{
                        borderTop: '1px solid #e5e7eb',
                        backgroundColor: status.color === '#ef4444' ? '#fef2f2' :
                                        status.color === '#f59e0b' ? '#fffbeb' : 'white'
                      }}>
                        <td style={{ padding: '12px', fontSize: '12px', color: '#111827' }}>
                          {new Date(sample.timestamp).toLocaleString('fr-FR')}
                        </td>
                        <td style={{ padding: '12px', fontSize: '12px', color: '#6b7280', fontFamily: 'monospace' }}>
                          ...{sample.device_id.slice(-6)}
                        </td>
                        <td style={{
                          padding: '12px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: temp > 30 ? '#ef4444' : temp > 25 ? '#f59e0b' : '#10b981'
                        }}>
                          {temp.toFixed(1)}°C
                        </td>
                        <td style={{ padding: '12px', fontSize: '14px', fontWeight: '500', color: '#3b82f6' }}>
                          {sample.sensors.humidity.toFixed(1)}%
                        </td>
                        <td style={{
                          padding: '12px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: co > 0.01 ? '#ef4444' : co > 0.005 ? '#f59e0b' : '#10b981'
                        }}>
                          {co.toFixed(4)}
                        </td>
                        <td style={{
                          padding: '12px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: smoke > 0.02 ? '#ef4444' : smoke > 0.015 ? '#f59e0b' : '#10b981'
                        }}>
                          {smoke.toFixed(4)}
                        </td>
                        <td style={{
                          padding: '12px',
                          fontSize: '12px',
                          fontWeight: '500',
                          color: status.color
                        }}>
                          {status.text}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: '#6b7280', textAlign: 'center', padding: '32px' }}>
              Aucune donnée disponible
            </p>
          )}
        </div>

        {/* Footer */}
        <div style={{
          marginTop: '32px',
          textAlign: 'center',
          fontSize: '14px',
          color: '#6b7280'
        }}>
          <p>📊 Dashboard IoT Telemetry - Données CSV Historiques Analysées</p>
          <p>🔄 Dernière mise à jour: {new Date().toLocaleString('fr-FR')}</p>
          <p>📈 Seuils: Température >25°C (⚠️) >30°C (🚨) | CO >0.005 (⚠️) >0.01 (🚨) | Fumée >0.015 (⚠️) >0.02 (🚨)</p>
        </div>

        {/* Animation CSS pour le spinner */}
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
};

export default Dashboard;