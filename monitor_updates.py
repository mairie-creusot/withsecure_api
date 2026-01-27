"""
Script de surveillance des mises à jour des appareils WithSecure
Affiche un rapport détaillé sur l'état des mises à jour
"""

import json
from datetime import datetime
from collections import defaultdict
from typing import List, Dict
from withsecure_client import WithSecureClient, load_config


def analyze_update_status(devices: List[Dict], updates: List[Dict]) -> Dict:
    """
    Analyse l'état des mises à jour des appareils
    
    Args:
        devices: Liste des appareils
        updates: Liste des informations de mise à jour
        
    Returns:
        Dict contenant les statistiques d'analyse
    """
    # Créer un dictionnaire device_id -> update_info
    updates_by_device = {item["deviceId"]: item for item in updates}
    
    stats = {
        "total_devices": len(devices),
        "devices_with_updates": 0,
        "devices_up_to_date": 0,
        "devices_with_pending_updates": 0,
        "devices_by_status": defaultdict(int),
        "devices_by_platform": defaultdict(int),
        "update_details": []
    }
    
    for device in devices:
        device_id = device.get("id")
        device_name = device.get("name", "Unknown")
        platform = device.get("platform", "Unknown")
        
        stats["devices_by_platform"][platform] += 1
        
        if device_id in updates_by_device:
            update_info = updates_by_device[device_id]
            stats["devices_with_updates"] += 1
            
            # Analyser les mises à jour en attente
            pending = update_info.get("pendingSoftwareUpdates", [])
            
            if pending:
                stats["devices_with_pending_updates"] += 1
                status = "Mises à jour en attente"
            else:
                stats["devices_up_to_date"] += 1
                status = "À jour"
            
            stats["devices_by_status"][status] += 1
            
            stats["update_details"].append({
                "device_id": device_id,
                "device_name": device_name,
                "platform": platform,
                "status": status,
                "pending_updates": len(pending),
                "pending_update_names": [u.get("title", "Unknown") for u in pending]
            })
        else:
            stats["devices_by_status"]["Pas d'information"] += 1
    
    return stats


def print_update_report(stats: Dict):
    """Affiche un rapport formaté des mises à jour"""
    
    print("\n" + "="*80)
    print(" RAPPORT DE SURVEILLANCE DES MISES À JOUR WITHSECURE")
    print("="*80)
    print(f"\nDate du rapport: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "-"*80)
    print(" STATISTIQUES GÉNÉRALES")
    print("-"*80)
    print(f"Nombre total d'appareils: {stats['total_devices']}")
    print(f"Appareils avec informations de mise à jour: {stats['devices_with_updates']}")
    print(f"Appareils à jour: {stats['devices_up_to_date']}")
    print(f"Appareils avec mises à jour en attente: {stats['devices_with_pending_updates']}")
    
    print("\n" + "-"*80)
    print(" RÉPARTITION PAR PLATEFORME")
    print("-"*80)
    for platform, count in sorted(stats["devices_by_platform"].items()):
        percentage = (count / stats["total_devices"] * 100) if stats["total_devices"] > 0 else 0
        print(f"  {platform}: {count} ({percentage:.1f}%)")
    
    print("\n" + "-"*80)
    print(" RÉPARTITION PAR STATUT")
    print("-"*80)
    for status, count in sorted(stats["devices_by_status"].items()):
        percentage = (count / stats["total_devices"] * 100) if stats["total_devices"] > 0 else 0
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Afficher les détails des appareils avec mises à jour en attente
    devices_with_pending = [d for d in stats["update_details"] 
                           if d["status"] == "Mises à jour en attente"]
    
    if devices_with_pending:
        print("\n" + "-"*80)
        print(" APPAREILS AVEC MISES À JOUR EN ATTENTE")
        print("-"*80)
        
        for device in devices_with_pending:
            print(f"\n📱 {device['device_name']}")
            print(f"   ID: {device['device_id']}")
            print(f"   Plateforme: {device['platform']}")
            print(f"   Nombre de mises à jour: {device['pending_updates']}")
            print(f"   Mises à jour:")
            for update_name in device['pending_update_names']:
                print(f"     • {update_name}")
    
    print("\n" + "="*80)


def save_report_to_file(stats: Dict, filename: str = None):
    """
    Sauvegarde le rapport dans un fichier JSON
    
    Args:
        stats: Statistiques à sauvegarder
        filename: Nom du fichier (par défaut: update_report_YYYYMMDD_HHMMSS.json)
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"update_report_{timestamp}.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Rapport sauvegardé dans: {filename}")


def monitor_updates(client: WithSecureClient, save_to_file: bool = True):
    """
    Fonction principale de surveillance des mises à jour
    
    Args:
        client: Instance du client WithSecure
        save_to_file: Si True, sauvegarde le rapport dans un fichier
    """
    try:
        # Récupérer les appareils
        print("\n🔄 Récupération de la liste des appareils...")
        devices = client.get_all_devices()
        
        # Récupérer les informations de mise à jour
        print("\n🔄 Récupération des informations de mise à jour...")
        updates = client.get_all_software_updates()
        
        # Analyser les données
        print("\n📊 Analyse des données...")
        stats = analyze_update_status(devices, updates)
        
        # Afficher le rapport
        print_update_report(stats)
        
        # Sauvegarder si demandé
        if save_to_file:
            save_report_to_file(stats)
        
    except Exception as e:
        print(f"\n✗ Erreur lors de la surveillance: {e}")
        raise


def main():
    """Point d'entrée principal du script"""
    print("="*80)
    print(" SURVEILLANCE DES MISES À JOUR WITHSECURE")
    print("="*80)
    
    # Charger la configuration
    try:
        config = load_config("config.json")
    except Exception:
        print("\n💡 Conseil: Copiez config.example.json vers config.json et renseignez vos identifiants.")
        return
    
    # Initialiser le client
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        api_base_url=config.get("api_base_url", "https://api.connect.withsecure.com"),
        scopes=config.get("scopes", "connect.api.read connect.api.write")
    )
    
    # Authentification
    print("\n🔐 Authentification...")
    try:
        client.authenticate()
    except Exception as e:
        print(f"\n✗ Échec de l'authentification: {e}")
        print("\n💡 Vérifiez vos identifiants dans config.json")
        return
    
    # Lancer la surveillance
    monitor_updates(client, save_to_file=True)


if __name__ == "__main__":
    main()
