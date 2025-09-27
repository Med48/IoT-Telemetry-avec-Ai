#!/usr/bin/env python3
"""
Modèles de Machine Learning pour les données IoT (version sans emojis)
====================================================================
Détection d'anomalies et prédiction des capteurs IoT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class IoTAnomalyDetector:
    """Détecteur d'anomalies pour les données IoT"""

    def __init__(self):
        self.isolation_forest = None
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
        print("Entrainement des modeles de detection d'anomalies...")

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

        self.is_fitted = True
        print("Modeles entraines avec succes")

    def detect_anomalies(self, data):
        """Détecte les anomalies dans les données"""
        if not self.is_fitted:
            raise ValueError("Les modeles doivent etre entraines avant la detection")

        # Préparation des features
        features = self.prepare_features(data)
        features_scaled = self.scaler.transform(features)

        # Prédictions Isolation Forest (-1 = anomalie, 1 = normal)
        iso_predictions = self.isolation_forest.predict(features_scaled)
        iso_scores = self.isolation_forest.decision_function(features_scaled)

        # Combinaison des résultats
        results = data.copy()
        results['iso_anomaly'] = iso_predictions == -1
        results['iso_score'] = iso_scores

        return results

    def save_model(self, path_prefix='anomaly_detector'):
        """Sauvegarde les modèles"""
        joblib.dump(self.isolation_forest, f'{path_prefix}_isolation_forest.joblib')
        joblib.dump(self.scaler, f'{path_prefix}_scaler.joblib')
        print(f"Modeles sauvegardes avec le prefixe {path_prefix}")

class IoTPredictor:
    """Modèle de prédiction pour les capteurs IoT"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.target_columns = ['temp', 'humidity', 'co', 'lpg', 'smoke']

    def fit(self, data, sequence_length=10):
        """Entraîne les modèles de prédiction"""
        print("Entrainement des modeles de prediction...")

        # Conversion du timestamp en datetime
        if 'datetime' not in data.columns:
            data['datetime'] = pd.to_datetime(data['ts'], unit='s')

        for target_col in self.target_columns:
            print(f"  Entrainement pour {target_col}...")

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

        print("Modeles de prediction entraines")

    def save_models(self, path_prefix='predictor'):
        """Sauvegarde les modèles"""
        for target_col in self.models:
            joblib.dump(self.models[target_col], f'{path_prefix}_{target_col}_model.joblib')
            joblib.dump(self.scalers[target_col], f'{path_prefix}_{target_col}_scaler.joblib')
        print(f"Modeles de prediction sauvegardes avec le prefixe {path_prefix}")

def analyze_anomalies(anomaly_results):
    """Analyse les résultats de détection d'anomalies"""
    print("\n" + "="*50)
    print("ANALYSE DES ANOMALIES DETECTEES")
    print("="*50)

    total_samples = len(anomaly_results)
    iso_anomalies = anomaly_results['iso_anomaly'].sum()

    print(f"Resultats globaux :")
    print(f"  • Total d'echantillons : {total_samples}")
    print(f"  • Anomalies detectees : {iso_anomalies} ({iso_anomalies/total_samples*100:.2f}%)")

    # Analyse par dispositif
    print(f"\nAnomalies par dispositif :")
    for device in anomaly_results['device'].unique():
        device_data = anomaly_results[anomaly_results['device'] == device]
        device_anomalies = device_data['iso_anomaly'].sum()
        print(f"  • {device}: {device_anomalies} anomalies ({device_anomalies/len(device_data)*100:.2f}%)")

    # Anomalies les plus sévères
    severe_anomalies = anomaly_results[anomaly_results['iso_score'] < -0.5]
    print(f"\nAnomalies severes (score < -0.5) : {len(severe_anomalies)}")

    if len(severe_anomalies) > 0:
        print("  Top 5 des anomalies les plus severes :")
        top_anomalies = severe_anomalies.nsmallest(5, 'iso_score')
        for _, row in top_anomalies.iterrows():
            print(f"    • {row['device']} - Score: {row['iso_score']:.3f} - "
                  f"Temp: {row['temp']:.1f}C, CO: {row['co']:.3f}, Fumee: {row['smoke']:.3f}")

def main():
    """Fonction principale"""
    print("Demarrage du Machine Learning pour IoT")
    print("="*60)

    # Chargement des données
    print("Chargement des donnees...")
    data = pd.read_csv('iot_data_cleaned.csv')

    print(f"Donnees chargees : {len(data)} echantillons")

    # Échantillonnage pour l'entraînement (pour accélérer)
    sample_size = min(50000, len(data))
    data_sample = data.sample(n=sample_size, random_state=42)

    # 1. Détection d'anomalies
    print("\n" + "="*40)
    print("DETECTION D'ANOMALIES")
    print("="*40)

    anomaly_detector = IoTAnomalyDetector()
    anomaly_detector.fit(data_sample, contamination=0.05)

    # Test sur un échantillon plus petit
    test_sample = data.sample(n=min(10000, len(data)), random_state=123)
    anomaly_results = anomaly_detector.detect_anomalies(test_sample)

    # Analyse des anomalies
    analyze_anomalies(anomaly_results)

    # Sauvegarde des anomalies
    anomaly_results.to_csv('iot_anomalies.csv', index=False)
    anomaly_detector.save_model()

    # 2. Prédiction
    print("\n" + "="*40)
    print("MODELES DE PREDICTION")
    print("="*40)

    predictor = IoTPredictor()
    predictor.fit(data_sample, sequence_length=10)

    predictor.save_models()

    print("\n" + "="*60)
    print("Machine Learning termine avec succes !")
    print("Fichiers generes :")
    print("   • iot_anomalies.csv - Resultats de detection d'anomalies")
    print("   • anomaly_detector_*.joblib - Modeles de detection")
    print("   • predictor_*.joblib - Modeles de prediction")

if __name__ == "__main__":
    main()