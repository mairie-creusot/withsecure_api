"""
API FastAPI pour WithSecure Elements
"""

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime
import json
import os

from async_withsecure_client import AsyncWithSecureClient
from models import (
    HealthResponse, DeviceListResponse, TokenResponse, UpdatesListResponse, 
    StatisticsResponse, UpdateReport, DatabaseVersionsResponse,
    ErrorResponse, SecurityEventsResponse, Device, DeviceWithPendingUpdates,
    PlatformStats, UpdateStatusStats, UpdateStatus
)


# ============================================================================
# Configuration
# ============================================================================

def load_config(config_path: str = "config.json") -> dict:
    """Charge la configuration depuis un fichier JSON"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' not found")
    
    with open(config_path, 'r') as f:
        return json.load(f)


# Charger la configuration
config = load_config("config.json")

# Client WithSecure global
withsecure_client: Optional[AsyncWithSecureClient] = None


# ============================================================================
# Lifecycle et dépendances
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global withsecure_client
    
    # Startup: Initialiser le client WithSecure
    withsecure_client = AsyncWithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        api_base_url=config.get("api_base_url", "https://api.connect.withsecure.com"),
        scopes=config.get("scopes", "connect.api.read connect.api.write")
    )
    
    # Authentification initiale
    try:
        await withsecure_client.authenticate()
        print("✓ WithSecure API client initialized and authenticated")
    except Exception as e:
        print(f"✗ Failed to authenticate with WithSecure API: {e}")
    
    yield
    
    # Shutdown: Nettoyage si nécessaire
    print("Shutting down...")


def get_client() -> AsyncWithSecureClient:
    """Dépendance pour obtenir le client WithSecure"""
    if withsecure_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WithSecure client not initialized"
        )
    return withsecure_client


# ============================================================================
# Application FastAPI
# ============================================================================

app = FastAPI(
    title="WithSecure Elements API",
    description="API REST pour gérer et surveiller les appareils WithSecure",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'exceptions HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire d'exceptions générales"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "status_code": 500
        }
    )


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Endpoint racine"""
    return {
        "message": "WithSecure Elements API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(client: AsyncWithSecureClient = Depends(get_client)):
    """Vérifie la santé de l'API et la connexion à WithSecure"""
    try:
        # Tester la connexion en récupérant les appareils (limité à 1)
        await client.get_devices(limit=1)
        withsecure_connected = True
    except Exception:
        withsecure_connected = False
    
    return HealthResponse(
        status="healthy" if withsecure_connected else "degraded",
        timestamp=datetime.now(),
        withsecure_api_connected=withsecure_connected
    )

#=============================================================================
# Endpoints API Key
#=============================================================================
@app.post("/api-keys/v1/create", tags=["API Keys"])
async def create_api-key(
    """Crée un token pour les utilisateurs de l'API"""
)


#=============================================================================
# Endpoints Authentication
#=============================================================================

@app.post("/as/token.oauth2", response_model=TokenResponse, tags=["Authentication"])
async def authenticate(

)


# ============================================================================
# Endpoints Devices
# ============================================================================

@app.get("/devices", response_model=DeviceListResponse, tags=["Devices"])
async def list_devices(
    anchor: Optional[str] = Query(None, description="Point de pagination"),
    limit: int = Query(100, ge=1, le=200, description="Nombre de résultats"),
    client: AsyncWithSecureClient = Depends(get_client)
):
    """
    Récupère la liste des appareils avec pagination
    """
    try:
        response = await client.get_devices(anchor=anchor, limit=limit)
        return DeviceListResponse(
            items=response.get("items", []),
            nextAnchor=response.get("nextAnchor"),
            total=len(response.get("items", []))
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch devices: {str(e)}"
        )


@app.get("/devices/all", response_model=List[Device], tags=["Devices"])
async def list_all_devices(client: AsyncWithSecureClient = Depends(get_client)):
    """
    Récupère tous les appareils (toutes les pages)
    ⚠️ Peut être lent si vous avez beaucoup d'appareils
    """
    try:
        devices = await client.get_all_devices()
        return devices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch all devices: {str(e)}"
        )


@app.get("/devices/{device_id}", response_model=Device, tags=["Devices"])
async def get_device(
    device_id: str,
    client: AsyncWithSecureClient = Depends(get_client)
):
    """
    Récupère les informations d'un appareil spécifique
    """
    try:
        device = await client.get_device_by_id(device_id)
        return device
    except Exception as e:
        if "404" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch device: {str(e)}"
        )


@app.get("/devices/platform/{platform}", response_model=List[Device], tags=["Devices"])
async def list_devices_by_platform(
    platform: str,
    client: AsyncWithSecureClient = Depends(get_client)
):
    """
    Filtre les appareils par plateforme (Windows, macOS, Linux)
    """
    try:
        all_devices = await client.get_all_devices()
        filtered = [d for d in all_devices if d.get("platform", "").lower() == platform.lower()]
        return filtered
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to filter devices: {str(e)}"
        )


# ============================================================================
# Endpoints Software Updates
# ============================================================================

@app.get("/updates", response_model=UpdatesListResponse, tags=["Updates"])
async def list_updates(
    anchor: Optional[str] = Query(None, description="Point de pagination"),
    limit: int = Query(100, ge=1, le=200, description="Nombre de résultats"),
    client: AsyncWithSecureClient = Depends(get_client)
):
    """
    Récupère la liste des informations de mise à jour avec pagination
    """
    try:
        response = await client.get_software_updates(anchor=anchor, limit=limit)
        items = response.get("items", [])
        
        # Enrichir avec le statut
        enriched_items = []
        for item in items:
            pending = item.get("pendingSoftwareUpdates", [])
            enriched_items.append({
                **item,
                "status": UpdateStatus.PENDING if pending else UpdateStatus.UP_TO_DATE
            })
        
        return UpdatesListResponse(
            items=enriched_items,
            nextAnchor=response.get("nextAnchor"),
            total=len(items)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch updates: {str(e)}"
        )


@app.get("/updates/{device_id}", tags=["Updates"])
async def get_device_updates(
    device_id: str,
    client: AsyncWithSecureClient = Depends(get_client)
):
    """
    Récupère les mises à jour pour un appareil spécifique
    """
    try:
        update_info = await client.get_software_update_by_device(device_id)
        pending = update_info.get("pendingSoftwareUpdates", [])
        
        return {
            **update_info,
            "status": UpdateStatus.PENDING if pending else UpdateStatus.UP_TO_DATE,
            "pending_count": len(pending)
        }
    except Exception as e:
        if "404" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Update info for device {device_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch device updates: {str(e)}"
        )


@app.get("/updates/pending/all", response_model=List[DeviceWithPendingUpdates], tags=["Updates"])
async def list_pending_updates(client: AsyncWithSecureClient = Depends(get_client)):
    """
    Liste tous les appareils avec des mises à jour en attente
    """
    try:
        updates = await client.get_all_software_updates()
        
        pending_devices = []
        for update in updates:
            pending = update.get("pendingSoftwareUpdates", [])
            if pending:
                pending_devices.append(DeviceWithPendingUpdates(
                    device_id=update.get("deviceId"),
                    device_name=update.get("deviceName"),
                    platform=update.get("platform"),
                    pending_updates_count=len(pending),
                    pending_updates=[u.get("title", "Unknown") for u in pending]
                ))
        
        return pending_devices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending updates: {str(e)}"
        )


# ============================================================================
# Endpoints Statistics & Reports
# ============================================================================

@app.get("/statistics", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics(client: AsyncWithSecureClient = Depends(get_client)):
    """
    Récupère les statistiques complètes sur les appareils et mises à jour
    """
    try:
        # Récupérer les données
        devices = await client.get_all_devices()
        updates = await client.get_all_software_updates()
        
        # Créer un mapping device_id -> update_info
        updates_by_device = {item["deviceId"]: item for item in updates}
        
        # Calculer les statistiques
        total_devices = len(devices)
        devices_online = sum(1 for d in devices if d.get("online", False))
        devices_offline = total_devices - devices_online
        
        # Statistiques par plateforme
        platform_counts = {}
        for device in devices:
            platform = device.get("platform", "Unknown")
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        platform_stats = [
            PlatformStats(
                platform=platform,
                count=count,
                percentage=round((count / total_devices * 100) if total_devices > 0 else 0, 2)
            )
            for platform, count in platform_counts.items()
        ]
        
        # Statistiques par statut de mise à jour
        status_counts = {"up_to_date": 0, "pending": 0, "no_info": 0}
        pending_details = []
        
        for device in devices:
            device_id = device.get("id")
            if device_id in updates_by_device:
                update_info = updates_by_device[device_id]
                pending = update_info.get("pendingSoftwareUpdates", [])
                
                if pending:
                    status_counts["pending"] += 1
                    pending_details.append(DeviceWithPendingUpdates(
                        device_id=device_id,
                        device_name=device.get("name"),
                        platform=device.get("platform"),
                        pending_updates_count=len(pending),
                        pending_updates=[u.get("title", "Unknown") for u in pending]
                    ))
                else:
                    status_counts["up_to_date"] += 1
            else:
                status_counts["no_info"] += 1
        
        status_stats = [
            UpdateStatusStats(
                status=status,
                count=count,
                percentage=round((count / total_devices * 100) if total_devices > 0 else 0, 2)
            )
            for status, count in status_counts.items()
        ]
        
        return StatisticsResponse(
            total_devices=total_devices,
            devices_online=devices_online,
            devices_offline=devices_offline,
            devices_with_updates=len(updates),
            devices_up_to_date=status_counts["up_to_date"],
            devices_with_pending_updates=status_counts["pending"],
            devices_by_platform=platform_stats,
            devices_by_status=status_stats,
            devices_with_pending_details=pending_details,
            generated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate statistics: {str(e)}"
        )


@app.get("/reports/updates", response_model=UpdateReport, tags=["Reports"])
async def generate_update_report(client: AsyncWithSecureClient = Depends(get_client)):
    """
    Génère un rapport complet des mises à jour
    """
    try:
        stats = await get_statistics(client)
        
        summary = {
            "total_devices": stats.total_devices,
            "devices_up_to_date": stats.devices_up_to_date,
            "devices_pending": stats.devices_with_pending_updates,
            "devices_online": stats.devices_online,
            "devices_offline": stats.devices_offline
        }
        
        return UpdateReport(
            timestamp=datetime.now(),
            summary=summary,
            statistics=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


# ============================================================================
# Endpoints Databases
# ============================================================================

@app.get("/databases/versions", response_model=DatabaseVersionsResponse, tags=["Databases"])
async def get_database_versions(
    database_ids: List[str] = Query(..., description="Liste des IDs de bases de données"),
    client: AsyncWithSecureClient = Depends(get_client)
):
    """
    Récupère les dernières versions des bases de données spécifiées
    
    Exemples d'IDs de bases de données:
    - hydra-win64
    - capricorn-win64
    - sensor-win64
    - virgo-win64
    """
    try:
        response = await client.get_latest_database_versions(database_ids)
        return DatabaseVersionsResponse(
            items=response.get("items", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch database versions: {str(e)}"
        )


# ============================================================================
# Endpoints Security Events
# ============================================================================

@app.get("/security-events", response_model=SecurityEventsResponse, tags=["Security"])
async def list_security_events(
    anchor: Optional[str] = Query(None, description="Point de pagination"),
    limit: int = Query(100, ge=1, le=200, description="Nombre de résultats"),
    client: AsyncWithSecureClient = Depends(get_client)
):
    """
    Récupère les événements de sécurité
    """
    try:
        response = await client.get_security_events(anchor=anchor, limit=limit)
        return SecurityEventsResponse(
            items=response.get("items", []),
            nextAnchor=response.get("nextAnchor"),
            total=len(response.get("items", []))
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch security events: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)