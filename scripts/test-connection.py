#!/usr/bin/env python3
"""
Script de test de connexion aux services
"""

import asyncio
import json
import os
from pathlib import Path

import aiohttp
import openai
from dotenv import load_dotenv

# Charger .env
load_dotenv()


async def test_openai_connection():
    """Test la connexion à OpenAI"""
    print("\n🧪 Test OpenAI...")
    try:
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY non configurée")
            return False
        
        client = openai.AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Dis bonjour en français"}],
            max_tokens=10
        )
        
        print(f"✅ OpenAI OK: {response.choices[0].message.content}")
        return True
    
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return False


async def test_home_assistant():
    """Test la connexion à Home Assistant"""
    print("\n🧪 Test Home Assistant...")
    try:
        url = os.getenv('HA_URL', 'http://home-assistant:8123')
        token = os.getenv('HA_TOKEN')
        
        if not token:
            print("❌ HA_TOKEN non configurée")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/api/", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Home Assistant OK: {data.get('message', 'Connecté')}")
                    return True
                else:
                    print(f"❌ Erreur Home Assistant: {resp.status}")
                    return False
    
    except Exception as e:
        print(f"❌ Erreur Home Assistant: {e}")
        return False


async def main():
    print("=" * 50)
    print("🤖 Test de connexion JARVIS")
    print("=" * 50)
    
    openai_ok = await test_openai_connection()
    ha_ok = await test_home_assistant()
    
    print("\n" + "=" * 50)
    if openai_ok and ha_ok:
        print("✅ Tous les tests réussis! JARVIS est prêt.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
