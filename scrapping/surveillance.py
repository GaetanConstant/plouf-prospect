#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import sys
import signal
import datetime

# Configuration
SCRIPT_PRINCIPAL = "scraper.py"
DELAI_VERIFICATION = 60  # Vérifier toutes les 60 secondes
MAX_TENTATIVES = 10  # Nombre maximum de tentatives de redémarrage
DELAI_ENTRE_TENTATIVES = 120  # Délai entre les tentatives en secondes
FICHIER_LOG = "surveillance.log"

def log(message):
    """Écrire un message dans le fichier de log avec horodatage"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FICHIER_LOG, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def est_en_cours(nom_script):
    """Vérifier si le script est en cours d'exécution"""
    try:
        # Vérifier si le processus Python exécutant le script est en cours
        commande = f"ps aux | grep -v grep | grep -i 'python.*{nom_script}'"
        resultat = subprocess.run(commande, shell=True, capture_output=True, text=True)
        return len(resultat.stdout.strip()) > 0
    except Exception as e:
        log(f"Erreur lors de la vérification du processus: {e}")
        return False

def lancer_script():
    """Lancer le script principal avec l'environnement virtuel"""
    try:
        log(f"Lancement de {SCRIPT_PRINCIPAL}...")
        
        # Utiliser l'environnement virtuel pour lancer le script
        commande = f"python {SCRIPT_PRINCIPAL}"
        
        # Lancer le processus en arrière-plan
        process = subprocess.Popen(commande, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre un peu pour vérifier que le processus a bien démarré
        time.sleep(5)
        
        if process.poll() is None:  # None signifie que le processus est toujours en cours
            log(f"✅ {SCRIPT_PRINCIPAL} lancé avec succès (PID: {process.pid})")
            return True
        else:
            stdout, stderr = process.communicate()
            log(f"❌ Échec du lancement: {stderr.decode('utf-8')}")
            return False
    except Exception as e:
        log(f"❌ Erreur lors du lancement du script: {e}")
        return False

def main():
    log("=== Démarrage du système de surveillance ===")
    
    tentatives = 0
    
    while tentatives < MAX_TENTATIVES:
        # Vérifier si le script est en cours d'exécution
        if not est_en_cours(SCRIPT_PRINCIPAL):
            log(f"⚠️ {SCRIPT_PRINCIPAL} n'est pas en cours d'exécution (tentative {tentatives+1}/{MAX_TENTATIVES})")
            
            # Lancer le script
            if lancer_script():
                tentatives = 0  # Réinitialiser le compteur si le lancement réussit
            else:
                tentatives += 1
                log(f"⏳ Attente de {DELAI_ENTRE_TENTATIVES} secondes avant nouvelle tentative...")
                time.sleep(DELAI_ENTRE_TENTATIVES)
        else:
            log(f"✅ {SCRIPT_PRINCIPAL} est en cours d'exécution")
            tentatives = 0  # Réinitialiser le compteur car le script fonctionne
        
        # Attendre avant la prochaine vérification
        time.sleep(DELAI_VERIFICATION)
    
    log("❌ Nombre maximum de tentatives atteint. Arrêt de la surveillance.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Surveillance arrêtée par l'utilisateur")
    except Exception as e:
        log(f"Erreur critique: {e}")
