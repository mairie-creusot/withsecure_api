# API FastAPI WithSecure Elements 🚀

API REST complète et moderne pour interagir avec l'API WithSecure Elements, construite avec FastAPI.

## ✨ Fonctionnalités

- ⚡ **API REST asynchrone** avec FastAPI pour des performances optimales
- 📚 **Documentation automatique** (Swagger UI et ReDoc)
- 🔐 **Authentification OAuth 2.0** gérée automatiquement
- 📊 **Endpoints de statistiques** et rapports détaillés
- 🔄 **Gestion automatique de la pagination** WithSecure
- 🎯 **Validation des données** avec Pydantic
- 🌐 **CORS configuré** pour les applications web
- ⚠️ **Gestion d'erreurs robuste**

## 🏗️ Architecture

```
.
├── main.py                          # Application FastAPI principale
├── async_withsecure_client.py      # Client asynchrone WithSecure
├── models.py                        # Modèles Pydantic
├── config.json                      # Configuration (à créer)
├── requirements_fastapi.txt         # Dépendances Python
└── README_FASTAPI.md               # Cette documentation
```

## 🚀 Installation

### 1. Installer les dépendances

```bash
pip install -r requirements_fastapi.txt
```

### 2. Configuration

Créez un fichier `config.json` avec vos identifiants WithSecure :

```json
{
  "client_id": "VOTRE_CLIENT_ID",
  "client_secret": "VOTRE_CLIENT_SECRET",
  "api_base_url": "https://api.connect.withsecure.com",
  "scopes": "connect.api.read connect.api.write"
}
```

### 3. Lancer l'API

```bash
python main.py
```

Ou avec uvicorn directement :

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur : **http://localhost:8000**

## 📖 Documentation Interactive

Une fois l'API lancée, accédez à :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

Ces interfaces vous permettent de :
- ✅ Tester tous les endpoints directement
- ✅ Voir les schémas de requête/réponse
- ✅ Comprendre les paramètres requis

## 🛣️ Endpoints Disponibles

### 🏥 Santé et Monitoring

#### `GET /health`
Vérifie la santé de l'API et la connexion à WithSecure

```bash
curl http://localhost:8000/health
```

**Réponse :**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T14:30:00Z",
  "withsecure_api_connected": true
}
```

---

### 💻 Appareils (Devices)

#### `GET /devices`
Liste les appareils avec pagination

**Paramètres :**
- `anchor` (optionnel) : Point de pagination
- `limit` (optionnel, défaut=100) : Nombre de résultats (1-200)

```bash
curl "http://localhost:8000/devices?limit=50"
```

#### `GET /devices/all`
Récupère TOUS les appareils (toutes les pages)

```bash
curl http://localhost:8000/devices/all
```

⚠️ **Attention** : Peut être lent avec beaucoup d'appareils

#### `GET /devices/{device_id}`
Récupère un appareil spécifique

```bash
curl http://localhost:8000/devices/12345-abcde-67890
```

#### `GET /devices/platform/{platform}`
Filtre les appareils par plateforme

Plateformes supportées : `Windows`, `macOS`, `Linux`

```bash
curl http://localhost:8000/devices/platform/Windows
```

---

### 🔄 Mises à jour (Updates)

#### `GET /updates`
Liste les informations de mise à jour avec pagination

```bash
curl "http://localhost:8000/updates?limit=100"
```

#### `GET /updates/{device_id}`
Récupère les mises à jour d'un appareil spécifique

```bash
curl http://localhost:8000/updates/12345-abcde-67890
```

**Réponse :**
```json
{
  "deviceId": "12345-abcde-67890",
  "status": "pending",
  "pending_count": 2,
  "pendingSoftwareUpdates": [
    {
      "title": "WithSecure Client Security 24.1.123",
      "version": "24.1.123"
    }
  ]
}
```

#### `GET /updates/pending/all`
Liste tous les appareils avec mises à jour en attente

```bash
curl http://localhost:8000/updates/pending/all
```

**Réponse :**
```json
[
  {
    "device_id": "12345-abcde",
    "device_name": "PC-BUREAU-01",
    "platform": "Windows",
    "pending_updates_count": 2,
    "pending_updates": [
      "WithSecure Client Security 24.1.123",
      "WithSecure Hydra Update 2024-01-15_01"
    ]
  }
]
```

---

### 📊 Statistiques et Rapports

#### `GET /statistics`
Statistiques complètes sur les appareils et mises à jour

```bash
curl http://localhost:8000/statistics
```

**Réponse :**
```json
{
  "total_devices": 50,
  "devices_online": 45,
  "devices_offline": 5,
  "devices_with_updates": 48,
  "devices_up_to_date": 35,
  "devices_with_pending_updates": 13,
  "devices_by_platform": [
    {
      "platform": "Windows",
      "count": 30,
      "percentage": 60.0
    },
    {
      "platform": "macOS",
      "count": 15,
      "percentage": 30.0
    }
  ],
  "devices_by_status": [
    {
      "status": "up_to_date",
      "count": 35,
      "percentage": 70.0
    },
    {
      "status": "pending",
      "count": 13,
      "percentage": 26.0
    }
  ],
  "devices_with_pending_details": [...],
  "generated_at": "2026-01-27T14:30:00Z"
}
```

#### `GET /reports/updates`
Génère un rapport complet des mises à jour

```bash
curl http://localhost:8000/reports/updates
```

---

### 💾 Bases de données

#### `GET /databases/versions`
Récupère les versions des bases de données

**Paramètres :**
- `database_ids` (requis) : Liste des IDs de bases de données

```bash
curl "http://localhost:8000/databases/versions?database_ids=hydra-win64&database_ids=capricorn-win64"
```

**Exemple de bases de données communes :**
- `hydra-win64`
- `capricorn-win64`
- `sensor-win64`
- `virgo-win64`
- `deepguard-db`

---

### 🔒 Événements de sécurité

#### `GET /security-events`
Récupère les événements de sécurité

```bash
curl "http://localhost:8000/security-events?limit=50"
```

---

## 🐍 Utilisation avec Python

### Client Python simple

```python
import httpx

BASE_URL = "http://localhost:8000"

# Récupérer les statistiques
response = httpx.get(f"{BASE_URL}/statistics")
stats = response.json()

print(f"Total d'appareils: {stats['total_devices']}")
print(f"Mises à jour en attente: {stats['devices_with_pending_updates']}")
```

### Client asynchrone

```python
import httpx
import asyncio

async def get_devices():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/devices/all")
        return response.json()

devices = asyncio.run(get_devices())
print(f"Nombre d'appareils: {len(devices)}")
```

---

## 🌐 Utilisation avec JavaScript

### Fetch API

```javascript
// Récupérer les appareils avec mises à jour en attente
fetch('http://localhost:8000/updates/pending/all')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.length} appareils ont des mises à jour en attente`);
    data.forEach(device => {
      console.log(`${device.device_name}: ${device.pending_updates_count} mises à jour`);
    });
  });
```

### Axios

```javascript
const axios = require('axios');

async function getStatistics() {
  const response = await axios.get('http://localhost:8000/statistics');
  const stats = response.data;
  
  console.log(`Total: ${stats.total_devices} appareils`);
  console.log(`En ligne: ${stats.devices_online}`);
  console.log(`Mises à jour en attente: ${stats.devices_with_pending_updates}`);
}

getStatistics();
```

---

## 🔧 Configuration Avancée

### Variables d'environnement

Vous pouvez aussi utiliser des variables d'environnement :

```python
import os

config = {
    "client_id": os.getenv("WITHSECURE_CLIENT_ID"),
    "client_secret": os.getenv("WITHSECURE_CLIENT_SECRET"),
    "api_base_url": os.getenv("WITHSECURE_API_URL", "https://api.connect.withsecure.com"),
    "scopes": os.getenv("WITHSECURE_SCOPES", "connect.api.read connect.api.write")
}
```

### Déploiement en production

#### Avec Gunicorn (recommandé)

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Avec Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_fastapi.txt .
RUN pip install --no-cache-dir -r requirements_fastapi.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t withsecure-api .
docker run -p 8000:8000 -v $(pwd)/config.json:/app/config.json withsecure-api
```

---

## 📊 Exemples d'Intégration

### Dashboard Web Simple

```html
<!DOCTYPE html>
<html>
<head>
    <title>WithSecure Dashboard</title>
</head>
<body>
    <h1>Statistiques WithSecure</h1>
    <div id="stats"></div>
    
    <script>
        fetch('http://localhost:8000/statistics')
            .then(r => r.json())
            .then(data => {
                document.getElementById('stats').innerHTML = `
                    <p>Total d'appareils: ${data.total_devices}</p>
                    <p>En ligne: ${data.devices_online}</p>
                    <p>Mises à jour en attente: ${data.devices_with_pending_updates}</p>
                `;
            });
    </script>
</body>
</html>
```

### Script de monitoring avec alertes

```python
import httpx
import time

def check_pending_updates():
    response = httpx.get("http://localhost:8000/updates/pending/all")
    pending = response.json()
    
    if len(pending) > 10:
        print(f"⚠️ ALERTE: {len(pending)} appareils ont des mises à jour en attente!")
        for device in pending[:5]:  # Afficher les 5 premiers
            print(f"  - {device['device_name']}: {device['pending_updates_count']} mises à jour")

# Vérifier toutes les heures
while True:
    check_pending_updates()
    time.sleep(3600)
```

---

## 🔐 Sécurité

### En production

1. **Restreindre CORS** :
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://votre-domaine.com"],  # Pas "*"
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

2. **Ajouter de l'authentification** :
   ```python
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   @app.get("/devices")
   async def list_devices(credentials: HTTPAuthorizationCredentials = Depends(security)):
       # Vérifier le token
       ...
   ```

3. **Rate limiting** :
   ```bash
   pip install slowapi
   ```

4. **HTTPS uniquement** en production

---

## 🐛 Dépannage

### L'API ne démarre pas

**Erreur** : `Configuration file 'config.json' not found`

**Solution** : Créez le fichier `config.json` avec vos identifiants

---

### Erreur d'authentification

**Erreur** : `Failed to authenticate with WithSecure API`

**Solution** : Vérifiez vos identifiants dans `config.json`

---

### Timeouts ou lenteur

**Problème** : Les requêtes prennent trop de temps

**Solutions** :
- Utilisez les endpoints avec pagination plutôt que `/all`
- Implémentez un cache (Redis, Memcached)
- Augmentez le nombre de workers

---

## 📈 Monitoring et Logs

### Logs structurés

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Métriques Prometheus

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🤝 Contribution

Pour améliorer cette API :

1. Fork le projet
2. Créez une branche : `git checkout -b feature/ma-fonctionnalite`
3. Commitez : `git commit -m "Ajout de ma fonctionnalité"`
4. Push : `git push origin feature/ma-fonctionnalite`
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est fourni "tel quel" à des fins d'intégration avec l'API WithSecure Elements.

---

## 🔗 Liens Utiles

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation WithSecure API](https://connect.withsecure.com/api-reference)
- [Swagger/OpenAPI](https://swagger.io/)
- [HTTPX (client async)](https://www.python-httpx.org/)

---

## ✉️ Support

Pour toute question :
- Consultez la documentation interactive : `/docs`
- Vérifiez les logs de l'application
- Contactez le support WithSecure pour les problèmes liés à leur API
