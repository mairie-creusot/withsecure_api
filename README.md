# Client API WithSecure Elements

Client Python pour interagir avec l'API WithSecure Elements, permettant l'authentification et la surveillance des mises à jour des appareils.

## 📋 Fonctionnalités

- ✅ **Authentification OAuth 2.0** avec gestion automatique du renouvellement des tokens
- ✅ **Récupération de la liste des appareils** avec pagination automatique
- ✅ **Surveillance des mises à jour** logicielles
- ✅ **Rapports détaillés** sur l'état des mises à jour
- ✅ **Export des rapports** en JSON

## 🚀 Installation

### Prérequis

- Python 3.7 ou supérieur
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Copiez le fichier de configuration exemple :

```bash
cp config.example.json config.json
```

2. Éditez `config.json` avec vos identifiants API WithSecure :

```json
{
  "client_id": "VOTRE_CLIENT_ID",
  "client_secret": "VOTRE_CLIENT_SECRET",
  "api_base_url": "https://api.connect.withsecure.com",
  "scopes": "connect.api.read connect.api.write"
}
```

### Obtenir vos identifiants API

1. Connectez-vous à votre compte WithSecure Elements
2. Allez dans **Paramètres** → **API Keys**
3. Créez une nouvelle clé API avec les scopes appropriés
4. Copiez le `client_id` et le `client_secret`

## 📖 Utilisation

### Script de surveillance des mises à jour

Le moyen le plus simple de surveiller vos appareils :

```bash
python monitor_updates.py
```

Ce script va :
1. S'authentifier auprès de l'API
2. Récupérer tous les appareils
3. Récupérer les informations de mise à jour
4. Afficher un rapport détaillé
5. Sauvegarder le rapport dans un fichier JSON

### Exemple de sortie

```
================================================================================
 RAPPORT DE SURVEILLANCE DES MISES À JOUR WITHSECURE
================================================================================

Date du rapport: 2026-01-27 14:30:00

--------------------------------------------------------------------------------
 STATISTIQUES GÉNÉRALES
--------------------------------------------------------------------------------
Nombre total d'appareils: 50
Appareils avec informations de mise à jour: 48
Appareils à jour: 35
Appareils avec mises à jour en attente: 13

--------------------------------------------------------------------------------
 RÉPARTITION PAR PLATEFORME
--------------------------------------------------------------------------------
  Windows: 30 (60.0%)
  macOS: 15 (30.0%)
  Linux: 5 (10.0%)

--------------------------------------------------------------------------------
 RÉPARTITION PAR STATUT
--------------------------------------------------------------------------------
  À jour: 35 (70.0%)
  Mises à jour en attente: 13 (26.0%)
  Pas d'information: 2 (4.0%)

--------------------------------------------------------------------------------
 APPAREILS AVEC MISES À JOUR EN ATTENTE
--------------------------------------------------------------------------------

📱 PC-BUREAU-01
   ID: 12345-abcde-67890
   Plateforme: Windows
   Nombre de mises à jour: 2
   Mises à jour:
     • WithSecure Client Security 24.1.123
     • WithSecure Hydra Update 2024-01-15_01
```

### Utilisation du client Python dans vos scripts

```python
from withsecure_client import WithSecureClient, load_config

# Charger la configuration
config = load_config("config.json")

# Initialiser le client
client = WithSecureClient(
    client_id=config["client_id"],
    client_secret=config["client_secret"]
)

# Authentification
client.authenticate()

# Récupérer tous les appareils
devices = client.get_all_devices()

# Récupérer les mises à jour
updates = client.get_all_software_updates()

# Récupérer les versions des bases de données
db_versions = client.get_latest_database_versions([
    "hydra-win64",
    "sensor-win64",
    "capricorn-win64"
])
```

## 📁 Structure des fichiers

```
.
├── withsecure_client.py    # Client API principal
├── monitor_updates.py       # Script de surveillance
├── config.example.json      # Template de configuration
├── config.json             # Votre configuration (à créer)
├── requirements.txt        # Dépendances Python
└── README.md              # Cette documentation
```

## 🔧 API Client - Méthodes principales

### `WithSecureClient`

#### `authenticate()`
Authentifie le client et récupère un token OAuth 2.0.

#### `get_devices(anchor=None, limit=100)`
Récupère une page d'appareils.
- `anchor`: Point de pagination (optionnel)
- `limit`: Nombre d'appareils par page (1-200)

#### `get_all_devices()`
Récupère tous les appareils en gérant automatiquement la pagination.

#### `get_software_updates(anchor=None, limit=100)`
Récupère une page d'informations de mise à jour.

#### `get_all_software_updates()`
Récupère toutes les informations de mise à jour.

#### `get_latest_database_versions(database_ids)`
Récupère les dernières versions des bases de données spécifiées.

## 📊 Format des rapports JSON

Les rapports sont sauvegardés au format JSON avec la structure suivante :

```json
{
  "timestamp": "2026-01-27T14:30:00",
  "statistics": {
    "total_devices": 50,
    "devices_with_updates": 48,
    "devices_up_to_date": 35,
    "devices_with_pending_updates": 13,
    "devices_by_platform": {
      "Windows": 30,
      "macOS": 15,
      "Linux": 5
    },
    "update_details": [
      {
        "device_id": "12345-abcde",
        "device_name": "PC-BUREAU-01",
        "platform": "Windows",
        "status": "Mises à jour en attente",
        "pending_updates": 2,
        "pending_update_names": [...]
      }
    ]
  }
}
```

## 🔐 Sécurité

- ⚠️ **Ne commitez JAMAIS** le fichier `config.json` dans un dépôt Git
- Le fichier `.gitignore` est configuré pour ignorer `config.json`
- Les tokens sont automatiquement renouvelés avant expiration
- Les identifiants sont transmis via HTTPS uniquement

## 🐛 Dépannage

### Erreur d'authentification

```
✗ Erreur d'authentification: 401 Client Error
```

**Solution** : Vérifiez vos `client_id` et `client_secret` dans `config.json`.

### Erreur de scope

```
error: invalid_scope
```

**Solution** : Assurez-vous que les scopes dans `config.json` correspondent à ceux configurés dans votre clé API.

### Pas d'appareils trouvés

Si aucun appareil n'est retourné, vérifiez que :
- Votre compte a bien accès aux appareils
- Les scopes incluent `connect.api.read`

## 📝 Exemples avancés

### Surveillance continue

```python
import time
from withsecure_client import WithSecureClient, load_config
from monitor_updates import monitor_updates

config = load_config("config.json")
client = WithSecureClient(config["client_id"], config["client_secret"])

# Surveiller toutes les heures
while True:
    monitor_updates(client)
    time.sleep(3600)  # Attendre 1 heure
```

### Filtrer les appareils par plateforme

```python
devices = client.get_all_devices()

# Filtrer uniquement les appareils Windows
windows_devices = [d for d in devices if d.get("platform") == "Windows"]

print(f"Nombre d'appareils Windows: {len(windows_devices)}")
```

### Alertes pour mises à jour critiques

```python
updates = client.get_all_software_updates()

for update in updates:
    pending = update.get("pendingSoftwareUpdates", [])
    if len(pending) > 5:  # Plus de 5 mises à jour en attente
        device_id = update.get("deviceId")
        print(f"⚠️ ALERTE: {device_id} a {len(pending)} mises à jour en attente!")
```

## 🤝 Contribution

Pour contribuer à ce projet :
1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est fourni "tel quel" à des fins éducatives et d'intégration avec l'API WithSecure Elements.

## 🔗 Liens utiles

- [Documentation API WithSecure Elements](https://connect.withsecure.com/api-reference)
- [Portail WithSecure Elements](https://connect.withsecure.com)
- [Support WithSecure](https://www.withsecure.com/support)

## ✉️ Support

Pour toute question ou problème, consultez la documentation officielle de WithSecure ou contactez leur support technique.
