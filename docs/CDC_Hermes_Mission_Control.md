# Cahier des charges - Hermes Mission Control

**Version :** 1.0  
**Date :** 25 mai 2026  
**Objet :** interface séparée de pilotage, visualisation et configuration d'une flotte d'agents Hermes, sans modification du moteur Hermes existant.  
**Hypothèse de travail :** le Hermes installé est `NousResearch/hermes-agent`. Si ton installation correspond à un autre projet nommé Hermes, l'architecture reste valable, mais les adaptateurs techniques devront être changés.

---

## 1. Thèse produit

Il ne faut pas construire un nouveau Hermes : il faut construire **un cockpit compagnon** qui utilise Hermes tel qu'il existe déjà, avec ses profils, son Kanban, son dashboard, ses providers, ses skills et son API, comme une tour de contrôle posée à côté du réacteur.

La bonne image : Hermes est le moteur et l'équipage. Hermes Mission Control est la verrière du cockpit, les voyants, les leviers, les écrans radar et le journal de bord.

---

## 2. Ce qu'on ne touche pas

Le principe fondateur du projet : **zéro modification intrusive du cœur Hermes**.

Interdits :

- modifier `run_agent.py`, `model_tools.py`, `hermes_state.py`, `gateway/run.py` ou les fichiers internes Hermes pour ajouter l'interface ;
- remplacer le dashboard Hermes natif ;
- écrire directement dans les fichiers Hermes sans passer par un adaptateur contrôlé ;
- stocker les clés API dans l'application Mission Control ;
- lancer des agents en mode non sécurisé par défaut ;
- confondre profils Hermes, workspaces et sandboxing.

Autorisés :

- utiliser les commandes Hermes existantes ;
- utiliser les endpoints REST du dashboard Hermes ;
- créer un plugin dashboard Hermes ;
- créer des profils Hermes via les commandes documentées ;
- lire et afficher l'état des sessions, logs, jobs cron, toolsets, skills et board Kanban ;
- créer un dépôt GitHub autonome qui s'installe comme plugin ou sidecar.

---

## 3. Recherche et éléments structurants

### 3.1 Hermes possède déjà le socle multi-agent

Hermes Agent dispose déjà d'un système de profils : chaque profil est un agent indépendant avec son propre `config.yaml`, `.env`, `SOUL.md`, ses mémoires, sessions, skills, cron jobs et état de gateway. La documentation indique aussi qu'un profil peut être créé avec une description, notamment pour servir de worker Kanban.

Conclusion : le concept “donner un nom, une mission, un provider et des capacités à un agent” doit se mapper sur les **profiles Hermes**, pas sur une base de données parallèle inventée de zéro.

### 3.2 Hermes Kanban est la bonne primitive pour visualiser le travail multi-agent

Hermes Kanban est décrit comme un tableau durable partagé entre profils. Chaque tâche est persistée dans SQLite, chaque handoff est traçable, chaque worker est un processus OS avec identité. C'est plus robuste que de simples subagents éphémères.

Conclusion : l'interface doit afficher les agents et les tâches sous forme de **Mission Control + Kanban + Timeline**, avec les profils en “lanes”.

### 3.3 Hermes Dashboard est extensible

Le dashboard Hermes peut être étendu par thèmes, plugins UI et plugins backend FastAPI, sans fork du code Hermes. Les plugins peuvent ajouter des tabs, injecter des widgets dans des slots et exposer des endpoints sous `/api/plugins/<name>/`.

Conclusion : le meilleur chemin V1 est un **plugin de dashboard Hermes**, distribué dans un repo GitHub autonome, plutôt qu'une application web totalement séparée qui dupliquerait tout.

### 3.4 L'API Hermes donne déjà les données de monitoring

Le dashboard expose des endpoints pour le statut, les sessions, la configuration, les variables d'environnement redacted, les logs, l'analytics d'usage, les jobs cron, les skills et les toolsets.

Conclusion : Mission Control doit d'abord consommer l'existant, puis ajouter seulement les endpoints manquants.

### 3.5 L'industrie converge vers le “mission control” multi-agent

GitHub Agent HQ présente le même mouvement : une interface unifiée pour assigner, suivre, gouverner et auditer des agents, avec agents personnalisés, prompts, outils, contexte et permissions.

Conclusion : le produit doit assumer le vocabulaire de contrôle : assigner, observer, interrompre, reprendre, auditer, comparer, gouverner.

---

## 4. Vision produit

**Nom de travail :** Hermes Mission Control  
**Type :** plugin dashboard Hermes + backend local FastAPI + option sidecar autonome  
**But :** donner à l'utilisateur une interface visuelle pour créer, configurer, surveiller et piloter une flotte d'agents Hermes spécialisés.

### Promesse

Depuis une seule interface, l'utilisateur peut :

1. voir tous ses agents Hermes ;
2. créer un nouvel agent nommé ;
3. choisir s'il hérite du provider principal ou possède son propre provider ;
4. définir sa mission, son rôle, ses limites, ses skills, ses outils et son workspace ;
5. l'affecter à une tâche ou un board Kanban ;
6. suivre ce qu'il fait en temps réel ou quasi temps réel ;
7. consulter ses logs, sessions, coûts, erreurs, blocages et livrables ;
8. l'arrêter, le relancer, le mettre en pause ou le dupliquer ;
9. exporter la configuration vers GitHub.

---

## 5. Positionnement technique

### Option A - Plugin Hermes Dashboard, recommandée

**Choix recommandé.**

Le repo GitHub contient un plugin installable dans `~/.hermes/plugins/hermes-mission-control/dashboard/`.

Avantages :

- respecte l'architecture Hermes ;
- pas de fork ;
- local-first ;
- accès direct aux SDK, endpoints et composants dashboard ;
- installation légère ;
- meilleure compatibilité avec les évolutions Hermes ;
- sécurité plus simple, car le dashboard est local par défaut.

Limites :

- dépend du dashboard Hermes ;
- l'UI doit respecter les contraintes du système de plugins ;
- certaines fonctions avancées peuvent nécessiter des routes backend plugin.

### Option B - Sidecar autonome, V2 seulement

Application web séparée, par exemple Next.js + FastAPI, qui se connecte à Hermes via API locale, CLI et éventuellement fichiers de config.

Avantages :

- séparation maximale ;
- liberté UI totale ;
- possibilité mobile/tablette plus ambitieuse ;
- peut devenir une interface indépendante.

Limites :

- plus de surface de sécurité ;
- plus de duplication ;
- plus fragile si Hermes change ;
- gestion CORS/auth plus délicate ;
- risque de réinventer le dashboard Hermes.

### Option C - Fork du dashboard Hermes, déconseillée

À éviter sauf besoin impossible à réaliser autrement.

Raison : un fork devient vite un jardin envahi par les ronces. À chaque update Hermes, il faut recoller les morceaux.

---

## 6. Architecture cible

```text
┌─────────────────────────────────────────────────────────────┐
│                    Hermes Mission Control UI                 │
│       Plugin dashboard : React/JS bundle + thème optionnel   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│        Backend plugin FastAPI : /api/plugins/mission-control │
│   Adaptateurs : profiles, config, kanban, sessions, logs     │
└──────────────┬─────────────────────┬────────────────────────┘
               │                     │
               ▼                     ▼
┌─────────────────────────┐   ┌───────────────────────────────┐
│ Hermes Dashboard API     │   │ Hermes CLI / Python internals │
│ /api/status              │   │ hermes profile ...            │
│ /api/sessions            │   │ hermes kanban ...             │
│ /api/config              │   │ hermes config ...             │
│ /api/logs                │   │ official import read paths     │
│ /api/analytics/usage     │   │ controlled write adapters      │
└─────────────────────────┘   └───────────────────────────────┘
               │                     │
               ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                         Hermes Agent                         │
│ Profiles | Gateway | Kanban DB | Sessions | Skills | Tools   │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Concepts métier

### 7.1 Agent

Dans Mission Control, un agent est un **profil Hermes enrichi d'une fiche visuelle**.

Champs principaux :

- nom affiché ;
- slug Hermes profile ;
- rôle ;
- mission ;
- description courte ;
- avatar ou icône ;
- provider ;
- modèle ;
- fallback ;
- toolsets ;
- skills ;
- workspace ;
- backend terminal ;
- niveau d'autonomie ;
- mode approval ;
- statut ;
- tâches actives ;
- coût estimé ;
- dernière activité ;
- erreurs récentes.

### 7.2 Provider

Un provider représente la stratégie LLM de l'agent :

- hériter du provider principal ;
- utiliser un provider explicite ;
- utiliser OpenRouter avec routing ;
- utiliser un endpoint custom OpenAI-compatible ;
- configurer une chaîne de fallback ;
- définir des providers auxiliaires pour vision, compression, web extraction, triage.

### 7.3 Capacité

Une capacité est une combinaison de :

- toolsets Hermes ;
- skills ;
- MCP servers ;
- terminal backend ;
- permissions ;
- workspace ;
- règles d'usage ;
- limites de sécurité.

Exemples :

- Recherche web profonde ;
- Développement backend ;
- Analyse GitHub PR ;
- Génération de rapport ;
- Gestion inbox ;
- QA exploratoire ;
- Orchestration Kanban ;
- Worker code isolé Docker ;
- Analyste lecture seule.

### 7.4 Mission

La mission correspond principalement à `SOUL.md` + description de profil + éventuels context files.

Elle doit être éditable dans l'interface avec :

- mission courte ;
- règles de comportement ;
- ce que l'agent doit faire ;
- ce que l'agent ne doit jamais faire ;
- critères de réussite ;
- format de sortie attendu ;
- escalade vers l'humain ;
- contraintes de sécurité.

---

## 8. Fonctionnalités MVP

Le MVP doit être solide, pas spectaculaire pour la galerie. Il doit montrer que la boussole fonctionne avant d'ajouter les néons.

### F1 - Vue flotte d'agents

Tableau de bord avec cartes agents :

- nom ;
- statut ;
- provider/model ;
- rôle ;
- tâches en cours ;
- sessions récentes ;
- erreurs ;
- coût/jour ou tokens/jour ;
- actions rapides.

Actions :

- ouvrir fiche agent ;
- lancer chat ciblé ;
- voir logs ;
- voir tâches Kanban ;
- démarrer/arrêter gateway si pertinent ;
- dupliquer agent ;
- exporter config.

### F2 - Création d'agent

Assistant en 5 étapes :

1. Identité : nom, slug, icône, description ;
2. Mission : rôle, objectifs, interdits, format ;
3. Provider : hériter ou choisir ;
4. Capacités : toolsets, skills, MCP, workspace ;
5. Sécurité : approval mode, terminal backend, cwd, secrets requis.

Sortie technique :

- crée un profil Hermes ;
- écrit ou met à jour `SOUL.md` ;
- configure `config.yaml` via commandes ou adaptateur ;
- ne copie pas les secrets sans action explicite ;
- génère un résumé lisible.

### F3 - Éditeur de mission

Éditeur structuré :

- mode formulaire ;
- mode markdown ;
- aperçu du `SOUL.md` final ;
- bouton “tester la mission” avec prompt court ;
- versioning local léger ;
- diff avant sauvegarde.

### F4 - Configuration provider par agent

Interface pour :

- voir provider actuel ;
- choisir modèle ;
- sélectionner “hérite du principal” ;
- configurer fallback ;
- afficher clés requises sans révéler leur valeur ;
- indiquer les variables manquantes ;
- tester un appel simple.

### F5 - Capacités et toolsets

Interface de sélection :

- toolsets ;
- skills ;
- bundles de skills ;
- MCP servers ;
- permissions terminal ;
- backend local, docker, ssh, modal, daytona, etc. selon config Hermes.

### F6 - Kanban Mission Board

Vue Kanban enrichie :

- colonnes triage, todo, ready, running, blocked, done ;
- regroupement par profil ;
- filtres par agent, tenant, projet, priorité ;
- création de tâche ;
- assignation à agent ;
- décomposition manuelle ;
- affichage des parent/child ;
- blocages et demandes humaines ;
- historique d'exécution.

### F7 - Observabilité

Vue “ce qui s'est passé” :

- sessions récentes ;
- messages ;
- tool calls ;
- logs ;
- erreurs ;
- token usage ;
- coûts estimés ;
- temps d'exécution ;
- taux de tâches bloquées ;
- agents les plus actifs.

### F8 - Export GitHub

Génération d'un dossier prêt à versionner :

```text
hermes-mission-control-config/
├── agents/
│   ├── researcher.agent.yaml
│   ├── backend-dev.agent.yaml
│   └── reviewer.agent.yaml
├── missions/
│   ├── researcher.SOUL.md
│   └── backend-dev.SOUL.md
├── skill-bundles/
├── boards/
│   └── default.board.yaml
└── README.md
```

Important : pas d'export de `.env`, d'`auth.json`, de sessions privées ou de mémoire personnelle par défaut.

---

## 9. Fonctionnalités V1 complète

### 9.1 Templates d'agents

Créer des modèles :

- Orchestrateur ;
- Chercheur ;
- Développeur backend ;
- Développeur frontend ;
- Reviewer sécurité ;
- Rédacteur ;
- Analyste data ;
- Agent low-cost ;
- Agent local/private ;
- Agent exploratoire avec approval strict.

Chaque template définit :

- mission ;
- provider recommandé ;
- toolsets ;
- skills ;
- sécurité ;
- checklist de test.

### 9.2 Comparateur d'agents

Comparer deux profils :

- provider ;
- modèle ;
- skills ;
- toolsets ;
- memory active ;
- approvals ;
- cwd ;
- backend ;
- coût moyen ;
- taux de succès.

### 9.3 Simulateur de coût

Avant de lancer une mission :

- estimation tokens ;
- provider choisi ;
- coût attendu ;
- fallback possible ;
- avertissements si modèle cher ;
- suggestion low-cost pour triage ou spécification.

### 9.4 Graphe des agents

Vue réseau :

- agents ;
- tâches ;
- dépendances ;
- handoffs ;
- sessions ;
- MCP servers ;
- skills.

L'objectif n'est pas de faire joli : il faut voir rapidement qui dépend de qui, qui bloque qui, et quel agent a produit quel artefact.

### 9.5 Inbox humaine

Regrouper toutes les demandes où Hermes attend l'utilisateur :

- approvals ;
- tâches bloquées ;
- questions de clarification ;
- erreurs de secrets ;
- conflits ;
- demande de review.

### 9.6 Agent launchpad

Bouton “lancer mission” :

- choisir objectif ;
- choisir board ;
- choisir orchestrateur ;
- choisir niveau autonomie ;
- prévisualiser la décomposition ;
- créer tâches ;
- suivre exécution.

---

## 10. Exigences d'interface

### 10.1 Page d'accueil - Cockpit

Blocs :

- État Hermes : version, gateway, dashboard, providers ;
- Agents actifs ;
- Tâches en cours ;
- Blocages urgents ;
- Coût/tokens ;
- Dernières erreurs ;
- Bouton “Créer agent” ;
- Bouton “Créer mission”.

### 10.2 Page Agents

Liste avec filtres :

- rôle ;
- provider ;
- statut ;
- workspace ;
- toolsets ;
- activité.

Actions de masse :

- exporter ;
- désactiver ;
- vérifier santé ;
- synchroniser skills ;
- comparer.

### 10.3 Fiche Agent

Onglets :

1. Résumé ;
2. Mission ;
3. Provider ;
4. Capacités ;
5. Sessions ;
6. Kanban ;
7. Logs ;
8. Sécurité ;
9. Export.

### 10.4 Page Providers

Visualiser :

- providers disponibles ;
- clés présentes ou manquantes ;
- modèles utilisés ;
- fallback ;
- routing OpenRouter ;
- endpoints custom ;
- tests de connexion.

### 10.5 Page Mission Board

Kanban + timeline + drawer de tâche.

Drawer :

- titre ;
- description ;
- assignee ;
- statut ;
- dépendances ;
- commentaires ;
- runs ;
- metadata de sortie ;
- fichiers changés ;
- vérification ;
- risque résiduel ;
- bouton unblock/retry/archive.

### 10.6 Page Observabilité

Graphiques simples :

- tokens par jour ;
- coût par provider ;
- tasks done/blocked ;
- temps moyen par agent ;
- erreurs par type ;
- tool calls par agent.

Pas de décoration vide : chaque graphique doit répondre à une décision.

---

## 11. Modèle de données Mission Control

Mission Control doit éviter de devenir une vérité parallèle. La vérité reste Hermes. La base Mission Control ne stocke que les métadonnées UI et les préférences qui n'existent pas dans Hermes.

### 11.1 AgentDescriptor

```yaml
id: researcher
hermes_profile: researcher
display_name: Researcher
icon: search
color: blue
role: research
mission_file: missions/researcher.SOUL.md
description: Reads docs, web sources and code, produces sourced syntheses.
provider:
  mode: inherit | explicit | custom
  provider: openrouter
  model: anthropic/claude-sonnet-4
  fallback_enabled: true
capabilities:
  toolsets:
    - web
    - file
    - skills
  skills:
    - research
    - plan
  mcp_servers:
    - github
workspace:
  cwd: /absolute/path/to/project
  terminal_backend: docker
safety:
  approval_mode: manual
  autonomy_level: supervised
kanban:
  can_orchestrate: false
  can_work: true
  default_priority: 2
ui:
  pinned: true
  notes: "Agent de recherche documentaire."
```

### 11.2 ProviderPolicy

```yaml
id: low_cost_research
inherits_from: main
provider: openrouter
model: google/gemini-flash-or-equivalent
routing:
  sort: price
  data_collection: deny
fallbacks:
  - provider: nous
    model: default
limits:
  max_tokens_per_task: 120000
  warn_above_cost_eur: 2.00
```

### 11.3 CapabilityBundle

```yaml
id: backend_feature_work
label: Backend feature work
skills:
  - test-driven-development
  - github-pr-workflow
  - code-review
toolsets:
  - terminal
  - file
  - web
  - skills
mcp_servers:
  - github
required_env:
  - GITHUB_TOKEN
security:
  recommended_backend: docker
  approval_mode: manual
```

---

## 12. Endpoints backend plugin proposés

Routes sous :

```text
/api/plugins/hermes-mission-control/
```

### GET /agents

Retourne tous les profils détectés + métadonnées Mission Control.

### POST /agents

Crée un profil Hermes et sa fiche.

Body :

```json
{
  "name": "researcher",
  "description": "Reads docs and writes sourced summaries.",
  "clone_from": "default",
  "clone_mode": "config_only",
  "mission": "...",
  "provider": { "mode": "inherit" },
  "capabilities": { "toolsets": ["web", "skills"] }
}
```

### GET /agents/{id}

Fiche complète.

### PATCH /agents/{id}

Met à jour mission, provider, capacités, UI metadata.

### POST /agents/{id}/healthcheck

Teste configuration, provider, workspace, skills et gateway.

### POST /agents/{id}/chat

Lance un prompt court contre ce profil via commande Hermes ou API.

### GET /providers

Liste providers disponibles, clés présentes, modèles connus, erreurs.

### POST /providers/test

Teste provider/model sans persister.

### GET /kanban/boards

Liste boards.

### GET /kanban/tasks

Liste tâches avec filtres.

### POST /kanban/tasks

Crée tâche assignée à un agent.

### POST /kanban/tasks/{id}/unblock

Débloque tâche.

### POST /export/github

Génère un bundle versionnable sans secrets.

---

## 13. Commandes Hermes utilisées par l'adaptateur

À confirmer dans l'environnement réel, mais le cahier des charges prévoit d'utiliser les commandes documentées :

```bash
hermes profile list
hermes profile show <profile>
hermes profile create <name> --description "..."
hermes profile create <name> --clone --clone-from <source>
hermes -p <profile> config set model.default <model>
hermes -p <profile> config set terminal.cwd <path>
hermes -p <profile> skills list
hermes -p <profile> tools
hermes kanban init
hermes kanban create "Task" --assignee <profile> --body "..."
hermes kanban list
hermes dashboard --no-open
```

Écriture directe dans fichiers seulement via adaptateur atomique :

- sauvegarde avant écriture ;
- validation YAML ;
- diff ;
- rollback si erreur ;
- jamais de secrets affichés.

---

## 14. Sécurité

### 14.1 Secrets

Règles :

- Mission Control ne stocke jamais les clés API dans sa base ;
- affichage uniquement `set/unset` ou valeur redacted ;
- écriture de secrets via l'API Hermes existante ou `.env` contrôlé ;
- export GitHub exclut `.env`, `auth.json`, sessions, memory, logs sensibles.

### 14.2 Exposition réseau

Par défaut : localhost uniquement.

Accès distant recommandé :

- SSH tunnel ;
- Tailscale ;
- VPN privé.

À éviter :

- dashboard exposé en `0.0.0.0` sans auth forte ;
- plugin non audité accessible depuis un réseau public.

### 14.3 Approvals

Chaque agent doit afficher :

- approval mode ;
- terminal backend ;
- cwd ;
- toolsets dangereux ;
- accès aux secrets ;
- dernier usage de commandes sensibles.

Actions risquées nécessitent confirmation :

- suppression profil ;
- changement provider global ;
- passage approval off ;
- activation terminal local large ;
- export de données ;
- modification massive de skills.

### 14.4 Audit

Tout changement doit produire un événement :

```json
{
  "timestamp": "2026-05-25T12:00:00+02:00",
  "actor": "local-user",
  "action": "agent.update_provider",
  "agent": "researcher",
  "before": { "provider": "inherit" },
  "after": { "provider": "openrouter" },
  "result": "success"
}
```

---

## 15. Non-fonctionnel

### Performance

- chargement dashboard < 2 secondes hors première installation ;
- rafraîchissement statuts toutes les 5 à 10 secondes ;
- gros logs paginés ;
- sessions chargées à la demande ;
- pas de scan complet lourd à chaque page.

### Fiabilité

- aucun crash UI ne doit arrêter Hermes ;
- opérations d'écriture idempotentes ;
- backup avant changement critique ;
- rollback visible ;
- erreurs lisibles par humain.

### Compatibilité

- Linux, macOS, WSL2 en priorité ;
- Windows natif en lecture/monitoring si Hermes dashboard le supporte ;
- mobile responsive ;
- thème sombre et clair ;
- mode compact.

### Maintenabilité

- TypeScript côté UI si build externe ;
- Python FastAPI côté backend plugin ;
- tests unitaires pour adaptateurs ;
- contrats JSON documentés ;
- pas de dépendances lourdes inutiles ;
- repo installable par clone GitHub.

---

## 16. Repo GitHub cible

```text
hermes-mission-control/
├── README.md
├── LICENSE
├── docs/
│   ├── architecture.md
│   ├── install.md
│   ├── security.md
│   ├── api.md
│   └── agent-descriptor.schema.md
├── dashboard/
│   ├── manifest.json
│   ├── plugin_api.py
│   ├── dist/
│   │   └── index.js
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       ├── components/
│       ├── api/
│       └── types/
├── schemas/
│   ├── agent-descriptor.schema.json
│   ├── provider-policy.schema.json
│   └── capability-bundle.schema.json
├── examples/
│   ├── agents/
│   ├── missions/
│   └── boards/
├── scripts/
│   ├── install.sh
│   ├── uninstall.sh
│   └── export-config.py
├── tests/
│   ├── test_profiles_adapter.py
│   ├── test_config_adapter.py
│   ├── test_export.py
│   └── test_security_redaction.py
└── pyproject.toml
```

### README attendu

Le README doit expliquer :

- ce que fait le projet ;
- ce qu'il ne fait pas ;
- prérequis Hermes ;
- installation ;
- première création d'agent ;
- sécurité ;
- limitations ;
- roadmap.

---

## 17. Critères d'acceptation MVP

Le MVP est accepté si :

1. l'installation ne modifie pas le cœur Hermes ;
2. le plugin apparaît dans le dashboard ;
3. la page agents liste au moins le profil default ;
4. la création d'un agent crée un profil Hermes réel ;
5. la mission est écrite dans le bon `SOUL.md` ;
6. le provider peut être hérité ou configuré par agent ;
7. les toolsets et skills sont visibles ;
8. une tâche Kanban peut être créée et assignée à un profil ;
9. le statut de la tâche remonte dans l'UI ;
10. les sessions récentes et logs sont consultables ;
11. les secrets sont redacted ;
12. l'export GitHub ne contient aucun secret ;
13. suppression ou modification risquée demande confirmation ;
14. un test automatisé valide la redaction des secrets ;
15. un rollback de config simple existe.

---

## 18. Roadmap proposée

### Phase 0 - Validation locale

- vérifier version Hermes ;
- vérifier dashboard disponible ;
- vérifier profiles ;
- vérifier Kanban ;
- vérifier endpoints REST ;
- décider plugin ou sidecar.

### Phase 1 - Plugin squelette

- manifest ;
- tab Mission Control ;
- page statut ;
- appel `/api/status` ;
- appel `/api/sessions` ;
- design initial.

### Phase 2 - Agents registry

- adapter profils ;
- liste agents ;
- fiche agent ;
- lecture config ;
- lecture `SOUL.md` ;
- healthcheck.

### Phase 3 - Création et édition

- wizard de création ;
- création profil ;
- clone config optionnel ;
- édition mission ;
- modification provider ;
- diff + rollback.

### Phase 4 - Kanban

- liste boards/tâches ;
- assignation agent ;
- création tâche ;
- drawer tâche ;
- blocked/unblock ;
- timeline.

### Phase 5 - Observabilité

- usage analytics ;
- logs ;
- coût ;
- erreurs ;
- activité par agent.

### Phase 6 - Export GitHub

- agent descriptors ;
- missions ;
- bundles ;
- README auto ;
- validation anti-secrets ;
- archive zip ou dossier.

---

## 19. Points de vigilance

### 19.1 Profils ne sont pas des sandboxes

Un profil Hermes isole la configuration et la mémoire, mais pas forcément le filesystem. Si un agent doit être limité, il faut configurer `terminal.cwd` et idéalement un backend isolé comme Docker ou équivalent.

### 19.2 Subagents et agents persistants ne jouent pas le même rôle

- `delegate_task` : utile pour sous-tâche courte, isolée, retour final seulement ;
- Kanban profiles : mieux pour agents nommés, persistants, observables et relançables.

L'interface doit donc privilégier Kanban pour ta vision “agents que je vois”. Les subagents restent un mécanisme interne.

### 19.3 Le piège du beau dashboard muet

Une interface jolie qui ne permet pas de comprendre pourquoi un agent bloque ne sert à rien. Le cœur du produit est : statut, trace, raison, prochain geste.

### 19.4 Le piège de la base parallèle

Ne pas inventer une “vérité” séparée de Hermes. Mission Control doit être un miroir augmenté, pas un deuxième cerveau qui contredit le premier.

---

## 20. Prompt de lancement pour un agent de code

À utiliser dans Hermes ou un autre agent de développement :

```text
Tu vas créer le projet hermes-mission-control.
Objectif : construire un plugin dashboard Hermes local-first permettant de visualiser, créer et configurer des profils Hermes comme agents nommés.
Contrainte absolue : ne pas modifier le cœur hermes-agent. Utiliser les mécanismes documentés : dashboard plugin, backend FastAPI plugin, CLI Hermes et endpoints REST existants.

Livrables MVP :
1. README.md clair.
2. dashboard/manifest.json.
3. dashboard/plugin_api.py avec routes /agents, /agents/{id}, /providers, /health.
4. UI simple avec pages Cockpit, Agents, Agent Detail.
5. Adapter Python pour lister les profils Hermes.
6. Adapter pour lire config.yaml et SOUL.md d'un profil sans afficher de secrets.
7. Wizard minimal de création d'agent qui appelle hermes profile create.
8. Tests de redaction secrets.
9. Documentation sécurité.

Ne pas implémenter Kanban avant que la liste et création d'agents soient stables.
Chaque opération d'écriture doit avoir dry-run, diff, backup et rollback simple.
```

---

## 21. Sources consultées

- Hermes Agent GitHub : https://github.com/NousResearch/hermes-agent
- Hermes Agent docs : https://hermes-agent.nousresearch.com/docs/
- Hermes profiles : https://hermes-agent.nousresearch.com/docs/user-guide/profiles
- Hermes dashboard : https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard
- Extending Hermes dashboard : https://hermes-agent.nousresearch.com/docs/user-guide/features/extending-the-dashboard
- Hermes Kanban : https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban
- Hermes Kanban worker lanes : https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban-worker-lanes
- Hermes API server : https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server
- Hermes providers : https://hermes-agent.nousresearch.com/docs/integrations/providers
- Hermes fallback providers : https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers
- Hermes skills : https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- GitHub Agent HQ : https://github.blog/news-insights/company-news/welcome-home-agents/
- GitHub Universe recap : https://github.com/events/universe/recap
- AutoGen Studio : https://microsoft.github.io/autogen/dev/user-guide/autogenstudio-user-guide/index.html
- LangSmith Studio : https://docs.langchain.com/oss/python/langgraph/studio
- CrewAI observability : https://docs.crewai.com/en/observability/overview

---

## 22. Décision finale

Construire **Hermes Mission Control** comme plugin dashboard local, avec backend FastAPI plugin, en s'appuyant sur les profils Hermes comme agents persistants et sur Kanban comme colonne vertébrale de coordination. La V2 pourra devenir une app sidecar plus autonome, mais seulement après avoir prouvé le MVP plugin.
