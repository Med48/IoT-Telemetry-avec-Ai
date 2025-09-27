#!/usr/bin/env python3
"""
Script de démarrage rapide pour le projet IoT
============================================
Lance automatiquement l'analyse des données et démarre le simulateur
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

class IoTQuickStart:
    """Gestionnaire de démarrage rapide"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.csv_file = self.project_root / "iot_telemetry_data.csv"

    def check_requirements(self):
        """Vérifie que tous les fichiers nécessaires sont présents"""
        print("🔍 Vérification des prérequis...")

        required_files = [
            "iot_telemetry_data.csv",
            "requirements.txt",
            "data_analysis.py",
            "ml_models.py",
            "iot_simulator.py"
        ]

        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)

        if missing_files:
            print(f"❌ Fichiers manquants : {', '.join(missing_files)}")
            return False

        print("✅ Tous les fichiers requis sont présents")
        return True

    def check_python_packages(self):
        """Vérifie l'installation des packages Python"""
        print("📦 Vérification des packages Python...")

        required_packages = [
            'pandas', 'numpy', 'matplotlib', 'seaborn',
            'scikit-learn', 'flask', 'requests'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Packages manquants : {', '.join(missing_packages)}")
            print("💡 Installez-les avec : pip install -r requirements.txt")
            return False

        print("✅ Tous les packages sont installés")
        return True

    def run_data_analysis(self):
        """Lance l'analyse des données"""
        print("\n" + "="*60)
        print("📊 LANCEMENT DE L'ANALYSE DES DONNÉES")
        print("="*60)

        try:
            result = subprocess.run([
                sys.executable, "data_analysis.py"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode == 0:
                print("✅ Analyse des données terminée avec succès")
                return True
            else:
                print(f"❌ Erreur lors de l'analyse : {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Erreur lors du lancement de l'analyse : {e}")
            return False

    def run_ml_models(self):
        """Lance l'entraînement des modèles ML"""
        print("\n" + "="*60)
        print("🤖 LANCEMENT DE L'ENTRAÎNEMENT DES MODÈLES IA")
        print("="*60)

        try:
            result = subprocess.run([
                sys.executable, "ml_models.py"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode == 0:
                print("✅ Entraînement des modèles terminé avec succès")
                return True
            else:
                print(f"❌ Erreur lors de l'entraînement : {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Erreur lors du lancement des modèles : {e}")
            return False

    def start_simulator(self, web_server=True, speed=5.0, port=5000):
        """Démarre le simulateur IoT"""
        print("\n" + "="*60)
        print("🚀 DÉMARRAGE DU SIMULATEUR IoT")
        print("="*60)

        cmd = [sys.executable, "iot_simulator.py", "--speed", str(speed)]

        if web_server:
            cmd.extend(["--web-server", "--port", str(port)])
            print(f"🌐 Serveur web démarré sur http://localhost:{port}")

        try:
            print("⏳ Démarrage du simulateur...")
            print("📌 Appuyez sur Ctrl+C pour arrêter le simulateur")
            print()

            # Démarrage du simulateur (bloquant)
            subprocess.run(cmd, cwd=self.project_root)

        except KeyboardInterrupt:
            print("\n⏹️ Simulateur arrêté par l'utilisateur")
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du simulateur : {e}")

    def show_project_status(self):
        """Affiche le statut du projet"""
        print("\n" + "="*60)
        print("📋 STATUT DU PROJET")
        print("="*60)

        # Fichiers générés
        generated_files = [
            ("iot_data_cleaned.csv", "Données nettoyées"),
            ("iot_data_sample.csv", "Échantillon pour dashboard"),
            ("iot_anomalies.csv", "Anomalies détectées"),
            ("distribution_capteurs.png", "Visualisation distributions"),
            ("evolution_temporelle.png", "Évolution temporelle"),
            ("correlation_matrix.png", "Matrice de corrélation"),
            ("predictions_visualization.png", "Visualisations prédictions")
        ]

        print("📁 Fichiers générés :")
        for filename, description in generated_files:
            file_path = self.project_root / filename
            status = "✅" if file_path.exists() else "❌"
            print(f"  {status} {filename} - {description}")

        # Modèles ML
        model_files = [
            "anomaly_detector_isolation_forest.joblib",
            "anomaly_detector_scaler.joblib",
            "predictor_temp_model.joblib",
            "predictor_humidity_model.joblib"
        ]

        print("\n🤖 Modèles ML :")
        for filename in model_files:
            file_path = self.project_root / filename
            status = "✅" if file_path.exists() else "❌"
            print(f"  {status} {filename}")

    def show_next_steps(self):
        """Affiche les prochaines étapes"""
        print("\n" + "="*60)
        print("🎯 PROCHAINES ÉTAPES")
        print("="*60)

        print("1. 📊 Analyser les visualisations générées (fichiers PNG)")
        print("2. 🔍 Examiner les anomalies dans iot_anomalies.csv")
        print("3. 🌐 Créer le dashboard React avec les instructions dans dashboard_setup.txt")
        print("4. 🚀 Lancer le dashboard : npm create vite@latest iot-dashboard")
        print("5. 🔗 Connecter le dashboard à l'API : http://localhost:5000/api/latest")
        print()
        print("📖 Consultez GUIDE_COMPLET.txt pour tous les détails")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Démarrage rapide du projet IoT')
    parser.add_argument('--skip-analysis', action='store_true',
                      help='Ignorer l\'analyse des données')
    parser.add_argument('--skip-ml', action='store_true',
                      help='Ignorer l\'entraînement des modèles')
    parser.add_argument('--only-simulator', action='store_true',
                      help='Lancer uniquement le simulateur')
    parser.add_argument('--speed', type=float, default=5.0,
                      help='Vitesse du simulateur (défaut: 5.0)')
    parser.add_argument('--port', type=int, default=5000,
                      help='Port du serveur web (défaut: 5000)')
    parser.add_argument('--no-web', action='store_true',
                      help='Désactiver le serveur web')

    args = parser.parse_args()

    print("🚀 DÉMARRAGE RAPIDE DU PROJET IoT TELEMETRY")
    print("="*60)

    quick_start = IoTQuickStart()

    # Vérifications préalables
    if not quick_start.check_requirements():
        sys.exit(1)

    if not quick_start.check_python_packages():
        sys.exit(1)

    # Mode simulateur uniquement
    if args.only_simulator:
        quick_start.start_simulator(
            web_server=not args.no_web,
            speed=args.speed,
            port=args.port
        )
        return

    # Analyse des données
    if not args.skip_analysis:
        if not quick_start.run_data_analysis():
            print("⚠️ Erreur lors de l'analyse, mais continuation possible")

    # Modèles ML
    if not args.skip_ml:
        if not quick_start.run_ml_models():
            print("⚠️ Erreur lors des modèles ML, mais continuation possible")

    # Statut du projet
    quick_start.show_project_status()

    # Démarrage du simulateur
    print("\n🔄 Voulez-vous démarrer le simulateur maintenant ? (y/N)")
    response = input().lower().strip()

    if response in ['y', 'yes', 'oui', 'o']:
        quick_start.start_simulator(
            web_server=not args.no_web,
            speed=args.speed,
            port=args.port
        )
    else:
        quick_start.show_next_steps()

if __name__ == "__main__":
    main()