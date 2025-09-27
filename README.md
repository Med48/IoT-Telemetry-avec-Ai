# IoT Telemetry avec AI

Un projet complet de télémétrie IoT avec intelligence artificielle pour la simulation, l'analyse et la détection d'anomalies dans les données de capteurs.

## 🚀 Fonctionnalités

- **Analyse de données** : Exploration et visualisation des données IoT
- **Machine Learning** : Détection d'anomalies et prédiction avec IA
- **Dashboard Web** : Interface utilisateur interactive (React + Vite)
- **API REST** : Serveur Flask pour la communication en temps réel

## 📁 Structure du projet

```
IoTTelemetry/
├── 📊 Scripts d'analyse
│   ├── data_analysis_clean.py      # Analyse exploratoire des données
│   ├── data_analysis_simple.py     # Analyse simplifiée
│   └── ml_models_clean.py          # Modèles de machine learning
├── 🌐 Dashboard Web
│   └── iot-dashboard/              # Application React
├── 📈 Données
│   ├── iot_telemetry_data.csv      # Données principales
│   ├── iot_data_cleaned.csv        # Données nettoyées
│   └── iot_anomalies.csv           # Anomalies détectées
├── 🔧 Configuration
│   ├── requirements.txt            # Dépendances Python
│   └── .gitignore                  # Fichiers à ignorer
└── 📚 Documentation
    └── README.md                   # Ce fichier
```

## 📊 Fonctionnalités détaillées

### Simulation IoT (`iot_simulator_simple.py`)
- Génération de données de capteurs (température, humidité, pression)
- Serveur Flask avec API REST
- Support CORS pour le dashboard web
- Simulation en temps réel avec WebSocket

### Analyse de données (`data_analysis_clean.py`)
- Exploration statistique des données
- Visualisations avec matplotlib et seaborn
- Détection de valeurs aberrantes
- Corrélations entre capteurs

### Machine Learning (`ml_models_clean.py`)
- **Détection d'anomalies** : Isolation Forest
- **Prédiction** : Random Forest Regressor
- Préprocessing avec StandardScaler
- Sauvegarde des modèles avec joblib

### Dashboard Web
- Interface React moderne avec Vite
- Visualisations en temps réel
- Graphiques interactifs
- Design responsive avec Tailwind CSS

## 🔧 Technologies utilisées

### Backend
- **Python 3.8+**
- **Flask** : API REST et serveur web
- **Pandas** : Manipulation de données
- **Scikit-learn** : Machine learning
- **Matplotlib/Seaborn** : Visualisations
- **NumPy** : Calculs numériques

### Frontend
- **React 18** : Framework UI
- **Vite** : Build tool moderne
- **Tailwind CSS** : Framework CSS
- **Chart.js** : Graphiques interactifs

## 📈 Modèles d'IA

### Détection d'anomalies
- **Algorithme** : Isolation Forest
- **Objectif** : Identifier les comportements anormaux des capteurs
- **Métriques** : Scores d'anomalie, visualisations

### Prédiction de valeurs
- **Algorithme** : Random Forest Regressor
- **Objectif** : Prédire les valeurs futures des capteurs
- **Métriques** : RMSE, R², visualisations de prédiction

## 👨‍💻 Auteur

**Mohammed RHOUATI** - [GitHub](https://github.com/Med48)
