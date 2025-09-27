import { useState, useEffect, useCallback } from 'react';
import { fetchLatestData, fetchSimulatorStatus } from '../services/api';

export const useIoTData = (pollInterval = 3000) => {
  const [data, setData] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);

      // Récupérer les données et le statut en parallèle
      const [latestData, simulatorStatus] = await Promise.all([
        fetchLatestData(20),
        fetchSimulatorStatus()
      ]);

      setData(latestData);
      setStatus(simulatorStatus);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (err) {
      console.error('Erreur lors de la récupération des données:', err);
      setError(err.message);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Première récupération
    fetchData();

    // Mise en place du polling
    const interval = setInterval(fetchData, pollInterval);

    return () => clearInterval(interval);
  }, [fetchData, pollInterval]);

  // Fonction pour rafraîchir manuellement
  const refresh = useCallback(() => {
    setLoading(true);
    fetchData();
  }, [fetchData]);

  return {
    data,
    status,
    loading,
    error,
    lastUpdate,
    refresh
  };
};