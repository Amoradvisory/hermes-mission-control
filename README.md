# Hermes Mission Control

**Version :** 0.1.0 (V0 — lecture seule, non intrusive)
**Statut :** Scaffolding initial — Phase 0 validation locale

## Ce que fait ce projet

Hermes Mission Control est un **plugin dashboard compagnon** pour Hermes Agent.
Il offre une interface visuelle pour créer, configurer, surveiller et piloter une flotte d'agents Hermes spécialisés.

Il ne remplace pas Hermes. Il ne modifie pas Hermes. Il s'y branche par-dessus comme un cockpit sur un réacteur.

## Ce que cette V0 ne fait PAS

- Elle ne modifie aucun fichier du coeur Hermes (config.yaml, run_agent.py, gateway/, .env, auth.json).
- Elle ne lance aucun agent.
- Elle n'ecrit dans aucun profil Hermes.
- Elle n'expose aucun secret, token ou cle API.
- Elle ne contacte aucun service externe.

**Cette V0 est en lecture seule et non intrusive.** Toutes les routes d'ecriture sont marquees dry_run=True par defaut jusqu'a validation explicite.

## Prerequis

- Hermes Agent installe et fonctionnel (hermes --version)
- Python 3.10+ avec fastapi, uvicorn, pyyaml

## Installation

```bash
git clone https://github.com/Amoradvisory/hermes-mission-control
cd hermes-mission-control
pip install fastapi uvicorn pyyaml
python dashboard/plugin_api.py
```

L'API demarre sur http://localhost:7700 par defaut.

## Endpoints disponibles

| Route | Description |
|---|---|
| GET /health | Statut du plugin |
| GET /agents | Liste des profils Hermes detectes |
| GET /agents/{id} | Detail d'un profil (config redacted) |
| GET /providers | Providers configures (secrets masques) |

## Roadmap

- Phase 0 (actuelle) : scaffolding, API read-only, redaction secrets, tests
- Phase 1 : plugin Hermes Dashboard avec tab Mission Control
- Phase 2 : agents registry complet
- Phase 3 : wizard creation/edition (dry-run, diff, rollback)
- Phase 4 : Kanban multi-agent
- Phase 5 : observabilite (logs, couts, erreurs)
- Phase 6 : export GitHub anti-secrets

---

*Hermes est le moteur. Mission Control est la verriere du cockpit.*
