#!/usr/bin/env python3
"""Manual test script to verify ABRP API works with your credentials."""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import sys

# Add custom_components to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from custom_components.abetterrouteplanner.api import ABRPApiClient

async def main():
    load_dotenv()

    email = os.getenv("ABRP_EMAIL")
    password = os.getenv("ABRP_PASSWORD")
    api_key = os.getenv("ABRP_API_KEY", "f4128c06-5e39-4852-95f9-3286712a9f3a")

    if not email or not password:
        print("❌ Error: ABRP_EMAIL and ABRP_PASSWORD must be set in .env file")
        return

    print("🔐 Testing ABRP API Login...")
    print(f"   Email: {email}")
    print(f"   API Key: {api_key[:20]}...")
    print()

    async with aiohttp.ClientSession() as session:
        client = ABRPApiClient(session, api_key)

        try:
            # Test login (without reCAPTCHA - might fail on first attempt)
            print("📡 Attempting login...")
            print("   Note: ABRP may require reCAPTCHA on first login")
            result = await client.login(email, password)

            print("✅ Login successful!")
            print(f"   Session ID: {result['session_id'][:30]}...")
            print(f"   Found {len(result['vehicles'])} vehicle(s)")
            print()

            for idx, vehicle in enumerate(result['vehicles'], 1):
                print(f"   Vehicle {idx}:")
                print(f"      ID: {vehicle['id']}")
                print(f"      Name: {vehicle['name']}")
            print()

            # Test telemetry
            if result['vehicles']:
                vehicle_id = result['vehicles'][0]['id']
                print(f"📊 Fetching telemetry for vehicle {vehicle_id}...")

                telemetry = await client.get_telemetry(result['session_id'], vehicle_id)

                if 'tlm' in telemetry:
                    tlm = telemetry['tlm']
                    print("✅ Telemetry retrieved successfully!")
                    print(f"   SOC: {tlm.get('soc')}%")
                    print(f"   Speed: {tlm.get('speed')} km/h")
                    print(f"   Location: {tlm.get('latitude')}, {tlm.get('longitude')}")
                    print(f"   Charging: {'Yes' if tlm.get('is_charging') == 1 else 'No'}")
                    print(f"   Power: {tlm.get('power')} kW")
                    print(f"   Battery Temp: {tlm.get('batt_temp')}°C")
                else:
                    print(f"✅ Telemetry response: {telemetry}")
            else:
                print("ℹ️  No vehicles found to test telemetry")

        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
