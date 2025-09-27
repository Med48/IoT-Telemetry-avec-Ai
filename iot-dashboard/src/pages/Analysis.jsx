import { useState, useEffect } from 'react';

const Analysis = () => {
  const [stats, setStats] = useState(null);
  const [mlResults, setMlResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysisData = async () => {
      try {
        // Récupérer les statistiques
        const statsResponse = await fetch('http://localhost:5000/api/status');
        const statsData = await statsResponse.json();

        // Récupérer les résultats ML
        const mlResponse = await fetch('http://localhost:5000/api/ml-results');
        const mlData = await mlResponse.json();

        setStats(statsData.statistics);
        setMlResults(mlData.results);
        setLoading(false);
      } catch (error) {
        console.error('Erreur de chargement:', error);
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, []);

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
          <p style={{ color: '#6b7280' }}>Chargement de l'analyse...</p>
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
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '8px'
          }}>
            <span style={{ fontSize: '32px' }}>📈</span>
            <span>Analyse Avancée des Données IoT</span>
          </h1>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>
            Analyse statistique, ML et visualisations des 405,184 échantillons CSV
          </p>
        </div>

        {/* Résumé exécutif */}
        {stats && mlResults && (
          <div style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            marginBottom: '32px',
            borderLeft: '4px solid #3b82f6'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: 'bold',
              color: '#111827',
              marginBottom: '16px'
            }}>
              📊 Résumé Exécutif de l'Analyse
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px'
            }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                <h3 style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
                  {stats.total_samples?.toLocaleString()}
                </h3>
                <p style={{ color: '#6b7280', margin: '4px 0 0 0', fontSize: '14px' }}>Échantillons Analysés</p>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
                <h3 style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981', margin: 0 }}>
                  {mlResults.anomaly_detection.anomaly_rate}%
                </h3>
                <p style={{ color: '#6b7280', margin: '4px 0 0 0', fontSize: '14px' }}>Taux d'Anomalies</p>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fefce8', borderRadius: '8px' }}>
                <h3 style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b', margin: 0 }}>
                  {Math.round(mlResults.prediction_model.accuracy * 100)}%
                </h3>
                <p style={{ color: '#6b7280', margin: '4px 0 0 0', fontSize: '14px' }}>Précision Prédiction</p>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f5f3ff', borderRadius: '8px' }}>
                <h3 style={{ fontSize: '24px', fontWeight: 'bold', color: '#8b5cf6', margin: 0 }}>
                  {stats.date_range?.duration_days}
                </h3>
                <p style={{ color: '#6b7280', margin: '4px 0 0 0', fontSize: '14px' }}>Jours Analysés</p>
              </div>
            </div>
          </div>
        )}

        {/* Statistiques générales */}
        {stats && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '24px',
            marginBottom: '32px'
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              padding: '24px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <h3 style={{
                    fontSize: '28px',
                    fontWeight: 'bold',
                    color: '#3b82f6',
                    margin: 0
                  }}>
                    {stats.total_samples?.toLocaleString()}
                  </h3>
                  <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Échantillons Total</p>
                  <p style={{ color: '#10b981', fontSize: '12px', margin: '4px 0 0 0' }}>
                    ✅ Qualité: {stats.data_quality?.data_completeness}%
                  </p>
                </div>
                <span style={{ fontSize: '32px' }}>🗄️</span>
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              padding: '24px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <h3 style={{
                    fontSize: '28px',
                    fontWeight: 'bold',
                    color: '#10b981',
                    margin: 0
                  }}>
                    {stats.devices_count}
                  </h3>
                  <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Dispositifs IoT</p>
                  <p style={{ color: '#10b981', fontSize: '12px', margin: '4px 0 0 0' }}>
                    📡 Tous opérationnels
                  </p>
                </div>
                <span style={{ fontSize: '32px' }}>📡</span>
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              padding: '24px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <h3 style={{
                    fontSize: '28px',
                    fontWeight: 'bold',
                    color: '#8b5cf6',
                    margin: 0
                  }}>
                    {stats.date_range?.duration_days}
                  </h3>
                  <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>Jours de Données</p>
                  <p style={{ color: '#8b5cf6', fontSize: '12px', margin: '4px 0 0 0' }}>
                    📅 12-20 Juillet 2020
                  </p>
                </div>
                <span style={{ fontSize: '32px' }}>📅</span>
              </div>
            </div>
          </div>
        )}

        {/* Visualisations avec vraies images */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          padding: '24px',
          marginBottom: '32px'
        }}>
          <h2 style={{
            fontSize: '20px',
            fontWeight: 'bold',
            marginBottom: '16px',
            color: '#111827'
          }}>
            📊 Visualisations Générées par l'Analyse Python
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '24px'
          }}>
            <div style={{
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <h3 style={{
                fontWeight: 'bold',
                color: '#111827',
                marginBottom: '8px'
              }}>
                📈 Distribution des Capteurs
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                marginBottom: '16px'
              }}>
                Histogrammes montrant la distribution statistique de chaque capteur
              </p>
              <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '4px',
                padding: '8px',
                textAlign: 'center',
                minHeight: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <img
                  src="http://localhost:5000/api/images/distribution_capteurs.png"
                  alt="Distribution des capteurs"
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '4px'
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <div style={{
                  display: 'none',
                  color: '#6b7280',
                  fontSize: '14px',
                  textAlign: 'center'
                }}>
                  📊 distribution_capteurs.png<br />
                  <span style={{ fontSize: '12px' }}>
                    Image générée par data_analysis_clean.py
                  </span>
                </div>
              </div>
            </div>

            <div style={{
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <h3 style={{
                fontWeight: 'bold',
                color: '#111827',
                marginBottom: '8px'
              }}>
                ⏱️ Évolution Temporelle
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                marginBottom: '16px'
              }}>
                Tendances et patterns temporels des mesures IoT
              </p>
              <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '4px',
                padding: '8px',
                textAlign: 'center',
                minHeight: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <img
                  src="http://localhost:5000/api/images/evolution_temporelle.png"
                  alt="Evolution temporelle"
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '4px'
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <div style={{
                  display: 'none',
                  color: '#6b7280',
                  fontSize: '14px',
                  textAlign: 'center'
                }}>
                  📈 evolution_temporelle.png<br />
                  <span style={{ fontSize: '12px' }}>
                    Image générée par data_analysis_clean.py
                  </span>
                </div>
              </div>
            </div>

            <div style={{
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <h3 style={{
                fontWeight: 'bold',
                color: '#111827',
                marginBottom: '8px'
              }}>
                🔗 Matrice de Corrélation
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                marginBottom: '16px'
              }}>
                Corrélations entre les différents capteurs et leurs interactions
              </p>
              <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '4px',
                padding: '8px',
                textAlign: 'center',
                minHeight: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <img
                  src="http://localhost:5000/api/images/correlation_matrix.png"
                  alt="Matrice de correlation"
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '4px'
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <div style={{
                  display: 'none',
                  color: '#6b7280',
                  fontSize: '14px',
                  textAlign: 'center'
                }}>
                  🔗 correlation_matrix.png<br />
                  <span style={{ fontSize: '12px' }}>
                    Image générée par data_analysis_clean.py
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Résultats des modèles ML */}
        {mlResults && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
            gap: '24px',
            marginBottom: '32px'
          }}>
            {/* Détection d'anomalies */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              padding: '24px',
              borderLeft: '4px solid #ef4444'
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: 'bold',
                marginBottom: '16px',
                color: '#111827',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                🚨 Détection d'Anomalies - {mlResults.anomaly_detection.model_type}
              </h2>

              <div style={{ marginBottom: '16px' }}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '12px',
                  marginBottom: '16px'
                }}>
                  <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#fef2f2', borderRadius: '6px' }}>
                    <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#ef4444', margin: 0 }}>
                      {mlResults.anomaly_detection.anomalies_detected.toLocaleString()}
                    </h3>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '2px 0 0 0' }}>Anomalies Détectées</p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#fef2f2', borderRadius: '6px' }}>
                    <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#ef4444', margin: 0 }}>
                      {mlResults.anomaly_detection.anomaly_rate}%
                    </h3>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '2px 0 0 0' }}>Taux d'Anomalies</p>
                  </div>
                </div>

                <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                  📊 Performance du Modèle
                </h4>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>Précision:</span>
                    <span style={{ fontWeight: 'bold', color: '#10b981' }}>
                      {Math.round(mlResults.anomaly_detection.performance.precision * 100)}%
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>Rappel:</span>
                    <span style={{ fontWeight: 'bold', color: '#3b82f6' }}>
                      {Math.round(mlResults.anomaly_detection.performance.recall * 100)}%
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>F1-Score:</span>
                    <span style={{ fontWeight: 'bold', color: '#8b5cf6' }}>
                      {Math.round(mlResults.anomaly_detection.performance.f1_score * 100)}%
                    </span>
                  </div>
                </div>

                <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                  🎯 Caractéristiques Anomales Principales
                </h4>
                <div style={{ space: '8px' }}>
                  {mlResults.anomaly_detection.top_anomalous_features.map((feature, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '6px 8px',
                      backgroundColor: '#f9fafb',
                      borderRadius: '4px',
                      marginBottom: '4px'
                    }}>
                      <span style={{ fontSize: '13px', color: '#6b7280' }}>
                        {feature.feature === 'temperature' ? '🌡️' :
                         feature.feature === 'co' ? '💨' :
                         feature.feature === 'smoke' ? '🔥' : '💧'} {feature.feature}
                      </span>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#ef4444' }}>
                          {Math.round(feature.importance * 100)}%
                        </div>
                        <div style={{ fontSize: '10px', color: '#6b7280' }}>
                          seuil: {feature.threshold}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Modèle de prédiction */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              padding: '24px',
              borderLeft: '4px solid #3b82f6'
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: 'bold',
                marginBottom: '16px',
                color: '#111827',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                🔮 Prédiction - {mlResults.prediction_model.model_type}
              </h2>

              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '12px',
                marginBottom: '16px'
              }}>
                <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#dbeafe', borderRadius: '6px' }}>
                  <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
                    {Math.round(mlResults.prediction_model.accuracy * 100)}%
                  </h3>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '2px 0 0 0' }}>Précision</p>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#dbeafe', borderRadius: '6px' }}>
                  <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
                    {Math.round(mlResults.prediction_model.r2_score * 100)}%
                  </h3>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '2px 0 0 0' }}>R² Score</p>
                </div>
              </div>

              <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                🎯 Importance des Caractéristiques
              </h4>
              <div style={{ marginBottom: '16px' }}>
                {mlResults.prediction_model.feature_importance.map((feature, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '6px'
                  }}>
                    <span style={{ fontSize: '13px', color: '#6b7280' }}>
                      {feature.feature}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        width: `${feature.importance * 100}px`,
                        height: '4px',
                        backgroundColor: '#3b82f6',
                        borderRadius: '2px'
                      }}></div>
                      <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#3b82f6' }}>
                        {Math.round(feature.importance * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                📊 Exemples de Prédictions
              </h4>
              <div style={{ fontSize: '12px' }}>
                {mlResults.prediction_model.predictions_sample.map((pred, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '4px 8px',
                    backgroundColor: '#f8fafc',
                    borderRadius: '4px',
                    marginBottom: '4px'
                  }}>
                    <span style={{ color: '#6b7280' }}>
                      Réel: {pred.actual}°C
                    </span>
                    <span style={{ color: '#3b82f6' }}>
                      Prédit: {pred.predicted}°C
                    </span>
                    <span style={{
                      color: Math.abs(pred.error) < 0.5 ? '#10b981' : '#f59e0b'
                    }}>
                      Erreur: {pred.error > 0 ? '+' : ''}{pred.error}°C
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Insights avancés */}
        {mlResults && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            padding: '24px',
            marginBottom: '32px'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: 'bold',
              marginBottom: '16px',
              color: '#111827'
            }}>
              🧠 Insights Avancés des Données
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '24px'
            }}>
              {/* Patterns saisonniers */}
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', marginBottom: '12px' }}>
                  🌡️ Patterns Temporels Détectés
                </h3>
                {mlResults.data_insights.seasonal_patterns.map((pattern, index) => (
                  <div key={index} style={{
                    padding: '8px',
                    backgroundColor: '#f0fdf4',
                    borderRadius: '6px',
                    marginBottom: '8px',
                    borderLeft: '3px solid #10b981'
                  }}>
                    <div style={{ fontSize: '13px', color: '#111827', fontWeight: '500' }}>
                      {pattern.pattern}
                    </div>
                    <div style={{ fontSize: '11px', color: '#10b981' }}>
                      Confiance: {Math.round(pattern.confidence * 100)}%
                    </div>
                  </div>
                ))}
              </div>

              {/* Performance des dispositifs */}
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', marginBottom: '12px' }}>
                  🖥️ Performance des Dispositifs
                </h3>
                {mlResults.data_insights.device_performance.map((device, index) => (
                  <div key={index} style={{
                    padding: '8px',
                    backgroundColor: '#f8fafc',
                    borderRadius: '6px',
                    marginBottom: '8px'
                  }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
                      Dispositif {index + 1}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span>Fiabilité: <strong style={{ color: '#10b981' }}>
                        {Math.round(device.reliability * 100)}%
                      </strong></span>
                      <span>Qualité: <strong style={{ color: '#3b82f6' }}>
                        {Math.round(device.data_quality * 100)}%
                      </strong></span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Corrélations */}
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', marginBottom: '12px' }}>
                  🔗 Analyse de Corrélation
                </h3>
                {Object.entries(mlResults.data_insights.correlation_analysis).map(([key, value]) => (
                  <div key={key} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '6px 8px',
                    backgroundColor: '#fef7ff',
                    borderRadius: '4px',
                    marginBottom: '6px'
                  }}>
                    <span style={{ fontSize: '12px', color: '#6b7280' }}>
                      {key.replace('_', ' - ')}
                    </span>
                    <span style={{
                      fontSize: '12px',
                      fontWeight: 'bold',
                      color: Math.abs(value) > 0.7 ? '#ef4444' :
                             Math.abs(value) > 0.5 ? '#f59e0b' : '#10b981'
                    }}>
                      {value > 0 ? '+' : ''}{value.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

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

export default Analysis;