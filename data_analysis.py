#!/usr/bin/env python3
"""
Analyse exploratoire des données IoT
===================================
Script pour l'exploration, le nettoyage et la visualisation des données de capteurs IoT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
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
        print(f"✅ Données chargées : {len(self.data)} lignes, {len(self.data.columns)} colonnes")
        return self.data

    def basic_info(self):
        """Affiche les informations de base sur le dataset"""
        print("\n" + "="*50)
        print("📋 INFORMATIONS GÉNÉRALES")
        print("="*50)

        print(f"Forme du dataset : {self.data.shape}")
        print(f"Période des données : {pd.to_datetime(self.data['ts'], unit='s').min()} à {pd.to_datetime(self.data['ts'], unit='s').max()}")
        print(f"Nombre de dispositifs uniques : {self.data['device'].nunique()}")
        print(f"Dispositifs : {list(self.data['device'].unique())}")

        print("\n📊 Types de données :")
        print(self.data.dtypes)

        print("\n📊 Statistiques descriptives :")
        print(self.data.describe())

        print("\n🔍 Valeurs manquantes :")
        print(self.data.isnull().sum())

        print("\n🔍 Premières lignes :")
        print(self.data.head())

    def clean_data(self):
        """Nettoie et prépare les données"""
        print("\n" + "="*50)
        print("🧹 NETTOYAGE DES DONNÉES")
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
        print("🔍 Détection des outliers...")
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

        print(f"✅ Données nettoyées : {len(self.cleaned_data)} lignes conservées")
        return self.cleaned_data

    def create_visualizations(self):
        """Crée diverses visualisations des données"""
        print("\n" + "="*50)
        print("📈 CRÉATION DES VISUALISATIONS")
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
        plt.show()

        # 2. Évolution temporelle des mesures
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle('Évolution Temporelle des Capteurs', fontsize=16, fontweight='bold')

        # Échantillonnage pour la visualisation (toutes les 100 lignes)
        sample_data = self.cleaned_data.iloc[::100]

        for i, col in enumerate(numeric_cols):
            row = i // 2
            col_idx = i % 2

            for device in self.cleaned_data['device'].unique():
                device_data = sample_data[sample_data['device'] == device]
                axes[row, col_idx].plot(device_data['datetime'], device_data[col],
                                       label=device, alpha=0.7, linewidth=1)

            axes[row, col_idx].set_title(f'Évolution {col.title()}')
            axes[row, col_idx].set_xlabel('Temps')
            axes[row, col_idx].set_ylabel(col.title())
            axes[row, col_idx].legend()
            axes[row, col_idx].tick_params(axis='x', rotation=45)

        # Supprime le subplot vide
        fig.delaxes(axes[2, 1])
        plt.tight_layout()
        plt.savefig('evolution_temporelle.png', dpi=300, bbox_inches='tight')
        plt.show()

        # 3. Matrice de corrélation
        plt.figure(figsize=(10, 8))
        correlation_matrix = self.cleaned_data[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Matrice de Corrélation entre les Capteurs', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()

        # 4. Distribution des événements de mouvement et lumière
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Mouvement par dispositif
        motion_counts = self.cleaned_data.groupby(['device', 'motion']).size().unstack(fill_value=0)
        motion_counts.plot(kind='bar', ax=axes[0], color=['skyblue', 'orange'])
        axes[0].set_title('Détection de Mouvement par Dispositif')
        axes[0].set_xlabel('Dispositif')
        axes[0].set_ylabel('Nombre de mesures')
        axes[0].legend(['Pas de mouvement', 'Mouvement détecté'])
        axes[0].tick_params(axis='x', rotation=45)

        # Lumière par dispositif
        light_counts = self.cleaned_data.groupby(['device', 'light']).size().unstack(fill_value=0)
        light_counts.plot(kind='bar', ax=axes[1], color=['navy', 'gold'])
        axes[1].set_title('État de la Lumière par Dispositif')
        axes[1].set_xlabel('Dispositif')
        axes[1].set_ylabel('Nombre de mesures')
        axes[1].legend(['Lumière éteinte', 'Lumière allumée'])
        axes[1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('evenements_mouvement_lumiere.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("✅ Visualisations créées et sauvegardées")

    def generate_statistics_report(self):
        """Génère un rapport statistique détaillé"""
        print("\n" + "="*50)
        print("📊 RAPPORT STATISTIQUE DÉTAILLÉ")
        print("="*50)

        numeric_cols = ['temp', 'humidity', 'co', 'lpg', 'smoke']

        # Statistiques par dispositif
        print("📱 Statistiques par dispositif :")
        for device in self.cleaned_data['device'].unique():
            device_data = self.cleaned_data[self.cleaned_data['device'] == device]
            print(f"\n🔸 Dispositif {device}:")
            print(f"  • Nombre de mesures : {len(device_data)}")
            print(f"  • Période : {device_data['datetime'].min()} à {device_data['datetime'].max()}")

            for col in numeric_cols:
                mean_val = device_data[col].mean()
                std_val = device_data[col].std()
                min_val = device_data[col].min()
                max_val = device_data[col].max()
                print(f"  • {col.title()} : µ={mean_val:.3f}, σ={std_val:.3f}, min={min_val:.3f}, max={max_val:.3f}")

        # Corrélations interessantes
        print("\n🔗 Corrélations intéressantes (|r| > 0.3) :")
        correlation_matrix = self.cleaned_data[numeric_cols].corr()
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j and abs(correlation_matrix.loc[col1, col2]) > 0.3:
                    print(f"  • {col1} ↔ {col2} : r = {correlation_matrix.loc[col1, col2]:.3f}")

        # Événements spéciaux
        print("\n🎯 Événements spéciaux :")
        motion_events = self.cleaned_data[self.cleaned_data['motion'] == True]
        light_events = self.cleaned_data[self.cleaned_data['light'] == True]

        print(f"  • Détections de mouvement : {len(motion_events)} ({len(motion_events)/len(self.cleaned_data)*100:.2f}%)")
        print(f"  • Activations de lumière : {len(light_events)} ({len(light_events)/len(self.cleaned_data)*100:.2f}%)")

        # Qualité de l'air préoccupante
        high_co = self.cleaned_data[self.cleaned_data['co'] > self.cleaned_data['co'].quantile(0.95)]
        high_smoke = self.cleaned_data[self.cleaned_data['smoke'] > self.cleaned_data['smoke'].quantile(0.95)]

        print(f"  • Niveaux élevés de CO (>95e percentile) : {len(high_co)} événements")
        print(f"  • Niveaux élevés de fumée (>95e percentile) : {len(high_smoke)} événements")

    def save_processed_data(self):
        """Sauvegarde les données nettoyées"""
        output_file = 'iot_data_cleaned.csv'
        self.cleaned_data.to_csv(output_file, index=False)
        print(f"✅ Données nettoyées sauvegardées dans {output_file}")

        # Sauvegarde un échantillon pour le dashboard
        sample_data = self.cleaned_data.sample(n=min(1000, len(self.cleaned_data))).copy()
        sample_data.to_csv('iot_data_sample.csv', index=False)
        print(f"✅ Échantillon de données sauvegardé dans iot_data_sample.csv")

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
    print("✅ Analyse des données IoT terminée avec succès !")
    print("📁 Fichiers générés :")
    print("   • iot_data_cleaned.csv - Données nettoyées complètes")
    print("   • iot_data_sample.csv - Échantillon pour le dashboard")
    print("   • distribution_capteurs.png - Distributions par capteur")
    print("   • evolution_temporelle.png - Évolution temporelle")
    print("   • correlation_matrix.png - Matrice de corrélation")
    print("   • evenements_mouvement_lumiere.png - Événements spéciaux")

if __name__ == "__main__":
    main()