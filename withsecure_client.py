"""
WithSecure Elements API Client
Gère l'authentification et la surveillance des mises à jour des appareils
"""

import requests
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time


class WithSecureClient:
    """Client pour interagir avec l'API WithSecure Elements"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 api_base_url: str = "https://api.connect.withsecure.com",
                 scopes: str = "connect.api.read connect.api.write"):
        """
        Initialise le client API
        
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
        
    def authenticate(self) -> Dict:
        """
        Authentification OAuth2 avec client credentials flow
        
        Returns:
            Dict contenant le token et ses métadonnées
        """
        url = f"{self.api_base_url}/as/token.oauth2"
        
        # Création de l'en-tête Authorization Basic
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "User-Agent": "WithSecure-Python-Client/1.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "scope": self.scopes
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Calcul de l'expiration du token
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"✓ Authentification réussie. Token expire dans {expires_in} secondes.")
            return token_data
            
        except requests.exceptions.HTTPError as e:
            print(f"✗ Erreur d'authentification: {e}")
            if e.response is not None:
                print(f"Détails: {e.response.text}")
            raise
        except Exception as e:
            print(f"✗ Erreur inattendue: {e}")
            raise
    
    def is_token_valid(self) -> bool:
        """Vérifie si le token est toujours valide"""
        if not self.access_token or not self.token_expiry:
            return False
        # On garde une marge de 60 secondes
        return datetime.now() < (self.token_expiry - timedelta(seconds=60))
    
    def ensure_authenticated(self):
        """S'assure que le client est authentifié avec un token valide"""
        if not self.is_token_valid():
            self.authenticate()
    
    def _get_headers(self) -> Dict:
        """Retourne les en-têtes HTTP avec le token d'authentification"""
        self.ensure_authenticated()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "WithSecure-Python-Client/1.0",
            "Content-Type": "application/json"
        }
    
    def get_devices(self, anchor: Optional[str] = None, limit: int = 100) -> Dict:
        """
        Récupère la liste des appareils
        
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
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"✗ Erreur lors de la récupération des appareils: {e}")
            if e.response is not None:
                print(f"Détails: {e.response.text}")
            raise
    
    def get_all_devices(self) -> List[Dict]:
        """
        Récupère tous les appareils en gérant la pagination
        
        Returns:
            Liste de tous les appareils
        """
        all_devices = []
        anchor = None
        
        print("Récupération de tous les appareils...")
        while True:
            response = self.get_devices(anchor=anchor)
            items = response.get("items", [])
            all_devices.extend(items)
            
            print(f"  → {len(items)} appareils récupérés (total: {len(all_devices)})")
            
            # Vérifier s'il y a une page suivante
            next_anchor = response.get("nextAnchor")
            if not next_anchor:
                break
            anchor = next_anchor
        
        print(f"✓ Total: {len(all_devices)} appareils récupérés")
        return all_devices
    
    def get_software_updates(self, anchor: Optional[str] = None, limit: int = 100) -> Dict:
        """
        Récupère les informations sur les mises à jour logicielles
        
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
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"✗ Erreur lors de la récupération des mises à jour: {e}")
            if e.response is not None:
                print(f"Détails: {e.response.text}")
            raise
    
    def get_all_software_updates(self) -> List[Dict]:
        """
        Récupère toutes les informations de mise à jour
        
        Returns:
            Liste de toutes les mises à jour
        """
        all_updates = []
        anchor = None
        
        print("Récupération des informations de mise à jour...")
        while True:
            response = self.get_software_updates(anchor=anchor)
            items = response.get("items", [])
            all_updates.extend(items)
            
            print(f"  → {len(items)} mises à jour récupérées (total: {len(all_updates)})")
            
            next_anchor = response.get("nextAnchor")
            if not next_anchor:
                break
            anchor = next_anchor
        
        print(f"✓ Total: {len(all_updates)} informations de mise à jour récupérées")
        return all_updates
    
    def get_latest_database_versions(self, database_ids: List[str]) -> Dict:
        """
        Récupère les dernières versions des bases de données
        
        Args:
            database_ids: Liste des identifiants de base de données
            
        Returns:
            Dict contenant les versions des bases de données
        """
        url = f"{self.api_base_url}/databases/v1/latest-versions"
        params = {"id": database_ids}
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"✗ Erreur lors de la récupération des versions: {e}")
            if e.response is not None:
                print(f"Détails: {e.response.text}")
            raise


def load_config(config_path: str = "config.json") -> Dict:
    """Charge la configuration depuis un fichier JSON"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Fichier de configuration '{config_path}' non trouvé.")
        print("Créez un fichier config.json avec vos identifiants API.")
        raise
    except json.JSONDecodeError as e:
        print(f"✗ Erreur lors de la lecture du fichier de configuration: {e}")
        raise


if __name__ == "__main__":
    # Test du client
    print("=== Test du client WithSecure API ===\n")
    
    # Chargement de la configuration
    config = load_config("config.json")
    
    # Initialisation du client
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        api_base_url=config.get("api_base_url", "https://api.connect.withsecure.com"),
        scopes=config.get("scopes", "connect.api.read connect.api.write")
    )
    
    # Test d'authentification
    client.authenticate()
    
    # Test de récupération des appareils
    print("\n=== Récupération des appareils ===")
    devices = client.get_all_devices()
    
    if devices:
        print(f"\nPremier appareil:")
        print(json.dumps(devices[0], indent=2))
