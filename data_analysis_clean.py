#!/usr/bin/env python3
"""
Analyse exploratoire des données IoT (version sans emojis)
========================================================
Script pour l'exploration, le nettoyage et la visualisation des données de capteurs IoT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class IoTDataAnalyzer:
    def __init__(self, csv_path):
        """Initialise l'analyseur avec le chemin du fichier CSV"""
        self.csv_path = csv_path
        self.data = None
        self.cleaned_data = None

    def load_data(self):
        """Charge les données depuis le fichier CSV"""
        print("Chargement des donnees...")
        self.data = pd.read_csv(self.csv_path)
        print(f"Donnees chargees : {len(self.data)} lignes, {len(self.data.columns)} colonnes")
        return self.data

    def basic_info(self):
        """Affiche les informations de base sur le dataset"""
        print("\n" + "="*50)
        print("INFORMATIONS GENERALES")
        print("="*50)

        print(f"Forme du dataset : {self.data.shape}")
        print(f"Periode des donnees : {pd.to_datetime(self.data['ts'], unit='s').min()} a {pd.to_datetime(self.data['ts'], unit='s').max()}")
        print(f"Nombre de dispositifs uniques : {self.data['device'].nunique()}")
        print(f"Dispositifs : {list(self.data['device'].unique())}")

        print("\nTypes de donnees :")
        print(self.data.dtypes)

        print("\nStatistiques descriptives :")
        print(self.data.describe())

        print("\nValeurs manquantes :")
        print(self.data.isnull().sum())

        print("\nPremieres lignes :")
        print(self.data.head())

    def clean_data(self):
        """Nettoie et prépare les données"""
        print("\n" + "="*50)
        print("NETTOYAGE DES DONNEES")
        print("="*50)

        # Copie des données originales
        self.cleaned_data = self.data.copy()

        # Conversion du timestamp
        self.cleaned_data['datetime'] = pd.to_datetime(self.cleaned_data['ts'], unit='s')
        self.cleaned_data['hour'] = self.cleaned_data['datetime'].dt.hour
        self.cleaned_data['day'] = self.cleaned_data['datetime'].dt.day

        # Conversion des colonnes booléennes
        self.cleaned_data['light'] = self.cleaned_data['light'].map({'true': True, 'false': False})
        self.cleaned_data['motion'] = self.cleaned_data['motion'].map({'true': True, 'false': False})

        # Conversion des colonnes numériques
        numeric_cols = ['co', 'humidity', 'lpg', 'smoke', 'temp']
        for col in numeric_cols:
            self.cleaned_data[col] = pd.to_numeric(self.cleaned_data[col], errors='coerce')

        # Détection des outliers avec IQR
        print("Detection des outliers...")
        outliers_info = {}
        for col in numeric_cols:
            Q1 = self.cleaned_data[col].quantile(0.25)
            Q3 = self.cleaned_data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = self.cleaned_data[(self.cleaned_data[col] < lower_bound) |
                                        (self.cleaned_data[col] > upper_bound)]
            outliers_info[col] = len(outliers)
            print(f"  {col}: {len(outliers)} outliers ({len(outliers)/len(self.cleaned_data)*100:.2f}%)")

        print(f"Donnees nettoyees : {len(self.cleaned_data)} lignes conservees")
        return self.cleaned_data

    def create_visualizations(self):
        """Crée diverses visualisations des données"""
        print("\n" + "="*50)
        print("CREATION DES VISUALISATIONS")
        print("="*50)

        # Configuration du style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        # 1. Distribution des capteurs par dispositif
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Distribution des Mesures par Capteur et Dispositif', fontsize=16, fontweight='bold')

        numeric_cols = ['temp', 'humidity', 'co', 'lpg', 'smoke']
        for i, col in enumerate(numeric_cols):
            row = i // 3
            col_idx = i % 3
            sns.boxplot(data=self.cleaned_data, x='device', y=col, ax=axes[row, col_idx])
            axes[row, col_idx].set_title(f'Distribution {col.title()}')
            axes[row, col_idx].tick_params(axis='x', rotation=45)

        # Supprime le subplot vide
        fig.delaxes(axes[1, 2])
        plt.tight_layout()
        plt.savefig('distribution_capteurs.png', dpi=300, bbox_inches='tight')
        print("Graphique distribution_capteurs.png cree")
        plt.close()

        # 2. Évolution temporelle des mesures
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle('Evolution Temporelle des Capteurs', fontsize=16, fontweight='bold')

        # Échantillonnage pour la visualisation (toutes les 100 lignes)
        sample_data = self.cleaned_data.iloc[::100]

        for i, col in enumerate(numeric_cols):
            row = i // 2
            col_idx = i % 2

            for device in self.cleaned_data['device'].unique():
                device_data = sample_data[sample_data['device'] == device]
                axes[row, col_idx].plot(device_data['datetime'], device_data[col],
                                       label=device, alpha=0.7, linewidth=1)

            axes[row, col_idx].set_title(f'Evolution {col.title()}')
            axes[row, col_idx].set_xlabel('Temps')
            axes[row, col_idx].set_ylabel(col.title())
            axes[row, col_idx].legend()
            axes[row, col_idx].tick_params(axis='x', rotation=45)

        # Supprime le subplot vide
        fig.delaxes(axes[2, 1])
        plt.tight_layout()
        plt.savefig('evolution_temporelle.png', dpi=300, bbox_inches='tight')
        print("Graphique evolution_temporelle.png cree")
        plt.close()

        # 3. Matrice de corrélation
        plt.figure(figsize=(10, 8))
        correlation_matrix = self.cleaned_data[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Matrice de Correlation entre les Capteurs', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
        print("Graphique correlation_matrix.png cree")
        plt.close()

        print("Visualisations creees et sauvegardees")

    def generate_statistics_report(self):
        """Génère un rapport statistique détaillé"""
        print("\n" + "="*50)
        print("RAPPORT STATISTIQUE DETAILLE")
        print("="*50)

        numeric_cols = ['temp', 'humidity', 'co', 'lpg', 'smoke']

        # Statistiques par dispositif
        print("Statistiques par dispositif :")
        for device in self.cleaned_data['device'].unique():
            device_data = self.cleaned_data[self.cleaned_data['device'] == device]
            print(f"\nDispositif {device}:")
            print(f"  • Nombre de mesures : {len(device_data)}")
            print(f"  • Periode : {device_data['datetime'].min()} a {device_data['datetime'].max()}")

            for col in numeric_cols:
                mean_val = device_data[col].mean()
                std_val = device_data[col].std()
                min_val = device_data[col].min()
                max_val = device_data[col].max()
                print(f"  • {col.title()} : moyenne={mean_val:.3f}, ecart-type={std_val:.3f}, min={min_val:.3f}, max={max_val:.3f}")

        # Corrélations interessantes
        print("\nCorrelations interessantes (|r| > 0.3) :")
        correlation_matrix = self.cleaned_data[numeric_cols].corr()
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j and abs(correlation_matrix.loc[col1, col2]) > 0.3:
                    print(f"  • {col1} <-> {col2} : r = {correlation_matrix.loc[col1, col2]:.3f}")

        # Événements spéciaux
        print("\nEvenements speciaux :")
        motion_events = self.cleaned_data[self.cleaned_data['motion'] == True]
        light_events = self.cleaned_data[self.cleaned_data['light'] == True]

        print(f"  • Detections de mouvement : {len(motion_events)} ({len(motion_events)/len(self.cleaned_data)*100:.2f}%)")
        print(f"  • Activations de lumiere : {len(light_events)} ({len(light_events)/len(self.cleaned_data)*100:.2f}%)")

    def save_processed_data(self):
        """Sauvegarde les données nettoyées"""
        output_file = 'iot_data_cleaned.csv'
        self.cleaned_data.to_csv(output_file, index=False)
        print(f"Donnees nettoyees sauvegardees dans {output_file}")

        # Sauvegarde un échantillon pour le dashboard
        sample_data = self.cleaned_data.sample(n=min(1000, len(self.cleaned_data))).copy()
        sample_data.to_csv('iot_data_sample.csv', index=False)
        print(f"Echantillon de donnees sauvegarde dans iot_data_sample.csv")

def main():
    """Fonction principale d'analyse"""
    print("Demarrage de l'analyse des donnees IoT")
    print("="*60)

    # Initialisation de l'analyseur
    analyzer = IoTDataAnalyzer('iot_telemetry_data.csv')

    # Chargement des données
    analyzer.load_data()

    # Informations de base
    analyzer.basic_info()

    # Nettoyage des données
    analyzer.clean_data()

    # Création des visualisations
    analyzer.create_visualizations()

    # Rapport statistique
    analyzer.generate_statistics_report()

    # Sauvegarde des données traitées
    analyzer.save_processed_data()

    print("\n" + "="*60)
    print("Analyse des donnees IoT terminee avec succes !")
    print("Fichiers generes :")
    print("   • iot_data_cleaned.csv - Donnees nettoyees completes")
    print("   • iot_data_sample.csv - Echantillon pour le dashboard")
    print("   • distribution_capteurs.png - Distributions par capteur")
    print("   • evolution_temporelle.png - Evolution temporelle")
    print("   • correlation_matrix.png - Matrice de correlation")

if __name__ == "__main__":
    main()