import os
import sys
import subprocess
import pandas as pd
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI(
    title="Plouf Prospect API",
    description="API de scraping et d'enrichissement de prospects",
    version="1.0.0"
)

# CORS enabled for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION DES CHEMINS ---
# Dossier actuel de l'API: /api
API_DIR = os.path.dirname(os.path.abspath(__file__))
# Dossier racine du projet: /
ROOT_DIR = os.path.dirname(API_DIR)
# Dossier des scripts de scraping: /scrapping
SCRAPPING_DIR = os.path.join(ROOT_DIR, "scrapping")

# Ajouter scrapping au path pour les imports
if SCRAPPING_DIR not in sys.path:
    sys.path.append(SCRAPPING_DIR)

# Chemins des fichiers dans le dossier scrapping
MOTS_CLES_CSV = os.path.join(SCRAPPING_DIR, "mots_cles.csv")
RESULTATS_DIR_RAW = os.path.join(SCRAPPING_DIR, "resultats")
RESULTATS_DIR_ENRICHED = os.path.join(SCRAPPING_DIR, "resultats_enrichis")
RESULTATS_DIR_DIRIGEANTS = os.path.join(SCRAPPING_DIR, "resultats_dirigeants")

RESULTATS_DIR_CONSOLIDATED = os.path.join(SCRAPPING_DIR, "resultats_consolides")

FICHIER_RAW = os.path.join(RESULTATS_DIR_RAW, "resultats_complets.csv")
FICHIER_ENRICHI = os.path.join(RESULTATS_DIR_ENRICHED, "resultats_enrichis_complets.csv")
FICHIER_DIRIGEANTS = os.path.join(RESULTATS_DIR_DIRIGEANTS, "resultats_dirigeants.csv")
FICHIER_GMB = os.path.join(RESULTATS_DIR_DIRIGEANTS, "resultats_dirigeants_enrichis_gmb.csv")
FICHIER_WHOIS = os.path.join(RESULTATS_DIR_DIRIGEANTS, "resultats_finaux_complets.csv")
FICHIER_CONSOLIDE = os.path.join(RESULTATS_DIR_CONSOLIDATED, "base_prospects_finale.csv")

# Ensure directories exist
for d in [RESULTATS_DIR_RAW, RESULTATS_DIR_ENRICHED, RESULTATS_DIR_DIRIGEANTS, RESULTATS_DIR_CONSOLIDATED]:
    os.makedirs(d, exist_ok=True)

class ProcessRequest(BaseModel):
    keyword: str
    zipcode: str
    max_fiches: Optional[int] = 5

def run_workflow(queries: List[str], max_fiches: int = 5):
    """
    Exécute le workflow complet : Scraping -> Web -> Dirigeants -> GMB -> Whois -> Consolidation
    """
    # 1. Sauvegarder les mots-clés
    df_queries = pd.DataFrame({"mot_cle": queries})
    df_queries.to_csv(MOTS_CLES_CSV, index=False)
    
    # 2. Nettoyer les anciens fichiers
    for f in [FICHIER_RAW, FICHIER_ENRICHI, FICHIER_DIRIGEANTS, FICHIER_GMB, FICHIER_WHOIS, FICHIER_CONSOLIDE]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
    
    # 3. Lancer le Scraping (+ Enrichissement sites web)
    try:
        print(f"DEBUG: Démarrage du scraping dans {SCRAPPING_DIR}...")
        subprocess.run([sys.executable, os.path.join(SCRAPPING_DIR, "scraper.py"), str(max_fiches)], 
                       cwd=SCRAPPING_DIR, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Erreur durant le scraping: {str(e)}")
    
    # 4. Lancer la recherche de dirigeants
    try:
        print("DEBUG: Recherche des dirigeants...")
        # Import dynamique du module dans le dossier scrapping
        import recherche_dirigeants
        # On force le rechargement si nécessaire ou on s'assure que le path est bon
        success = recherche_dirigeants.process_file(FICHIER_ENRICHI, FICHIER_DIRIGEANTS)
        if not success:
            raise Exception("La recherche de dirigeants a échoué")
    except Exception as e:
        raise Exception(f"Erreur durant la recherche de dirigeants: {str(e)}")

    # 5. Lancer l'enrichissement GMB
    try:
        print("DEBUG: Enrichissement GMB...")
        subprocess.run([sys.executable, os.path.join(SCRAPPING_DIR, "enrichisseur_gmb.py")], 
                       cwd=SCRAPPING_DIR, check=True)
    except Exception as e:
        print(f"⚠️ Alerte: L'enrichissement GMB a échoué. Erreur: {e}")

    # 6. Lancer l'enrichissement Whois
    try:
        print("DEBUG: Enrichissement Whois...")
        subprocess.run([sys.executable, os.path.join(SCRAPPING_DIR, "enrichisseur_whois.py")], 
                       cwd=SCRAPPING_DIR, check=True)
    except Exception as e:
        print(f"⚠️ Alerte: L'enrichissement Whois a échoué. Erreur: {e}")

    # 7. Lancer la consolidation finale
    try:
        print("DEBUG: Consolidation finale...")
        subprocess.run([sys.executable, os.path.join(SCRAPPING_DIR, "consolidation_prospects.py")], 
                       cwd=SCRAPPING_DIR, check=True)
    except Exception as e:
        print(f"⚠️ Alerte: La consolidation a échoué. Erreur: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/results")
def get_results():
    """
    Retourne les dernières données consolidées au format JSON.
    """
    final_file = FICHIER_CONSOLIDE
    
    if not os.path.exists(final_file):
        # Fallback si pas de fichier consolidé, on essaie le fichier intermédiaire le plus avancé
        for f in [FICHIER_WHOIS, FICHIER_GMB, FICHIER_DIRIGEANTS]:
             if os.path.exists(f):
                 final_file = f
                 break
    
    if not os.path.exists(final_file):
        print(f"DEBUG: No final file found.")
        return []
    
    try:
        print(f"DEBUG: Reading file {final_file}")
        df = pd.read_csv(final_file)
        # Nettoyer les NaN pour le JSON
        df = df.fillna("")
        data = df.to_dict(orient="records")
        print(f"DEBUG: Returning {len(data)} records")
        return data
    except Exception as e:
        print(f"DEBUG: Error reading CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_single(request: ProcessRequest):
    query = f"{request.keyword} {request.zipcode} FR"
    try:
        run_workflow([query], request.max_fiches)
        
        if os.path.exists(FICHIER_CONSOLIDE):
            return FileResponse(
                path=FICHIER_CONSOLIDE, 
                filename=f"prospects_{request.zipcode}.csv",
                media_type="text/csv"
            )
        else:
            raise HTTPException(status_code=500, detail="Aucun fichier de résultat consolidé n'a été généré.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_csv")
async def process_batch(
    file: UploadFile = File(...), 
    max_fiches: int = Form(5)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés.")
        
    try:
        contents = await file.read()
        df_upload = pd.read_csv(io.BytesIO(contents), sep=None, engine='python', dtype=str)
        
        df_upload.columns = [c.strip() for c in df_upload.columns]
        col_soc = next((c for c in df_upload.columns if 'sociét' in c.lower() or 'entreprise' in c.lower()), None)
        col_code = next((c for c in df_upload.columns if 'code' in c.lower() or 'cp' in c.lower() or 'postal' in c.lower()), None)
        
        if not col_soc or not col_code:
            raise HTTPException(status_code=400, detail="Colonnes essentielles non trouvées.")
            
        df_upload[col_code] = df_upload[col_code].astype(str).str.strip().str.zfill(5)
        df_upload[col_soc] = df_upload[col_soc].astype(str).str.strip()
        
        queries = (df_upload[col_soc] + " " + df_upload[col_code] + " FR").tolist()
        
        run_workflow(queries, max_fiches)
        
        final_file = FICHIER_CONSOLIDE
        if not os.path.exists(final_file):
             # Fallback
             final_file = FICHIER_GMB if os.path.exists(FICHIER_GMB) else FICHIER_DIRIGEANTS
        
        if os.path.exists(final_file):
            return FileResponse(
                path=final_file, 
                filename="prospects_batch.csv",
                media_type="text/csv"
            )
        else:
            raise HTTPException(status_code=500, detail="Fichier non généré.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement : {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
