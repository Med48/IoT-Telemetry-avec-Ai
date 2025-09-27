import { RefreshCw, Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';

const StatusBar = ({ status, lastUpdate, onRefresh, isLoading, error }) => {
  const getConnectionStatus = () => {
    if (error) return { color: 'text-red-600', icon: WifiOff, text: 'Déconnecté' };
    if (status?.is_running) return { color: 'text-green-600', icon: Wifi, text: 'Connecté' };
    return { color: 'text-yellow-600', icon: AlertCircle, text: 'En attente' };
  };

  const connectionStatus = getConnectionStatus();
  const Icon = connectionStatus.icon;

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
      <div className="flex items-center justify-between">
        {/* Statut de connexion */}
        <div className="flex items-center space-x-3">
          <Icon className={`w-5 h-5 ${connectionStatus.color}`} />
          <div>
            <p className={`font-medium ${connectionStatus.color}`}>
              {connectionStatus.text}
            </p>
            {status && (
              <p className="text-sm text-gray-600">
                {status.current_index}/{status.total_samples} échantillons traités
              </p>
            )}
          </div>
        </div>

        {/* Informations de mise à jour */}
        <div className="flex items-center space-x-4">
          {lastUpdate && (
            <div className="text-right">
              <p className="text-sm text-gray-600">Dernière mise à jour</p>
              <p className="text-xs text-gray-500">
                {lastUpdate.toLocaleTimeString()}
              </p>
            </div>
          )}

          {/* Bouton de rafraîchissement */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className={`p-2 rounded-full transition-colors ${
              isLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-100 text-blue-600 hover:bg-blue-200'
            }`}
            title="Rafraîchir les données"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Barre de progression */}
      {status && status.total_samples > 0 && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${(status.current_index / status.total_samples) * 100}%`
              }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Progression: {Math.round((status.current_index / status.total_samples) * 100)}%
          </p>
        </div>
      )}

      {/* Message d'erreur */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Indicateurs de performance */}
      {status && (
        <div className="mt-3 grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-sm font-medium text-gray-900">
              {status.queue_size}
            </p>
            <p className="text-xs text-gray-500">En attente</p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-900">
              {status.current_index}
            </p>
            <p className="text-xs text-gray-500">Traités</p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-900">
              {status.is_running ? 'Actif' : 'Arrêté'}
            </p>
            <p className="text-xs text-gray-500">État</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusBar;