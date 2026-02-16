"""
Client API WithSecure asynchrone optimisé pour FastAPI
"""

import httpx
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio


class AsyncWithSecureClient:
    """Client asynchrone pour interagir avec l'API WithSecure Elements"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 api_base_url: str = "https://api.connect.withsecure.com",
                 scopes: str = "connect.api.read connect.api.write"):
        """
        Initialise le client API asynchrone
        
        Args:
            client_id: L'identifiant client API
            client_secret: Le secret client API
            api_base_url: URL de base de l'API
            scopes: Les scopes OAuth2 requis
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base_url = api_base_url
        self.scopes = scopes
        self.access_token = None
        self.token_expiry = None
        self._lock = asyncio.Lock()
        
    async def authenticate(self) -> Dict:
        """
        Authentification OAuth2 avec client credentials flow (async)
        
        Returns:
            Dict contenant le token et ses métadonnées
        """
        url = f"{self.api_base_url}/as/token.oauth2"
        
        # Création de l'en-tête Authorization Basic
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "User-Agent": "WithSecure-FastAPI-Client/1.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "scope": self.scopes
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Calcul de l'expiration du token
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            return token_data
    
    def is_token_valid(self) -> bool:
        """Vérifie si le token est toujours valide"""
        if not self.access_token or not self.token_expiry:
            return False
        # Marge de sécurité de 60 secondes
        return datetime.now() < (self.token_expiry - timedelta(seconds=60))
    
    async def ensure_authenticated(self):
        """S'assure que le client est authentifié avec un token valide"""
        async with self._lock:
            if not self.is_token_valid():
                await self.authenticate()
    
    async def _get_headers(self) -> Dict:
        """Retourne les en-têtes HTTP avec le token d'authentification"""
        await self.ensure_authenticated()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "WithSecure-FastAPI-Client/1.0",
            "Content-Type": "application/json"
        }
    
    async def get_devices(self, anchor: Optional[str] = None, limit: int = 100) -> Dict:
        """
        Récupère la liste des appareils (async)
        
        Args:
            anchor: Point de pagination pour récupérer la page suivante
            limit: Nombre maximum d'appareils à récupérer (1-200)
            
        Returns:
            Dict contenant la liste des appareils et les informations de pagination
        """
        url = f"{self.api_base_url}/devices/v1"
        params = {"limit": limit}
        
        if anchor:
            params["anchor"] = anchor
        
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_all_devices(self) -> List[Dict]:
        """
        Récupère tous les appareils en gérant la pagination (async)
        
        Returns:
            Liste de tous les appareils
        """
        all_devices = []
        anchor = None
        
        while True:
            response = await self.get_devices(anchor=anchor)
            items = response.get("items", [])
            all_devices.extend(items)
            
            # Vérifier s'il y a une page suivante
            next_anchor = response.get("nextAnchor")
            if not next_anchor:
                break
            anchor = next_anchor
        
        return all_devices
    
    async def get_device_by_id(self, device_id: str) -> Dict:
        """
        Récupère les informations d'un appareil spécifique
        
        Args:
            device_id: L'identifiant de l'appareil
            
        Returns:
            Dict contenant les informations de l'appareil
        """
        url = f"{self.api_base_url}/devices/v1/{device_id}"
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def get_software_updates(self, anchor: Optional[str] = None, limit: int = 100) -> Dict:
        """
        Récupère les informations sur les mises à jour logicielles (async)
        
        Args:
            anchor: Point de pagination
            limit: Nombre maximum de résultats
            
        Returns:
            Dict contenant les informations de mise à jour
        """
        url = f"{self.api_base_url}/software-updates/v1"
        params = {"limit": limit}
        
        if anchor:
            params["anchor"] = anchor
        
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_all_software_updates(self) -> List[Dict]:
        """
        Récupère toutes les informations de mise à jour (async)
        
        Returns:
            Liste de toutes les mises à jour
        """
        all_updates = []
        anchor = None
        
        while True:
            response = await self.get_software_updates(anchor=anchor)
            items = response.get("items", [])
            all_updates.extend(items)
            
            next_anchor = response.get("nextAnchor")
            if not next_anchor:
                break
            anchor = next_anchor
        
        return all_updates
    
    async def get_software_update_by_device(self, device_id: str) -> Dict:
        """
        Récupère les mises à jour pour un appareil spécifique
        
        Args:
            device_id: L'identifiant de l'appareil
            
        Returns:
            Dict contenant les informations de mise à jour
        """
        url = f"{self.api_base_url}/software-updates/v1/{device_id}"
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def get_latest_database_versions(self, database_ids: List[str]) -> Dict:
        """
        Récupère les dernières versions des bases de données (async)
        
        Args:
            database_ids: Liste des identifiants de base de données
            
        Returns:
            Dict contenant les versions des bases de données
        """
        url = f"{self.api_base_url}/databases/v1/latest-versions"
        params = {"id": database_ids}
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_security_events(self, anchor: Optional[str] = None, limit: int = 100) -> Dict:
        """
        Récupère les événements de sécurité
        
        Args:
            anchor: Point de pagination
            limit: Nombre maximum de résultats
            
        Returns:
            Dict contenant les événements de sécurité
        """
        url = f"{self.api_base_url}/security-events/v1"
        params = {"limit": limit}
        
        if anchor:
            params["anchor"] = anchor
        
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
