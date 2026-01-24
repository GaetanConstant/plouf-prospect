#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
from pathlib import Path
import requests
import sys

# Base officielle des codes postaux – La Poste (dataNOVA)
LAPOSTE_CSV_URL = (
    "https://datanova.laposte.fr/data-fair/api/v1/datasets/"
    "laposte-hexasmal/metadata-attachments/base-officielle-codes-postaux.csv"
)

# -----------------------------
# Utils
# -----------------------------
def download_if_needed(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return

    print(f"Téléchargement du fichier La Poste (volumineux) → {dest}")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

def sniff_delimiter(sample: str) -> str:
    for d in (";", ",", "\t"):
        if sample.count(d) > 10:
            return d
    return ";"

# -----------------------------
# Extraction CP par département
# -----------------------------
def extract_postal_codes_by_dept(source_csv: Path, dept: str, out_csv: Path) -> int:
    dept = dept.upper()
    codes = set()

    with open(source_csv, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        delim = sniff_delimiter(sample)
        f.seek(0)

        reader = csv.DictReader(f, delimiter=delim)

        fields = {c.lower(): c for c in reader.fieldnames or []}
        insee_col = fields.get("code_commune_insee")
        cp_col = fields.get("code_postal")

        if not insee_col or not cp_col:
            raise RuntimeError(f"Colonnes requises introuvables: {reader.fieldnames}")

        for row in reader:
            insee = (row.get(insee_col) or "").strip().upper()
            cp = (row.get(cp_col) or "").strip()

            if not insee or not cp:
                continue

            # Cas général + Corse (2A / 2B)
            if insee.startswith(dept):
                codes.add(cp)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["postal_code"])
        for cp in sorted(codes):
            w.writerow([cp])

    return len(codes)

# -----------------------------
# Mots-clés / prospection
# -----------------------------
def load_keywords_from_csv(path: Path, column: str | None = None) -> list[str]:
    keywords = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return keywords
        col = column or reader.fieldnames[0]
        for row in reader:
            kw = (row.get(col) or "").strip()
            if kw:
                keywords.append(kw)
    return keywords

def export_queries(cp_csv: Path, keywords: list[str], out_csv: Path) -> int:
    cps = []
    with open(cp_csv, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            cp = (row.get("postal_code") or "").strip()
            if cp:
                cps.append(cp)

    count = 0
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        # Format demandé : entreprise;code postal
        w = csv.writer(f, delimiter=";")
        w.writerow(["entreprise", "code postal"])
        for kw in keywords:
            for cp in cps:
                w.writerow([kw, cp])
                count += 1
    return count

# -----------------------------
# CLI
# -----------------------------
def main():
    base_dir = Path(__file__).parent / "resultats_codepostaux"
    base_dir.mkdir(parents=True, exist_ok=True)

    ap = argparse.ArgumentParser(
        description="Extrait tous les codes postaux d’un département (Base officielle La Poste)."
    )
    ap.add_argument("--dept", required=True, help="Numéro de département (ex: 69, 01, 75, 2A, 2B)")
    ap.add_argument("--cache", default=str(base_dir / "base_officielle_codes_postaux.csv"), help="Cache local du CSV La Poste")
    ap.add_argument("--out-cp", default=None, help="CSV de sortie des codes postaux")
    ap.add_argument("--keyword", default=None, help="Mot-clé unique (ex: Boulangerie)")
    ap.add_argument("--keywords-csv", default=None, help="CSV de mots-clés (optionnel)")
    ap.add_argument("--keywords-col", default=None, help="Nom de colonne mots-clés (optionnel)")
    ap.add_argument("--out-queries", default=None, help="CSV des requêtes (optionnel)")
    args = ap.parse_args()

    dept = args.dept.upper()
    cache = Path(args.cache)

    out_cp = Path(args.out_cp or f"codes_postaux_{dept}.csv")
    if not out_cp.is_absolute():
        out_cp = base_dir / out_cp

    out_queries = Path(args.out_queries or f"requetes_prospection_{dept}.csv")
    if not out_queries.is_absolute():
        out_queries = base_dir / out_queries

    download_if_needed(LAPOSTE_CSV_URL, cache)
    nb = extract_postal_codes_by_dept(cache, dept, out_cp)
    print(f"✅ {nb} codes postaux trouvés pour le département {dept}")
    print(f"📄 Fichier : {out_cp}")

    keywords = []
    if args.keyword:
        keywords = [args.keyword]
    elif args.keywords_csv:
        keywords = load_keywords_from_csv(Path(args.keywords_csv), args.keywords_col)

    if keywords:
        n = export_queries(out_cp, keywords, out_queries)
        print(f"📄 Requêtes générées : {out_queries} ({n} lignes)")
    else:
        if args.keywords_csv:
            print("⚠️ Aucun mot-clé trouvé, génération des requêtes ignorée.", file=sys.stderr)

if __name__ == "__main__":
    main()