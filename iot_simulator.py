#!/usr/bin/env python3
"""
Simulateur de flux IoT en temps réel
===================================
Simule l'envoi de données IoT depuis le CSV comme si elles venaient de capteurs réels
"""

import pandas as pd
import numpy as np
import time
import json
import requests
from datetime import datetime, timedelta
import threading
import queue
from flask import Flask, jsonify, request
from flask_cors import CORS
import argparse

class IoTDataSimulator:
    """Simulateur de données IoT en temps réel"""

    def __init__(self, csv_path, speed_multiplier=1.0):
        """
        Initialise le simulateur
        Args:
            csv_path: Chemin vers le fichier CSV
            speed_multiplier: Multiplicateur de vitesse (1.0 = temps réel, 2.0 = 2x plus rapide)
        """
        self.csv_path = csv_path
        self.speed_multiplier = speed_multiplier
        self.data = None
        self.current_index = 0
        self.is_running = False
        self.data_queue = queue.Queue(maxsize=1000)
        self.subscribers = []

    def load_data(self):
        """Charge et prépare les données CSV"""
        print(f"📊 Chargement des données depuis {self.csv_path}...")
        self.data = pd.read_csv(self.csv_path)

        # Préparation des données
        self.data['datetime'] = pd.to_datetime(self.data['ts'], unit='s')
        self.data = self.data.sort_values('datetime')

        # Conversion des types
        self.data['light'] = self.data['light'].map({'true': True, 'false': False})
        self.data['motion'] = self.data['motion'].map({'true': True, 'false': False})

        numeric_cols = ['co', 'humidity', 'lpg', 'smoke', 'temp']
        for col in numeric_cols:
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce')

        # Suppression des valeurs manquantes
        self.data = self.data.dropna()

        print(f"✅ {len(self.data)} échantillons chargés")
        return self.data

    def calculate_delay(self, current_row, next_row):
        """Calcule le délai entre deux mesures"""
        if next_row is None:
            return 1.0  # Délai par défaut

        current_time = current_row['datetime']
        next_time = next_row['datetime']
        time_diff = (next_time - current_time).total_seconds()

        # Ajustement avec le multiplicateur de vitesse
        delay = max(time_diff / self.speed_multiplier, 0.1)  # Minimum 0.1 seconde
        return min(delay, 10.0)  # Maximum 10 secondes

    def format_data_point(self, row):
        """Formate un point de données pour l'envoi"""
        return {
            'timestamp': row['datetime'].isoformat(),
            'device_id': row['device'],
            'sensors': {
                'temperature': float(row['temp']),
                'humidity': float(row['humidity']),
                'co': float(row['co']),
                'lpg': float(row['lpg']),
                'smoke': float(row['smoke']),
                'light': bool(row['light']),
                'motion': bool(row['motion'])
            },
            'metadata': {
                'ts': float(row['ts']),
                'hour': int(row['datetime'].hour),
                'day': int(row['datetime'].day)
            }
        }

    def send_to_api(self, data_point, api_endpoint):
        """Envoie les données vers une API"""
        try:
            response = requests.post(
                api_endpoint,
                json=data_point,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print(f"✅ Données envoyées vers {api_endpoint}")
            else:
                print(f"⚠️ Erreur API {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur d'envoi vers {api_endpoint}: {e}")

    def notify_subscribers(self, data_point):
        """Notifie tous les abonnés d'un nouveau point de données"""
        for subscriber in self.subscribers:
            try:
                subscriber(data_point)
            except Exception as e:
                print(f"⚠️ Erreur lors de la notification: {e}")

    def start_streaming(self, api_endpoint=None, max_samples=None, save_to_file=None):
        """Démarre le streaming des données"""
        if self.data is None:
            self.load_data()

        self.is_running = True
        print(f"🚀 Démarrage du streaming (vitesse x{self.speed_multiplier})")

        if api_endpoint:
            print(f"📡 Envoi vers API: {api_endpoint}")

        if save_to_file:
            print(f"💾 Sauvegarde dans: {save_to_file}")
            output_file = open(save_to_file, 'w')
            output_file.write("timestamp,device_id,temp,humidity,co,lpg,smoke,light,motion\n")

        sent_count = 0
        self.current_index = 0

        try:
            while self.is_running and self.current_index < len(self.data):
                if max_samples and sent_count >= max_samples:
                    break

                current_row = self.data.iloc[self.current_index]
                next_row = self.data.iloc[self.current_index + 1] if self.current_index + 1 < len(self.data) else None

                # Formatage des données
                data_point = self.format_data_point(current_row)

                # Ajout à la queue
                if not self.data_queue.full():
                    self.data_queue.put(data_point)

                # Affichage
                device = data_point['device_id']
                temp = data_point['sensors']['temperature']
                humidity = data_point['sensors']['humidity']
                timestamp = data_point['timestamp']

                print(f"📊 [{timestamp}] {device}: T={temp:.1f}°C, H={humidity:.1f}%")

                # Envoi vers API
                if api_endpoint:
                    self.send_to_api(data_point, api_endpoint)

                # Sauvegarde dans fichier
                if save_to_file:
                    sensors = data_point['sensors']
                    line = f"{timestamp},{device},{sensors['temperature']},{sensors['humidity']}," \
                           f"{sensors['co']},{sensors['lpg']},{sensors['smoke']}," \
                           f"{sensors['light']},{sensors['motion']}\n"
                    output_file.write(line)
                    output_file.flush()

                # Notification des abonnés
                self.notify_subscribers(data_point)

                # Calcul du délai
                delay = self.calculate_delay(current_row, next_row)
                time.sleep(delay)

                self.current_index += 1
                sent_count += 1

                # Progress
                if sent_count % 100 == 0:
                    progress = (self.current_index / len(self.data)) * 100
                    print(f"📈 Progrès: {progress:.1f}% ({sent_count} échantillons envoyés)")

        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé par l'utilisateur")
        finally:
            self.is_running = False
            if save_to_file:
                output_file.close()
            print(f"✅ Streaming terminé. {sent_count} échantillons envoyés.")

    def stop_streaming(self):
        """Arrête le streaming"""
        self.is_running = False

    def get_latest_data(self, n_samples=10):
        """Récupère les dernières données de la queue"""
        latest_data = []
        for _ in range(min(n_samples, self.data_queue.qsize())):
            try:
                latest_data.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return latest_data

    def subscribe(self, callback):
        """Abonne une fonction callback aux nouvelles données"""
        self.subscribers.append(callback)

class IoTWebServer:
    """Serveur web pour exposer les données IoT via API"""

    def __init__(self, simulator, port=5000):
        self.simulator = simulator
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()

    def setup_routes(self):
        """Configure les routes de l'API"""

        @self.app.route('/api/latest', methods=['GET'])
        def get_latest():
            """Récupère les dernières données"""
            n_samples = request.args.get('n', 10, type=int)
            data = self.simulator.get_latest_data(n_samples)
            return jsonify({
                'success': True,
                'data': data,
                'count': len(data)
            })

        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Statut du simulateur"""
            return jsonify({
                'success': True,
                'status': {
                    'is_running': self.simulator.is_running,
                    'current_index': self.simulator.current_index,
                    'total_samples': len(self.simulator.data) if self.simulator.data is not None else 0,
                    'queue_size': self.simulator.data_queue.qsize()
                }
            })

        @self.app.route('/api/data', methods=['POST'])
        def receive_data():
            """Endpoint pour recevoir des données (pour test)"""
            data = request.get_json()
            print(f"📨 Données reçues: {data}")
            return jsonify({'success': True, 'message': 'Données reçues'})

        @self.app.route('/api/devices', methods=['GET'])
        def get_devices():
            """Liste des dispositifs"""
            if self.simulator.data is not None:
                devices = self.simulator.data['device'].unique().tolist()
                return jsonify({
                    'success': True,
                    'devices': devices
                })
            return jsonify({'success': False, 'message': 'Aucune donnée chargée'})

    def start(self):
        """Démarre le serveur web"""
        print(f"🌐 Démarrage du serveur web sur le port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)

def print_callback(data_point):
    """Callback d'exemple pour afficher les données"""
    device = data_point['device_id']
    temp = data_point['sensors']['temperature']
    print(f"🔔 Callback: {device} - {temp:.1f}°C")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Simulateur IoT en temps réel')
    parser.add_argument('--csv', default='iot_telemetry_data.csv', help='Chemin vers le fichier CSV')
    parser.add_argument('--speed', type=float, default=10.0, help='Multiplicateur de vitesse')
    parser.add_argument('--api', help='URL de l\'API de destination')
    parser.add_argument('--max-samples', type=int, help='Nombre maximum d\'échantillons à envoyer')
    parser.add_argument('--output', help='Fichier de sortie pour sauvegarder les données')
    parser.add_argument('--web-server', action='store_true', help='Démarrer le serveur web')
    parser.add_argument('--port', type=int, default=5000, help='Port du serveur web')

    args = parser.parse_args()

    print("🚀 Simulateur IoT en temps réel")
    print("="*50)

    # Initialisation du simulateur
    simulator = IoTDataSimulator(args.csv, args.speed)
    simulator.load_data()

    # Démarrage du serveur web si demandé
    if args.web_server:
        web_server = IoTWebServer(simulator, args.port)

        # Démarrage du serveur dans un thread séparé
        server_thread = threading.Thread(target=web_server.start)
        server_thread.daemon = True
        server_thread.start()

        print(f"🌐 Serveur web démarré sur http://localhost:{args.port}")
        time.sleep(2)  # Attendre que le serveur démarre

    # Abonnement à un callback d'exemple
    simulator.subscribe(print_callback)

    # Démarrage du streaming
    simulator.start_streaming(
        api_endpoint=args.api,
        max_samples=args.max_samples,
        save_to_file=args.output
    )

if __name__ == "__main__":
    main()