#!/usr/bin/env python3
"""
Simulateur IoT avec timestamps temps réel
========================================
Version améliorée avec timestamps actuels et données organisées
"""

import pandas as pd
import time
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import queue

class RealtimeIoTSimulator:
    """Simulateur IoT avec timestamps temps réel"""

    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = []
        self.current_index = 0
        self.is_running = False
        self.data_queue = queue.Queue(maxsize=100)
        self.start_time = datetime.now()

    def load_data(self):
        """Charge et prépare les données avec timestamps actuels"""
        print("Chargement des donnees avec timestamps actuels...")

        # Charger les données et les trier
        df = pd.read_csv(self.csv_path)
        df = df.sort_values('ts')  # Trier par timestamp original

        # Prendre un échantillon représentatif des 3 dispositifs
        sample_df = df.head(1000).copy()

        print(f"Donnees chargees : {len(sample_df)} echantillons")
        print(f"Dispositifs detectes : {sample_df['device'].unique()}")

        # Créer des données avec timestamps actuels, espacés de 3 secondes
        current_time = self.start_time

        for i, (_, row) in enumerate(sample_df.iterrows()):
            # Timestamp actuel + 3 secondes par échantillon
            timestamp = current_time + timedelta(seconds=i * 3)

            data_point = {
                'timestamp': timestamp.isoformat(),
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
                    'original_timestamp': datetime.fromtimestamp(row['ts']).isoformat(),
                    'sample_index': i
                }
            }
            self.data.append(data_point)

        print(f"OK {len(self.data)} echantillons prepares")
        print(f"Periode simulation : {self.start_time.strftime('%H:%M:%S')} à {(current_time + timedelta(seconds=len(self.data)*3)).strftime('%H:%M:%S')}")
        return self.data

    def start_streaming(self, interval=3.0):
        """Démarre le streaming avec timestamps cohérents"""
        self.is_running = True
        print(f"Demarrage du streaming temps reel (intervalle: {interval}s)")

        def stream_worker():
            while self.is_running and self.current_index < len(self.data):
                data_point = self.data[self.current_index]

                # Ajouter à la queue
                if not self.data_queue.full():
                    self.data_queue.put(data_point)

                # Affichage avec timestamp actuel
                device = data_point['device_id']
                temp = data_point['sensors']['temperature']
                timestamp = datetime.fromisoformat(data_point['timestamp'])

                print(f"[{timestamp.strftime('%H:%M:%S')}] {device}: T={temp:.1f}°C")

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

        # Trier par timestamp pour garantir l'ordre chronologique
        latest_data.sort(key=lambda x: x['timestamp'])

        return latest_data

    def get_status(self):
        """Retourne le statut du simulateur"""
        return {
            'is_running': self.is_running,
            'current_index': self.current_index,
            'total_samples': len(self.data),
            'queue_size': self.data_queue.qsize(),
            'start_time': self.start_time.isoformat(),
            'current_time': datetime.now().isoformat(),
            'progress_percent': round((self.current_index / len(self.data)) * 100, 1) if self.data else 0
        }

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

    n_samples = request.args.get('n', 20, type=int)
    data = simulator.get_latest_data(n_samples)

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Statut du simulateur"""
    if simulator is None:
        return jsonify({'success': False, 'message': 'Simulateur non initialise'})

    return jsonify({
        'success': True,
        'status': simulator.get_status()
    })

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Liste des dispositifs"""
    if simulator is None or not simulator.data:
        return jsonify({'success': False, 'message': 'Aucune donnee chargee'})

    devices = list(set(item['device_id'] for item in simulator.data))
    return jsonify({
        'success': True,
        'devices': devices,
        'count': len(devices)
    })

@app.route('/', methods=['GET'])
def home():
    """Page d'accueil avec informations"""
    if simulator:
        status = simulator.get_status()
        return jsonify({
            'message': 'Simulateur IoT Temps Reel',
            'status': status,
            'endpoints': {
                '/api/latest?n=X': 'Dernieres donnees (X=nombre)',
                '/api/status': 'Statut detaille',
                '/api/devices': 'Liste des dispositifs'
            }
        })
    else:
        return jsonify({
            'message': 'Simulateur IoT non initialise',
            'endpoints': ['Redemarrer le simulateur']
        })

def main():
    """Fonction principale"""
    global simulator

    print("SIMULATEUR IOT TEMPS REEL")
    print("="*50)

    # Initialisation du simulateur
    simulator = RealtimeIoTSimulator('iot_data_sample.csv')
    simulator.load_data()

    # Démarrage du streaming
    simulator.start_streaming(interval=3.0)

    print("\nServeur web demarre sur http://localhost:5000")
    print("Endpoints disponibles :")
    print("  • http://localhost:5000/api/latest?n=10")
    print("  • http://localhost:5000/api/status")
    print("  • http://localhost:5000/api/devices")
    print("  • http://localhost:5000/ (accueil)")
    print("\nTimestamps : TEMPS REEL (non historiques)")
    print("Mise à jour : Toutes les 3 secondes")
    print("Dashboard : http://localhost:5174")
    print("\nAppuyez sur Ctrl+C pour arreter")

    try:
        # Démarrage du serveur Flask
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nArret du simulateur...")
        simulator.stop_streaming()
        print("Simulateur arrete proprement")

if __name__ == "__main__":
    main()