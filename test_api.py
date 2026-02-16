"""
Script de test pour l'API FastAPI WithSecure
"""

import httpx
import asyncio
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


async def test_health():
    """Test de l'endpoint health"""
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data['status']}")
            print(f"✓ WithSecure API Connected: {data['withsecure_api_connected']}")
        else:
            print(f"✗ Erreur: {response.status_code}")


async def test_devices():
    """Test de récupération des appareils"""
    print("\n" + "="*60)
    print("TEST: Récupération des appareils")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/devices?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {data['total']} appareils récupérés")
            
            if data['items']:
                print("\nPremier appareil:")
                device = data['items'][0]
                print(f"  - ID: {device.get('id')}")
                print(f"  - Nom: {device.get('name', 'N/A')}")
                print(f"  - Plateforme: {device.get('platform', 'N/A')}")
        else:
            print(f"✗ Erreur: {response.status_code}")


async def test_statistics():
    """Test de récupération des statistiques"""
    print("\n" + "="*60)
    print("TEST: Statistiques")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{BASE_URL}/statistics")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Statistiques générées avec succès")
            print(f"\nRésumé:")
            print(f"  - Total d'appareils: {data['total_devices']}")
            print(f"  - Appareils en ligne: {data['devices_online']}")
            print(f"  - Mises à jour en attente: {data['devices_with_pending_updates']}")
            print(f"  - Appareils à jour: {data['devices_up_to_date']}")
            
            print(f"\nRépartition par plateforme:")
            for platform in data['devices_by_platform']:
                print(f"  - {platform['platform']}: {platform['count']} ({platform['percentage']}%)")
        else:
            print(f"✗ Erreur: {response.status_code}")
            print(f"Réponse: {response.text}")


async def test_pending_updates():
    """Test de récupération des mises à jour en attente"""
    print("\n" + "="*60)
    print("TEST: Mises à jour en attente")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{BASE_URL}/updates/pending/all")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {len(data)} appareils avec mises à jour en attente")
            
            if data:
                print("\nPremiers appareils:")
                for device in data[:3]:
                    print(f"\n  📱 {device.get('device_name', 'N/A')}")
                    print(f"     Plateforme: {device.get('platform', 'N/A')}")
                    print(f"     Mises à jour: {device['pending_updates_count']}")
                    for update in device['pending_updates'][:2]:
                        print(f"       • {update}")
        else:
            print(f"✗ Erreur: {response.status_code}")


async def test_database_versions():
    """Test de récupération des versions de bases de données"""
    print("\n" + "="*60)
    print("TEST: Versions des bases de données")
    print("="*60)
    
    database_ids = ["hydra-win64", "capricorn-win64"]
    params = "&".join([f"database_ids={db_id}" for db_id in database_ids])
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/databases/versions?{params}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Versions récupérées avec succès")
            
            for item in data.get('items', []):
                print(f"\n  • {item['id']}")
                print(f"    Titre: {item['title']}")
                print(f"    Version: {item['version']}")
        else:
            print(f"✗ Erreur: {response.status_code}")
            print(f"Note: Certaines bases de données peuvent ne pas être disponibles")


async def test_update_report():
    """Test de génération de rapport"""
    print("\n" + "="*60)
    print("TEST: Génération de rapport")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{BASE_URL}/reports/updates")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Rapport généré avec succès")
            print(f"\nRésumé du rapport:")
            summary = data['summary']
            for key, value in summary.items():
                print(f"  - {key}: {value}")
        else:
            print(f"✗ Erreur: {response.status_code}")


async def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print(" TESTS DE L'API FASTAPI WITHSECURE")
    print("="*60)
    print("\n⚠️  Assurez-vous que l'API est lancée sur http://localhost:8000")
    print("   Lancez l'API avec: python main.py\n")
    
    input("Appuyez sur Entrée pour commencer les tests...")
    
    tests = [
        ("Health Check", test_health),
        ("Appareils", test_devices),
        ("Statistiques", test_statistics),
        ("Mises à jour en attente", test_pending_updates),
        ("Versions de bases de données", test_database_versions),
        ("Rapport de mise à jour", test_update_report),
    ]
    
    results = {"success": 0, "failed": 0}
    
    for test_name, test_func in tests:
        try:
            await test_func()
            results["success"] += 1
        except Exception as e:
            print(f"\n✗ Erreur dans le test '{test_name}': {e}")
            results["failed"] += 1
        
        await asyncio.sleep(1)  # Pause entre les tests
    
    # Résumé
    print("\n" + "="*60)
    print(" RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"\n✓ Tests réussis: {results['success']}")
    print(f"✗ Tests échoués: {results['failed']}")
    print(f"\nTotal: {results['success'] + results['failed']} tests")
    
    if results['failed'] == 0:
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration et les logs.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
