#!/usr/bin/env python3
"""
Simulateur IoT simplifié (version sans emojis)
=============================================
Simule l'envoi de données IoT avec serveur Flask
"""

import pandas as pd
import time
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import queue

class SimpleIoTSimulator:
    """Simulateur IoT simplifié"""

    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = []
        self.current_index = 0
        self.is_running = False
        self.data_queue = queue.Queue(maxsize=100)

    def load_data(self):
        """Charge les données depuis le CSV"""
        print("Chargement des donnees...")

        # Charger les données dans l'ordre chronologique
        df = pd.read_csv(self.csv_path)
        df = df.sort_values('ts')  # Trier par timestamp
        sample_df = df.head(1000).copy()  # Prendre les 1000 premières mesures

        # Conversion en liste de dictionnaires avec timestamps actuels
        current_time = datetime.now()
        for i, (_, row) in enumerate(sample_df.iterrows()):
            # Utiliser le temps actuel + intervalle pour avoir des timestamps récents
            timestamp = current_time.timestamp() + (i * 3)  # 3 secondes entre chaque mesure

            data_point = {
                'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                'device_id': row['device'],
                'sensors': {
                    'temperature': float(row['temp']),
                    'humidity': float(row['humidity']),
                    'co': float(row['co']),
                    'lpg': float(row['lpg']),
                    'smoke': float(row['smoke']),
                    'light': bool(row['light']),
                    'motion': bool(row['motion'])
                }
            }
            self.data.append(data_point)

        print(f"Donnees chargees : {len(self.data)} echantillons")

    def start_streaming(self, interval=2.0):
        """Démarre le streaming des données"""
        self.is_running = True
        print(f"Demarrage du streaming (intervalle: {interval}s)")

        def stream_worker():
            while self.is_running and self.current_index < len(self.data):
                data_point = self.data[self.current_index]

                # Ajouter à la queue
                if not self.data_queue.full():
                    self.data_queue.put(data_point)

                # Affichage
                device = data_point['device_id']
                temp = data_point['sensors']['temperature']
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {device}: T={temp:.1f}C")

                self.current_index += 1
                time.sleep(interval)

        # Démarrer dans un thread séparé
        self.stream_thread = threading.Thread(target=stream_worker)
        self.stream_thread.daemon = True
        self.stream_thread.start()

    def get_latest_data(self, n=10):
        """Récupère les dernières données"""
        latest_data = []
        temp_queue = queue.Queue()

        # Récupérer les données sans les supprimer définitivement
        while not self.data_queue.empty() and len(latest_data) < n:
            try:
                item = self.data_queue.get_nowait()
                latest_data.append(item)
                temp_queue.put(item)  # Garder une copie
            except queue.Empty:
                break

        # Remettre les données dans la queue originale
        while not temp_queue.empty():
            try:
                self.data_queue.put_nowait(temp_queue.get_nowait())
            except queue.Full:
                break

        return latest_data

    def stop_streaming(self):
        """Arrête le streaming"""
        self.is_running = False

# Application Flask
app = Flask(__name__)
CORS(app)

# Instance globale du simulateur
simulator = None

@app.route('/api/latest', methods=['GET'])
def get_latest():
    """Récupère les dernières données"""
    if simulator is None:
        return jsonify({'success': False, 'message': 'Simulateur non initialise'})

    n_samples = request.args.get('n', 10, type=int)
    data = simulator.get_latest_data(n_samples)

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Statut du simulateur"""
    if simulator is None:
        return jsonify({'success': False, 'message': 'Simulateur non initialise'})

    return jsonify({
        'success': True,
        'status': {
            'is_running': simulator.is_running,
            'current_index': simulator.current_index,
            'total_samples': len(simulator.data),
            'queue_size': simulator.data_queue.qsize()
        }
    })

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Liste des dispositifs"""
    if simulator is None or not simulator.data:
        return jsonify({'success': False, 'message': 'Aucune donnee chargee'})

    devices = list(set(item['device_id'] for item in simulator.data))
    return jsonify({
        'success': True,
        'devices': devices
    })

@app.route('/', methods=['GET'])
def home():
    """Page d'accueil"""
    return jsonify({
        'message': 'Simulateur IoT API',
        'endpoints': {
            '/api/latest?n=10': 'Dernieres donnees',
            '/api/status': 'Statut du simulateur',
            '/api/devices': 'Liste des dispositifs'
        }
    })

def main():
    """Fonction principale"""
    global simulator

    print("Simulateur IoT Simple")
    print("="*40)

    # Initialisation du simulateur
    simulator = SimpleIoTSimulator('iot_data_sample.csv')
    simulator.load_data()

    # Démarrage du streaming
    simulator.start_streaming(interval=3.0)

    print("\nServeur web demarre sur http://localhost:5000")
    print("Endpoints disponibles :")
    print("  • http://localhost:5000/api/latest")
    print("  • http://localhost:5000/api/status")
    print("  • http://localhost:5000/api/devices")
    print("\nAppuyez sur Ctrl+C pour arreter")

    try:
        # Démarrage du serveur Flask
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nArret du simulateur...")
        simulator.stop_streaming()

if __name__ == "__main__":
    main()