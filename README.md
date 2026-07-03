# Competitive Price Monitor & Tracker

**Monitor competitor prices automatically and get alerted when they change.**

If you run an e-commerce store, you need to know when your competitors or suppliers change their prices — but checking 200 products manually every week is impossible.

This product does it in two phases:

1. **Extract** — scrape product data (prices, stock, SKUs) from password-protected marketplaces using Playwright
2. **Track** — compare snapshots over time and generate a report of what changed

## Pipeline completo

```
scraper.py  →  CSV snapshot  →  track.py  →  price change report
```

## Quick start

```bash
# Phase 1: Extraer productos
cp .env.example .env          # editá credenciales
playwright install chromium   # primera vez
python scraper.py             # genera output/dropi_<fecha>.csv

# Phase 2: Detectar cambios contra el snapshot anterior
python track.py output/dropi_20260614_235254.csv
```

## Phase 1 — Extracción (scraper.py)

Scrapea marketplaces tipo Dropi que cargan catálogos dinámicamente vía API:

1. Abre browser visible para login manual con 2FA
2. Captura el token Bearer interceptando la API
3. Navega categorías y exporta a CSV y JSON

## Phase 2 — Tracking (track.py)

Compara dos snapshots de precios y muestra qué cambió:

```bash
python track.py output/dropi_20260614_235254.csv
```

Output:
```
=== PRICE CHANGES DETECTED ===
Product                  | Old      | New      | Change
Cepillo Automatico       | $8000    | $8500    | +$500 🔺
Cama Perro Grande        | $15000   | $14200   | -$800 🔻
```

También genera un historial en SQLite para trackear tendencias a largo plazo.

## Uso típico

```bash
# Lunes: extraer precios
python scraper.py

# Comparar con el lunes anterior
python track.py output/dropi_20260614_235254.csv

# Automatico con cron (Linux/Mac)
0 9 * * 1 cd /ruta/proyecto && python scraper.py && python track.py output/$(ls -t output/*.csv | head -1)
```

---

**Tech stack:** Python · Playwright · SQLite · httpx
