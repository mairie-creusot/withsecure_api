"""
Exemples d'utilisation du client WithSecure API
"""

from withsecure_client import WithSecureClient, load_config
import json


def example_basic_authentication():
    """Exemple 1: Authentification basique"""
    print("\n" + "="*60)
    print("EXEMPLE 1: Authentification")
    print("="*60)
    
    config = load_config("config.json")
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    # Authentification
    token_info = client.authenticate()
    print(f"\n✓ Token obtenu: {token_info['access_token'][:20]}...")
    print(f"✓ Expire dans: {token_info['expires_in']} secondes")


def example_list_devices():
    """Exemple 2: Lister tous les appareils"""
    print("\n" + "="*60)
    print("EXEMPLE 2: Liste des appareils")
    print("="*60)
    
    config = load_config("config.json")
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    # Récupérer tous les appareils
    devices = client.get_all_devices()
    
    print(f"\n✓ Total: {len(devices)} appareils")
    
    # Afficher les premiers appareils
    for i, device in enumerate(devices[:5], 1):
        print(f"\n{i}. {device.get('name', 'Sans nom')}")
        print(f"   ID: {device.get('id')}")
        print(f"   Plateforme: {device.get('platform', 'Unknown')}")
        print(f"   Type: {device.get('type', 'Unknown')}")


def example_filter_by_platform():
    """Exemple 3: Filtrer les appareils par plateforme"""
    print("\n" + "="*60)
    print("EXEMPLE 3: Filtrage par plateforme")
    print("="*60)
    
    config = load_config("config.json")
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    devices = client.get_all_devices()
    
    # Compter par plateforme
    platforms = {}
    for device in devices:
        platform = device.get('platform', 'Unknown')
        platforms[platform] = platforms.get(platform, 0) + 1
    
    print("\nRépartition par plateforme:")
    for platform, count in sorted(platforms.items()):
        print(f"  • {platform}: {count}")


def example_check_updates():
    """Exemple 4: Vérifier les mises à jour en attente"""
    print("\n" + "="*60)
    print("EXEMPLE 4: Mises à jour en attente")
    print("="*60)
    
    config = load_config("config.json")
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    # Récupérer les informations de mise à jour
    updates = client.get_all_software_updates()
    
    # Trouver les appareils avec mises à jour en attente
    devices_with_pending = []
    for update in updates:
        pending = update.get("pendingSoftwareUpdates", [])
        if pending:
            devices_with_pending.append({
                "device_id": update.get("deviceId"),
                "pending_count": len(pending),
                "updates": [u.get("title", "Unknown") for u in pending]
            })
    
    print(f"\n✓ {len(devices_with_pending)} appareils ont des mises à jour en attente")
    
    # Afficher les détails
    for device in devices_with_pending[:3]:  # Afficher les 3 premiers
        print(f"\n📱 Device ID: {device['device_id']}")
        print(f"   Mises à jour: {device['pending_count']}")
        for update in device['updates']:
            print(f"     • {update}")


def example_database_versions():
    """Exemple 5: Vérifier les versions des bases de données"""
    print("\n" + "="*60)
    print("EXEMPLE 5: Versions des bases de données")
    print("="*60)
    
    config = load_config("config.json")
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    # Bases de données communes pour Windows
    database_ids = [
        "hydra-win64",
        "capricorn-win64",
        "virgo-win64",
        "deepguard-db"
    ]
    
    try:
        versions = client.get_latest_database_versions(database_ids)
        
        print("\nDernières versions disponibles:")
        for item in versions.get("items", []):
            print(f"\n• {item.get('id')}")
            print(f"  Titre: {item.get('title')}")
            print(f"  Version: {item.get('version')}")
    except Exception as e:
        print(f"\n⚠️ Erreur: {e}")
        print("(Certaines bases de données peuvent ne pas être disponibles)")


def example_export_device_list():
    """Exemple 6: Exporter la liste des appareils en JSON"""
    print("\n" + "="*60)
    print("EXEMPLE 6: Export de la liste des appareils")
    print("="*60)
    
    config = load_config("config.json")
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    devices = client.get_all_devices()
    
    # Créer un export simplifié
    export_data = []
    for device in devices:
        export_data.append({
            "id": device.get("id"),
            "name": device.get("name"),
            "platform": device.get("platform"),
            "type": device.get("type"),
            "online": device.get("online", False)
        })
    
    # Sauvegarder dans un fichier
    filename = "devices_export.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Export sauvegardé dans: {filename}")
    print(f"✓ {len(export_data)} appareils exportés")


def example_statistics():
    """Exemple 7: Statistiques générales"""
    print("\n" + "="*60)
    print("EXEMPLE 7: Statistiques générales")
    print("="*60)
    
    config = load_config("config.json")
    client = WithSecureClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    devices = client.get_all_devices()
    updates = client.get_all_software_updates()
    
    # Calculer les statistiques
    total_devices = len(devices)
    online_devices = sum(1 for d in devices if d.get("online", False))
    
    total_pending_updates = 0
    for update in updates:
        total_pending_updates += len(update.get("pendingSoftwareUpdates", []))
    
    print(f"\n📊 Statistiques:")
    print(f"  • Total d'appareils: {total_devices}")
    print(f"  • Appareils en ligne: {online_devices} ({online_devices/total_devices*100:.1f}%)")
    print(f"  • Appareils hors ligne: {total_devices - online_devices}")
    print(f"  • Total de mises à jour en attente: {total_pending_updates}")


def main():
    """Point d'entrée principal"""
    print("\n" + "="*60)
    print(" EXEMPLES D'UTILISATION DU CLIENT WITHSECURE API")
    print("="*60)
    
    examples = [
        ("1", "Authentification", example_basic_authentication),
        ("2", "Lister les appareils", example_list_devices),
        ("3", "Filtrer par plateforme", example_filter_by_platform),
        ("4", "Vérifier les mises à jour", example_check_updates),
        ("5", "Versions des bases de données", example_database_versions),
        ("6", "Exporter la liste des appareils", example_export_device_list),
        ("7", "Statistiques générales", example_statistics),
    ]
    
    print("\nExemples disponibles:")
    for num, title, _ in examples:
        print(f"  {num}. {title}")
    print("  0. Tous les exemples")
    print("  q. Quitter")
    
    choice = input("\nChoisissez un exemple (0-7, q): ").strip()
    
    if choice.lower() == 'q':
        print("\nAu revoir!")
        return
    
    try:
        if choice == '0':
            # Exécuter tous les exemples
            for num, title, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n✗ Erreur dans l'exemple {num}: {e}")
                input("\nAppuyez sur Entrée pour continuer...")
        else:
            # Exécuter l'exemple choisi
            example_func = next((func for num, _, func in examples if num == choice), None)
            if example_func:
                example_func()
            else:
                print("\n✗ Choix invalide")
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
