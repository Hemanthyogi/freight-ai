"""
FreightMind AI — Emergency Diversion Engine
backend/services/diversion_engine.py

Handles ship emergency scenarios:
  - Engine fault / mechanical breakdown
  - Storm diversion (ordered by port authority)
  - Medical emergency requiring nearest port
  - Port closure after departure

Given current vessel position → calculates:
  - Nearest safe alternate port
  - Extra distance (nm) and additional steaming time
  - Additional cost (bunker + port charges)
  - Revised ETA at destination (if diversion then resume)
  - Recommended action
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any

from src.utils.logger import logger


# ── Known alternate ports with coordinates ───────────────────────────────────

_ALTERNATE_PORTS = [
    {
        "id": "colombo",
        "name": "Colombo (Sri Lanka)",
        "country": "Sri Lanka",
        "lat": 6.9271, "lon": 79.8612,
        "services": ["Engine Repair", "Medical", "Bunkering", "Dry Dock"],
        "port_cost_usd": 25000,
        "typical_wait_hours": 8,
    },
    {
        "id": "singapore",
        "name": "Singapore",
        "country": "Singapore",
        "lat": 1.3521, "lon": 103.8198,
        "services": ["Engine Repair", "Medical", "Bunkering", "Dry Dock", "Cargo Transfer"],
        "port_cost_usd": 45000,
        "typical_wait_hours": 12,
    },
    {
        "id": "mumbai",
        "name": "Mumbai Port",
        "country": "India",
        "lat": 18.9220, "lon": 72.8347,
        "services": ["Engine Repair", "Medical", "Bunkering"],
        "port_cost_usd": 18000,
        "typical_wait_hours": 16,
    },
    {
        "id": "visakhapatnam",
        "name": "Visakhapatnam (Vizag)",
        "country": "India",
        "lat": 17.6868, "lon": 83.2185,
        "services": ["Bunkering", "Medical", "Minor Repairs"],
        "port_cost_usd": 12000,
        "typical_wait_hours": 6,
    },
    {
        "id": "chennai",
        "name": "Chennai Port",
        "country": "India",
        "lat": 13.0827, "lon": 80.2707,
        "services": ["Engine Repair", "Medical", "Bunkering"],
        "port_cost_usd": 15000,
        "typical_wait_hours": 10,
    },
    {
        "id": "galle",
        "name": "Galle Anchorage (Sri Lanka)",
        "country": "Sri Lanka",
        "lat": 6.0335, "lon": 80.2170,
        "services": ["Medical", "Emergency Bunkering"],
        "port_cost_usd": 8000,
        "typical_wait_hours": 4,
    },
    {
        "id": "aden",
        "name": "Aden (Yemen)",
        "country": "Yemen",
        "lat": 12.7855, "lon": 45.0187,
        "services": ["Emergency Bunkering"],
        "port_cost_usd": 20000,
        "typical_wait_hours": 12,
    },
]

_EMERGENCY_TYPES = {
    "engine_fault":    "Engine Fault / Mechanical Breakdown",
    "storm_diversion": "Storm Diversion (Port Authority Order)",
    "medical":         "Medical Emergency Onboard",
    "port_closure":    "Destination Port Closure",
    "fire":            "Onboard Fire (Controlled)",
    "grounding_risk":  "Shallow Water / Grounding Risk",
}

# Typical fuel consumption at reduced speed (mt/day)
_REDUCED_SPEED_FUEL: dict[str, float] = {
    "Handysize": 12.0,
    "Supramax":  18.0,
    "Panamax":   22.0,
    "Capesize":  32.0,
}

_NORMAL_SPEED_FUEL: dict[str, float] = {
    "Handysize": 18.0,
    "Supramax":  26.0,
    "Panamax":   32.0,
    "Capesize":  52.0,
}


class DiversionEngine:
    """
    Calculates emergency diversion plans for vessels in distress.
    """

    def calculate_diversion(
        self,
        vessel_type: str,
        current_lat: float,
        current_lon: float,
        emergency_type: str,
        original_destination: str = "paradip",
        cargo_quantity_mt: float = 55000.0,
        speed_knots: float = 12.0,
        fuel_price_usd_mt: float = 620.0,
    ) -> dict[str, Any]:
        """
        Given vessel position and emergency type, return the optimal diversion plan.
        """
        logger.warning(
            f"[Diversion] Emergency declared: type={emergency_type}, "
            f"vessel={vessel_type}, pos=({current_lat:.2f},{current_lon:.2f})"
        )

        # Filter ports by emergency type (medical needs medical services, etc.)
        required_service = self._required_service(emergency_type)
        eligible_ports = [
            p for p in _ALTERNATE_PORTS
            if any(required_service.lower() in s.lower() for s in p["services"])
        ]
        if not eligible_ports:
            eligible_ports = _ALTERNATE_PORTS

        # Find nearest eligible port
        def dist_nm(port: dict) -> float:
            return self._haversine_nm(current_lat, current_lon, port["lat"], port["lon"])

        nearest = min(eligible_ports, key=dist_nm)
        top_3 = sorted(eligible_ports, key=dist_nm)[:3]

        divert_nm = dist_nm(nearest)
        divert_hours = divert_nm / speed_knots
        repair_hours = nearest["typical_wait_hours"]

        # Cost of diversion
        fuel_consumption = _REDUCED_SPEED_FUEL.get(vessel_type, 20.0) if "engine" in emergency_type else _NORMAL_SPEED_FUEL.get(vessel_type, 26.0)
        divert_fuel_cost = (divert_hours / 24.0) * fuel_consumption * fuel_price_usd_mt
        port_cost = nearest["port_cost_usd"]
        total_extra_cost = round(divert_fuel_cost + port_cost, 0)

        # Delay to original destination (resume after diversion)
        dest_coords = self._destination_coords(original_destination)
        from_divert_nm = self._haversine_nm(nearest["lat"], nearest["lon"], dest_coords["lat"], dest_coords["lon"])
        resume_hours = from_divert_nm / (speed_knots * 0.9)  # slightly reduced after repair
        total_delay_hours = divert_hours + repair_hours + resume_hours

        now = datetime.now(timezone.utc)
        revised_eta = now + timedelta(hours=total_delay_hours)

        recommendations = self._build_recommendations(emergency_type, nearest, total_extra_cost)

        result = {
            "emergency_id": f"emg_{now.strftime('%Y%m%d%H%M%S')}",
            "emergency_type": emergency_type,
            "emergency_label": _EMERGENCY_TYPES.get(emergency_type, emergency_type),
            "vessel_type": vessel_type,
            "current_position": {"lat": current_lat, "lon": current_lon},
            "recommended_diversion_port": {
                "id": nearest["id"],
                "name": nearest["name"],
                "country": nearest["country"],
                "lat": nearest["lat"],
                "lon": nearest["lon"],
                "distance_nm": round(divert_nm, 1),
                "eta_hours": round(divert_hours, 1),
                "services_available": nearest["services"],
                "port_cost_usd": nearest["port_cost_usd"],
            },
            "alternate_ports": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "distance_nm": round(dist_nm(p), 1),
                    "eta_hours": round(dist_nm(p) / speed_knots, 1),
                    "services": p["services"],
                }
                for p in top_3
            ],
            "cost_impact": {
                "diversion_fuel_cost_usd": round(divert_fuel_cost, 0),
                "diversion_port_charges_usd": port_cost,
                "total_extra_cost_usd": total_extra_cost,
                "additional_delay_hours": round(total_delay_hours, 1),
                "revised_destination_eta": revised_eta.strftime("%d %b %Y, %H:%M UTC"),
            },
            "recommendations": recommendations,
            "status": "DIVERSION_REQUIRED",
            "generated_at": now.isoformat(),
        }

        logger.info(
            f"[Diversion] Recommended: {nearest['name']} "
            f"({divert_nm:.0f}nm, {divert_hours:.1f}h, +${total_extra_cost:,.0f})"
        )
        return result

    def _required_service(self, emergency_type: str) -> str:
        service_map = {
            "engine_fault":    "Engine Repair",
            "storm_diversion": "Bunkering",
            "medical":         "Medical",
            "port_closure":    "Cargo Transfer",
            "fire":            "Engine Repair",
            "grounding_risk":  "Bunkering",
        }
        return service_map.get(emergency_type, "Bunkering")

    def _haversine_nm(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 3440.065  # Earth radius in nautical miles
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * R * math.asin(math.sqrt(a))

    def _destination_coords(self, port_id: str) -> dict:
        dest_map = {
            "paradip":       {"lat": 20.3194, "lon": 86.6089},
            "visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
            "haldia":        {"lat": 22.0667, "lon": 88.0667},
            "chennai":       {"lat": 13.0827, "lon": 80.2707},
            "ennore":        {"lat": 13.2000, "lon": 80.3200},
        }
        return dest_map.get(port_id, {"lat": 20.3194, "lon": 86.6089})

    def _build_recommendations(
        self, emergency_type: str, port: dict, extra_cost: float
    ) -> list[str]:
        recs = [
            f"Proceed immediately to {port['name']} — nearest port with required facilities.",
            f"Notify charterer and cargo owner of emergency diversion. ETA delay communicated.",
            f"Estimated additional cost: ${extra_cost:,.0f}. File P&I club notification.",
        ]
        if emergency_type == "engine_fault":
            recs.append("Reduce speed to safe maneuvering speed. Alert engine room crew.")
            recs.append("Prepare engine room log for port authority inspection on arrival.")
        elif emergency_type == "medical":
            recs.append("Contact MRCC (Maritime Rescue Coordination Centre) if critical.")
            recs.append("Prepare patient for helicopter evacuation if port ETA exceeds 6h.")
        elif emergency_type == "storm_diversion":
            recs.append("Follow VTS / port authority instructions on safe anchorage position.")
            recs.append("Monitor storm track and seek clearance to resume voyage when safe.")
        elif emergency_type == "port_closure":
            recs.append("Notify receiver of cargo at original destination immediately.")
            recs.append("Assess cargo transfer options at alternate port.")
        return recs


# Module-level singleton
diversion_engine = DiversionEngine()
