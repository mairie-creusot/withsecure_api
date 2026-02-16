"""
Modèles Pydantic pour l'API FastAPI WithSecure
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    """Plateformes supportées"""
    WINDOWS = "Windows"
    MACOS = "macOS"
    LINUX = "Linux"
    UNKNOWN = "Unknown"


class UpdateStatus(str, Enum):
    """Statuts de mise à jour"""
    UP_TO_DATE = "up_to_date"
    PENDING = "pending"
    NO_INFO = "no_info"


# ============================================================================
# Modèles de requête
# ============================================================================

class DeviceQuery(BaseModel):
    """Paramètres de requête pour la liste des appareils"""
    anchor: Optional[str] = Field(None, description="Point de pagination")
    limit: int = Field(100, ge=1, le=200, description="Nombre de résultats par page")


class DatabaseVersionQuery(BaseModel):
    """Paramètres pour récupérer les versions de bases de données"""
    database_ids: List[str] = Field(..., description="Liste des IDs de bases de données")


# ============================================================================
# Modèles de réponse
# ============================================================================

class TokenResponse(BaseModel):
    """Réponse d'authentification OAuth"""
    access_token: str
    token_type: str
    expires_in: int


class HealthResponse(BaseModel):
    """Réponse de santé de l'API"""
    status: str
    timestamp: datetime
    withsecure_api_connected: bool


class Device(BaseModel):
    """Informations d'un appareil"""
    id: str
    name: Optional[str] = None
    platform: Optional[str] = None
    type: Optional[str] = None
    online: Optional[bool] = None
    lastSeen: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345-abcde-67890",
                "name": "PC-BUREAU-01",
                "platform": "Windows",
                "type": "computer",
                "online": True,
                "lastSeen": "2026-01-27T10:30:00Z"
            }
        }


class DeviceListResponse(BaseModel):
    """Réponse pour la liste des appareils"""
    items: List[Device]
    nextAnchor: Optional[str] = None
    total: int = Field(..., description="Nombre total d'appareils")


class SoftwareUpdate(BaseModel):
    """Information sur une mise à jour logicielle"""
    title: Optional[str] = None
    version: Optional[str] = None
    id: Optional[str] = None


class DeviceUpdateInfo(BaseModel):
    """Information de mise à jour pour un appareil"""
    deviceId: str
    pendingSoftwareUpdates: List[SoftwareUpdate] = []
    status: UpdateStatus


class UpdatesListResponse(BaseModel):
    """Réponse pour la liste des mises à jour"""
    items: List[DeviceUpdateInfo]
    nextAnchor: Optional[str] = None
    total: int


class DatabaseVersion(BaseModel):
    """Version d'une base de données"""
    id: str
    title: str
    version: int


class DatabaseVersionsResponse(BaseModel):
    """Réponse pour les versions de bases de données"""
    items: List[DatabaseVersion]


class PlatformStats(BaseModel):
    """Statistiques par plateforme"""
    platform: str
    count: int
    percentage: float


class UpdateStatusStats(BaseModel):
    """Statistiques par statut de mise à jour"""
    status: str
    count: int
    percentage: float


class DeviceWithPendingUpdates(BaseModel):
    """Appareil avec mises à jour en attente"""
    device_id: str
    device_name: Optional[str] = None
    platform: Optional[str] = None
    pending_updates_count: int
    pending_updates: List[str]


class StatisticsResponse(BaseModel):
    """Statistiques complètes sur les appareils et mises à jour"""
    total_devices: int
    devices_online: int
    devices_offline: int
    devices_with_updates: int
    devices_up_to_date: int
    devices_with_pending_updates: int
    devices_by_platform: List[PlatformStats]
    devices_by_status: List[UpdateStatusStats]
    devices_with_pending_details: List[DeviceWithPendingUpdates]
    generated_at: datetime


class UpdateReport(BaseModel):
    """Rapport de mise à jour complet"""
    timestamp: datetime
    summary: Dict[str, Any]
    statistics: StatisticsResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-01-27T14:30:00Z",
                "summary": {
                    "total_devices": 50,
                    "devices_up_to_date": 35,
                    "devices_pending": 13
                },
                "statistics": "..."
            }
        }


class SecurityEvent(BaseModel):
    """Événement de sécurité"""
    id: str
    type: Optional[str] = None
    severity: Optional[str] = None
    timestamp: Optional[datetime] = None
    deviceId: Optional[str] = None
    description: Optional[str] = None


class SecurityEventsResponse(BaseModel):
    """Réponse pour les événements de sécurité"""
    items: List[SecurityEvent]
    nextAnchor: Optional[str] = None
    total: int


# ============================================================================
# Modèles d'erreur
# ============================================================================

class ErrorDetail(BaseModel):
    """Détails d'une erreur"""
    message: str
    code: Optional[int] = None
    transaction_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Réponse d'erreur standard"""
    error: str
    detail: Optional[str] = None
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Authentication failed",
                "detail": "Invalid client credentials",
                "status_code": 401
            }
        }
