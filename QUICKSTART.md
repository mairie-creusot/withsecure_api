# 🚀 Guide de Démarrage Rapide - API FastAPI WithSecure

## Installation en 3 étapes

### 1️⃣ Installation des dépendances

```bash
pip install -r requirements_fastapi.txt
```

### 2️⃣ Configuration

Créez `config.json` avec vos identifiants :

```json
{
  "client_id": "VOTRE_CLIENT_ID",
  "client_secret": "VOTRE_CLIENT_SECRET",
  "api_base_url": "https://api.connect.withsecure.com",
  "scopes": "connect.api.read connect.api.write"
}
```

### 3️⃣ Lancement

```bash
python main.py
```

✅ L'API est maintenant accessible sur : **http://localhost:8000**

---

## 📚 Documentation Interactive

Une fois lancée, visitez :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 🧪 Test Rapide

Dans un nouveau terminal :

```bash
# Vérifier la santé de l'API
curl http://localhost:8000/health

# Récupérer les statistiques
curl http://localhost:8000/statistics

# Lister les appareils avec mises à jour en attente
curl http://localhost:8000/updates/pending/all
```

Ou lancez le script de test :

```bash
python test_api.py
```

---

## 📊 Endpoints Principaux

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Santé de l'API |
| `GET /devices` | Liste des appareils |
| `GET /devices/all` | Tous les appareils |
| `GET /updates/pending/all` | Mises à jour en attente |
| `GET /statistics` | Statistiques complètes |
| `GET /reports/updates` | Rapport détaillé |

---

## 🐳 Lancement avec Docker

```bash
# Build
docker build -t withsecure-api .

# Run
docker run -p 8000:8000 -v $(pwd)/config.json:/app/config.json withsecure-api
```

Ou avec Docker Compose :

```bash
docker-compose up -d
```

---

## 💡 Exemples d'Utilisation

### Python

```python
import httpx

# Récupérer les statistiques
response = httpx.get("http://localhost:8000/statistics")
stats = response.json()
print(f"Total: {stats['total_devices']} appareils")
```

### JavaScript

```javascript
fetch('http://localhost:8000/updates/pending/all')
  .then(r => r.json())
  .then(data => console.log(`${data.length} mises à jour en attente`));
```

### cURL

```bash
# Récupérer un appareil spécifique
curl http://localhost:8000/devices/DEVICE_ID

# Filtrer par plateforme
curl http://localhost:8000/devices/platform/Windows
```

---

## 🆘 Besoin d'Aide ?

- Consultez `README_FASTAPI.md` pour la documentation complète
- Visitez `/docs` pour tester les endpoints interactivement
- Vérifiez que `config.json` contient vos bons identifiants

---

## 🎯 Prochaines Étapes

1. Testez les endpoints dans Swagger UI (`/docs`)
2. Intégrez l'API dans votre application
3. Configurez les alertes pour les mises à jour
4. Déployez en production avec Docker

**Bonne utilisation ! 🚀**
