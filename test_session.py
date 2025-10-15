#!/usr/bin/env python3
"""Test ABRP API with session_id."""
import asyncio
import aiohttp
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from custom_components.abetterrouteplanner.api import ABRPApiClient

async def main():
    session_id = "37c4267efee530df5ba2933f8117edb5607a59f92df9073"
    api_key = "f4128c06-5e39-4852-95f9-3286712a9f3a"

    print("🔑 Testing ABRP Telemetry API with Session ID...")
    print(f"   Session ID: {session_id[:30]}...")
    print()

    async with aiohttp.ClientSession() as session:
        client = ABRPApiClient(session, api_key)

        try:
            # Test telemetry without vehicle_id
            print("📊 Fetching telemetry (no vehicle_id)...")
            telemetry = await client.get_telemetry(session_id)

            print("✅ Telemetry retrieved successfully!")
            print()

            if 'tlm' in telemetry:
                tlm = telemetry['tlm']
                print("📍 Vehicle Data:")
                print(f"   SOC: {tlm.get('soc')}%")
                print(f"   Speed: {tlm.get('speed')} km/h")
                print(f"   Location: {tlm.get('latitude')}, {tlm.get('longitude')}")
                print(f"   Charging: {'Yes' if tlm.get('is_charging') == 1 else 'No'}")
                print(f"   Power: {tlm.get('power')} kW")
                print(f"   Voltage: {tlm.get('voltage')} V")
                print(f"   Current: {tlm.get('current')} A")
                print(f"   Battery Temp: {tlm.get('batt_temp')}°C")
                print(f"   External Temp: {tlm.get('ext_temp')}°C")
                print(f"   Elevation: {tlm.get('elevation')} m")
                print(f"   Car Model: {tlm.get('car_model')}")
            else:
                print(f"Response: {telemetry}")

        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
