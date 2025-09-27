// Service API pour communiquer avec le simulateur IoT
const API_BASE_URL = 'http://localhost:5000/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export const fetchLatestData = async (n = 20) => {
  try {
    const response = await fetch(`${API_BASE_URL}/latest?n=${n}`);

    if (!response.ok) {
      throw new ApiError(
        `Erreur HTTP: ${response.status}`,
        response.status
      );
    }

    const result = await response.json();

    if (!result.success) {
      throw new ApiError(result.message || 'Erreur inconnue');
    }

    return result.data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Impossible de se connecter au simulateur IoT');
  }
};

export const fetchSimulatorStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/status`);

    if (!response.ok) {
      throw new ApiError(
        `Erreur HTTP: ${response.status}`,
        response.status
      );
    }

    const result = await response.json();

    if (!result.success) {
      throw new ApiError(result.message || 'Erreur inconnue');
    }

    return result.status;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Impossible de récupérer le statut du simulateur');
  }
};

export const fetchDevices = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/devices`);

    if (!response.ok) {
      throw new ApiError(
        `Erreur HTTP: ${response.status}`,
        response.status
      );
    }

    const result = await response.json();

    if (!result.success) {
      throw new ApiError(result.message || 'Erreur inconnue');
    }

    return result.devices;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Impossible de récupérer la liste des dispositifs');
  }
};