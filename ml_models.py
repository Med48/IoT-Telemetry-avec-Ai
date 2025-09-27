#!/usr/bin/env python3
"""
Modèles de Machine Learning pour les données IoT
===============================================
Détection d'anomalies et prédiction des capteurs IoT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import DBSCAN
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
import joblib
import warnings
warnings.filterwarnings('ignore')

class IoTAnomalyDetector:
    """Détecteur d'anomalies pour les données IoT"""

    def __init__(self):
        self.isolation_forest = None
        self.dbscan = None
        self.scaler = StandardScaler()
        self.is_fitted = False

    def prepare_features(self, data):
        """Prépare les features pour la détection d'anomalies"""
        # Sélection des features numériques
        features = ['temp', 'humidity', 'co', 'lpg', 'smoke']
        feature_data = data[features].copy()

        # Ajout de features dérivées
        feature_data['temp_humidity_ratio'] = feature_data['temp'] / (feature_data['humidity'] + 1e-8)
        feature_data['air_quality_index'] = feature_data['co'] + feature_data['lpg'] + feature_data['smoke']

        # Gestion des valeurs manquantes
        feature_data = feature_data.fillna(feature_data.median())

        return feature_data

    def fit(self, data, contamination=0.1):
        """Entraîne les modèles de détection d'anomalies"""
        print("🤖 Entraînement des modèles de détection d'anomalies...")

        # Préparation des features
        features = self.prepare_features(data)

        # Normalisation
        features_scaled = self.scaler.fit_transform(features)

        # Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.isolation_forest.fit(features_scaled)

        # DBSCAN
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.dbscan.fit(features_scaled)

        self.is_fitted = True
        print("✅ Modèles entraînés avec succès")

    def detect_anomalies(self, data):
        """Détecte les anomalies dans les données"""
        if not self.is_fitted:
            raise ValueError("Les modèles doivent être entraînés avant la détection")

        # Préparation des features
        features = self.prepare_features(data)
        features_scaled = self.scaler.transform(features)

        # Prédictions Isolation Forest (-1 = anomalie, 1 = normal)
        iso_predictions = self.isolation_forest.predict(features_scaled)
        iso_scores = self.isolation_forest.decision_function(features_scaled)

        # Prédictions DBSCAN (-1 = anomalie/bruit, >=0 = cluster normal)
        dbscan_predictions = self.dbscan.fit_predict(features_scaled)

        # Combinaison des résultats
        results = data.copy()
        results['iso_anomaly'] = iso_predictions == -1
        results['iso_score'] = iso_scores
        results['dbscan_anomaly'] = dbscan_predictions == -1
        results['combined_anomaly'] = results['iso_anomaly'] | results['dbscan_anomaly']

        return results

    def save_model(self, path_prefix='anomaly_detector'):
        """Sauvegarde les modèles"""
        joblib.dump(self.isolation_forest, f'{path_prefix}_isolation_forest.joblib')
        joblib.dump(self.scaler, f'{path_prefix}_scaler.joblib')
        print(f"✅ Modèles sauvegardés avec le préfixe {path_prefix}")

class IoTPredictor:
    """Modèle de prédiction pour les capteurs IoT"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.target_columns = ['temp', 'humidity', 'co', 'lpg', 'smoke']

    def create_sequences(self, data, sequence_length=10):
        """Crée des séquences temporelles pour la prédiction"""
        sequences = []
        targets = []

        # Trier par dispositif et timestamp
        data_sorted = data.sort_values(['device', 'datetime'])

        for device in data_sorted['device'].unique():
            device_data = data_sorted[data_sorted['device'] == device]

            for target_col in self.target_columns:
                values = device_data[target_col].values

                for i in range(sequence_length, len(values)):
                    sequence = values[i-sequence_length:i]
                    target = values[i]

                    if not np.isnan(sequence).any() and not np.isnan(target):
                        sequences.append(sequence)
                        targets.append(target)

        return np.array(sequences), np.array(targets)

    def fit(self, data, sequence_length=10):
        """Entraîne les modèles de prédiction"""
        print("🎯 Entraînement des modèles de prédiction...")

        # Conversion du timestamp en datetime
        if 'datetime' not in data.columns:
            data['datetime'] = pd.to_datetime(data['ts'], unit='s')

        for target_col in self.target_columns:
            print(f"  📊 Entraînement pour {target_col}...")

            # Création des features
            features = []
            targets = []

            # Trier par dispositif et timestamp
            data_sorted = data.sort_values(['device', 'datetime'])

            for device in data_sorted['device'].unique():
                device_data = data_sorted[data_sorted['device'] == device]

                # Features : valeurs précédentes + autres capteurs
                other_cols = [col for col in self.target_columns if col != target_col]

                for i in range(sequence_length, len(device_data)):
                    # Valeurs historiques du capteur cible
                    hist_values = device_data[target_col].iloc[i-sequence_length:i].values

                    # Valeurs actuelles des autres capteurs
                    current_other = device_data[other_cols].iloc[i].values

                    # Features combinées
                    feature_vector = np.concatenate([
                        hist_values,  # Historique du capteur
                        current_other,  # Autres capteurs
                        [device_data['hour'].iloc[i]]  # Heure
                    ])

                    target_value = device_data[target_col].iloc[i]

                    if not np.isnan(feature_vector).any() and not np.isnan(target_value):
                        features.append(feature_vector)
                        targets.append(target_value)

            if len(features) > 0:
                X = np.array(features)
                y = np.array(targets)

                # Division train/test
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                # Normalisation
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)

                # Modèle Random Forest
                model = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    max_depth=10
                )
                model.fit(X_train_scaled, y_train)

                # Évaluation
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                print(f"    MSE: {mse:.4f}, R²: {r2:.4f}")

                # Sauvegarde
                self.models[target_col] = model
                self.scalers[target_col] = scaler

        print("✅ Modèles de prédiction entraînés")

    def predict_next_values(self, data, device, sequence_length=10):
        """Prédit les prochaines valeurs pour un dispositif"""
        predictions = {}

        # Données récentes du dispositif
        device_data = data[data['device'] == device].tail(sequence_length)

        if len(device_data) < sequence_length:
            return predictions

        for target_col in self.target_columns:
            if target_col in self.models:
                # Préparation des features
                hist_values = device_data[target_col].tail(sequence_length).values
                other_cols = [col for col in self.target_columns if col != target_col]
                current_other = device_data[other_cols].iloc[-1].values
                current_hour = device_data['hour'].iloc[-1]

                feature_vector = np.concatenate([
                    hist_values,
                    current_other,
                    [current_hour]
                ]).reshape(1, -1)

                # Prédiction
                feature_scaled = self.scalers[target_col].transform(feature_vector)
                prediction = self.models[target_col].predict(feature_scaled)[0]
                predictions[target_col] = prediction

        return predictions

    def save_models(self, path_prefix='predictor'):
        """Sauvegarde les modèles"""
        for target_col in self.models:
            joblib.dump(self.models[target_col], f'{path_prefix}_{target_col}_model.joblib')
            joblib.dump(self.scalers[target_col], f'{path_prefix}_{target_col}_scaler.joblib')
        print(f"✅ Modèles de prédiction sauvegardés avec le préfixe {path_prefix}")

def analyze_anomalies(anomaly_results):
    """Analyse les résultats de détection d'anomalies"""
    print("\n" + "="*50)
    print("🚨 ANALYSE DES ANOMALIES DÉTECTÉES")
    print("="*50)

    total_samples = len(anomaly_results)
    iso_anomalies = anomaly_results['iso_anomaly'].sum()
    dbscan_anomalies = anomaly_results['dbscan_anomaly'].sum()
    combined_anomalies = anomaly_results['combined_anomaly'].sum()

    print(f"📊 Résultats globaux :")
    print(f"  • Total d'échantillons : {total_samples}")
    print(f"  • Anomalies Isolation Forest : {iso_anomalies} ({iso_anomalies/total_samples*100:.2f}%)")
    print(f"  • Anomalies DBSCAN : {dbscan_anomalies} ({dbscan_anomalies/total_samples*100:.2f}%)")
    print(f"  • Anomalies combinées : {combined_anomalies} ({combined_anomalies/total_samples*100:.2f}%)")

    # Analyse par dispositif
    print(f"\n📱 Anomalies par dispositif :")
    for device in anomaly_results['device'].unique():
        device_data = anomaly_results[anomaly_results['device'] == device]
        device_anomalies = device_data['combined_anomaly'].sum()
        print(f"  • {device}: {device_anomalies} anomalies ({device_anomalies/len(device_data)*100:.2f}%)")

    # Anomalies les plus sévères
    severe_anomalies = anomaly_results[anomaly_results['iso_score'] < -0.5]
    print(f"\n⚠️ Anomalies sévères (score < -0.5) : {len(severe_anomalies)}")

    if len(severe_anomalies) > 0:
        print("  Top 5 des anomalies les plus sévères :")
        top_anomalies = severe_anomalies.nsmallest(5, 'iso_score')
        for _, row in top_anomalies.iterrows():
            print(f"    • {row['device']} - Score: {row['iso_score']:.3f} - "
                  f"Temp: {row['temp']:.1f}°C, CO: {row['co']:.3f}, Fumée: {row['smoke']:.3f}")

def create_prediction_visualization(data, predictor):
    """Crée des visualisations des prédictions"""
    print("\n📈 Création des visualisations de prédiction...")

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Prédictions des Capteurs IoT', fontsize=16, fontweight='bold')

    target_columns = ['temp', 'humidity', 'co', 'lpg', 'smoke']

    for i, target_col in enumerate(target_columns):
        row = i // 3
        col_idx = i % 3

        # Prendre un échantillon de données récentes
        recent_data = data.tail(200)

        # Prédictions pour chaque dispositif
        for device in recent_data['device'].unique():
            device_data = recent_data[recent_data['device'] == device]

            if len(device_data) >= 10:
                # Valeurs réelles
                axes[row, col_idx].plot(range(len(device_data)), device_data[target_col],
                                       label=f'{device} (réel)', alpha=0.7)

                # Prédictions
                predictions = []
                for j in range(10, len(device_data)):
                    pred_data = device_data.iloc[:j]
                    pred = predictor.predict_next_values(pred_data, device)
                    if target_col in pred:
                        predictions.append(pred[target_col])
                    else:
                        predictions.append(np.nan)

                if predictions:
                    pred_indices = list(range(10, 10 + len(predictions)))
                    axes[row, col_idx].plot(pred_indices, predictions,
                                           label=f'{device} (prédit)', linestyle='--', alpha=0.7)

        axes[row, col_idx].set_title(f'Prédiction {target_col.title()}')
        axes[row, col_idx].set_xlabel('Temps')
        axes[row, col_idx].set_ylabel(target_col.title())
        axes[row, col_idx].legend()

    # Supprime le subplot vide
    fig.delaxes(axes[1, 2])
    plt.tight_layout()
    plt.savefig('predictions_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Fonction principale"""
    print("🤖 Démarrage du Machine Learning pour IoT")
    print("="*60)

    # Chargement des données
    print("📊 Chargement des données...")
    data = pd.read_csv('iot_telemetry_data.csv')

    # Préparation des données
    print("🧹 Préparation des données...")
    data['datetime'] = pd.to_datetime(data['ts'], unit='s')
    data['hour'] = data['datetime'].dt.hour
    data['light'] = data['light'].map({'true': True, 'false': False})
    data['motion'] = data['motion'].map({'true': True, 'false': False})

    # Conversion des colonnes numériques
    numeric_cols = ['co', 'humidity', 'lpg', 'smoke', 'temp']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # Nettoyage (suppression des valeurs manquantes)
    data_clean = data.dropna(subset=numeric_cols)
    print(f"✅ Données nettoyées : {len(data_clean)} échantillons")

    # Échantillonnage pour l'entraînement (pour accélérer)
    sample_size = min(50000, len(data_clean))
    data_sample = data_clean.sample(n=sample_size, random_state=42)

    # 1. Détection d'anomalies
    print("\n🚨 DÉTECTION D'ANOMALIES")
    print("="*40)

    anomaly_detector = IoTAnomalyDetector()
    anomaly_detector.fit(data_sample, contamination=0.05)

    # Test sur un échantillon plus petit
    test_sample = data_clean.sample(n=min(10000, len(data_clean)), random_state=123)
    anomaly_results = anomaly_detector.detect_anomalies(test_sample)

    # Analyse des anomalies
    analyze_anomalies(anomaly_results)

    # Sauvegarde des anomalies
    anomaly_results.to_csv('iot_anomalies.csv', index=False)
    anomaly_detector.save_model()

    # 2. Prédiction
    print("\n🎯 MODÈLES DE PRÉDICTION")
    print("="*40)

    predictor = IoTPredictor()
    predictor.fit(data_sample, sequence_length=10)

    # Test de prédiction
    test_device = data_sample['device'].iloc[0]
    recent_data = data_sample[data_sample['device'] == test_device].tail(50)
    predictions = predictor.predict_next_values(recent_data, test_device)

    print(f"\n🔮 Prédictions pour le dispositif {test_device}:")
    for sensor, value in predictions.items():
        print(f"  • {sensor}: {value:.3f}")

    predictor.save_models()

    # Visualisations
    create_prediction_visualization(data_sample, predictor)

    print("\n" + "="*60)
    print("✅ Machine Learning terminé avec succès !")
    print("📁 Fichiers générés :")
    print("   • iot_anomalies.csv - Résultats de détection d'anomalies")
    print("   • anomaly_detector_*.joblib - Modèles de détection")
    print("   • predictor_*.joblib - Modèles de prédiction")
    print("   • predictions_visualization.png - Visualisations des prédictions")

if __name__ == "__main__":
    main()