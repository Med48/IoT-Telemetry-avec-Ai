#!/usr/bin/env python3
"""
Analyse simple des données IoT (sans pandas)
===========================================
Version alternative utilisant uniquement les bibliothèques standard
"""

import csv
import json
import statistics
from datetime import datetime
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

class SimpleIoTAnalyzer:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = []
        self.devices = set()

    def load_and_parse_data(self):
        """Charge et parse les données CSV"""
        print("📊 Chargement des données...")

        with open(self.csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for i, row in enumerate(reader):
                if i % 50000 == 0:  # Progress
                    print(f"  Ligne {i} traitée...")

                try:
                    # Parse des données
                    parsed_row = {
                        'ts': float(row['ts']),
                        'device': row['device'],
                        'co': float(row['co']),
                        'humidity': float(row['humidity']),
                        'light': row['light'] == 'true',
                        'lpg': float(row['lpg']),
                        'motion': row['motion'] == 'true',
                        'smoke': float(row['smoke']),
                        'temp': float(row['temp'])
                    }

                    # Ajouter datetime
                    parsed_row['datetime'] = datetime.fromtimestamp(parsed_row['ts'])
                    parsed_row['hour'] = parsed_row['datetime'].hour

                    self.data.append(parsed_row)
                    self.devices.add(parsed_row['device'])

                except (ValueError, KeyError) as e:
                    # Ignorer les lignes avec des erreurs
                    continue

        print(f"✅ {len(self.data)} échantillons chargés")
        print(f"📱 Dispositifs détectés : {len(self.devices)}")
        for device in self.devices:
            print(f"  • {device}")

    def basic_statistics(self):
        """Calcule les statistiques de base"""
        print("\n" + "="*50)
        print("📊 STATISTIQUES DE BASE")
        print("="*50)

        numeric_fields = ['temp', 'humidity', 'co', 'lpg', 'smoke']

        for field in numeric_fields:
            values = [row[field] for row in self.data if row[field] is not None]

            if values:
                print(f"\n🌡️ {field.upper()}:")
                print(f"  • Moyenne: {statistics.mean(values):.3f}")
                print(f"  • Médiane: {statistics.median(values):.3f}")
                print(f"  • Min: {min(values):.3f}")
                print(f"  • Max: {max(values):.3f}")
                print(f"  • Écart-type: {statistics.stdev(values):.3f}")

    def device_analysis(self):
        """Analyse par dispositif"""
        print("\n" + "="*50)
        print("📱 ANALYSE PAR DISPOSITIF")
        print("="*50)

        device_stats = defaultdict(lambda: defaultdict(list))

        # Regroupement par dispositif
        for row in self.data:
            device = row['device']
            for field in ['temp', 'humidity', 'co', 'lpg', 'smoke']:
                device_stats[device][field].append(row[field])

        # Statistiques par dispositif
        for device in self.devices:
            print(f"\n🔸 Dispositif {device}:")
            device_data = [row for row in self.data if row['device'] == device]
            print(f"  • Nombre de mesures: {len(device_data)}")

            for field in ['temp', 'humidity', 'co', 'lpg', 'smoke']:
                values = device_stats[device][field]
                if values:
                    mean_val = statistics.mean(values)
                    print(f"  • {field}: µ={mean_val:.3f}")

    def create_simple_visualizations(self):
        """Crée des visualisations simples"""
        print("\n📈 Création des visualisations...")

        # 1. Distribution de température par dispositif
        plt.figure(figsize=(12, 8))

        colors = ['blue', 'red', 'green']
        for i, device in enumerate(self.devices):
            device_data = [row for row in self.data if row['device'] == device]
            temps = [row['temp'] for row in device_data]

            plt.subplot(2, 2, i+1)
            plt.hist(temps, bins=50, alpha=0.7, color=colors[i % len(colors)])
            plt.title(f'Distribution Température - {device}')
            plt.xlabel('Température (°C)')
            plt.ylabel('Fréquence')

        plt.tight_layout()
        plt.savefig('temperature_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()

        # 2. Évolution temporelle (échantillon)
        plt.figure(figsize=(15, 10))

        # Prendre un échantillon pour la visualisation
        sample_data = self.data[::100]  # Toutes les 100 lignes

        fields = ['temp', 'humidity', 'co', 'smoke']

        for i, field in enumerate(fields):
            plt.subplot(2, 2, i+1)

            for device in self.devices:
                device_sample = [row for row in sample_data if row['device'] == device]
                timestamps = [row['datetime'] for row in device_sample]
                values = [row[field] for row in device_sample]

                plt.plot(timestamps, values, label=device, alpha=0.7)

            plt.title(f'Évolution {field.title()}')
            plt.xlabel('Temps')
            plt.ylabel(field.title())
            plt.legend()
            plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig('evolution_temporelle_simple.png', dpi=300, bbox_inches='tight')
        plt.show()

    def analyze_events(self):
        """Analyse les événements (mouvement/lumière)"""
        print("\n" + "="*50)
        print("🎯 ANALYSE DES ÉVÉNEMENTS")
        print("="*50)

        motion_count = sum(1 for row in self.data if row['motion'])
        light_count = sum(1 for row in self.data if row['light'])

        print(f"🏃 Détections de mouvement: {motion_count} ({motion_count/len(self.data)*100:.2f}%)")
        print(f"💡 Activations de lumière: {light_count} ({light_count/len(self.data)*100:.2f}%)")

        # Par dispositif
        for device in self.devices:
            device_data = [row for row in self.data if row['device'] == device]
            device_motion = sum(1 for row in device_data if row['motion'])
            device_light = sum(1 for row in device_data if row['light'])

            print(f"\n📱 {device}:")
            print(f"  • Mouvement: {device_motion}/{len(device_data)} ({device_motion/len(device_data)*100:.1f}%)")
            print(f"  • Lumière: {device_light}/{len(device_data)} ({device_light/len(device_data)*100:.1f}%)")

    def detect_simple_anomalies(self):
        """Détection simple d'anomalies (valeurs extrêmes)"""
        print("\n" + "="*50)
        print("🚨 DÉTECTION D'ANOMALIES SIMPLES")
        print("="*50)

        fields = ['temp', 'humidity', 'co', 'lpg', 'smoke']

        for field in fields:
            values = [row[field] for row in self.data]
            mean_val = statistics.mean(values)
            stdev_val = statistics.stdev(values)

            # Valeurs à plus de 3 écarts-types
            threshold = 3 * stdev_val
            anomalies = []

            for row in self.data:
                if abs(row[field] - mean_val) > threshold:
                    anomalies.append(row)

            print(f"⚠️ {field.upper()}: {len(anomalies)} anomalies détectées (>{threshold:.3f})")

            if anomalies:
                print(f"  Exemples (premiers 3):")
                for i, anomaly in enumerate(anomalies[:3]):
                    print(f"    • {anomaly['device']}: {anomaly[field]:.3f} (à {anomaly['datetime']})")

    def save_sample_data(self):
        """Sauvegarde un échantillon des données"""
        print("\n💾 Sauvegarde d'un échantillon...")

        # Échantillon de 1000 points
        sample_size = min(1000, len(self.data))
        sample_data = self.data[::len(self.data)//sample_size]

        with open('iot_sample_simple.json', 'w') as f:
            # Conversion datetime en string pour JSON
            sample_json = []
            for row in sample_data:
                row_copy = row.copy()
                row_copy['datetime'] = row_copy['datetime'].isoformat()
                sample_json.append(row_copy)

            json.dump(sample_json, f, indent=2)

        print(f"✅ Échantillon de {len(sample_data)} points sauvegardé dans iot_sample_simple.json")

def main():
    """Fonction principale"""
    print("🚀 Analyse simple des données IoT")
    print("="*50)

    analyzer = SimpleIoTAnalyzer('iot_telemetry_data.csv')

    # Chargement et analyse
    analyzer.load_and_parse_data()
    analyzer.basic_statistics()
    analyzer.device_analysis()
    analyzer.analyze_events()
    analyzer.detect_simple_anomalies()

    # Visualisations
    analyzer.create_simple_visualizations()

    # Sauvegarde
    analyzer.save_sample_data()

    print("\n✅ Analyse terminée avec succès !")

if __name__ == "__main__":
    main()