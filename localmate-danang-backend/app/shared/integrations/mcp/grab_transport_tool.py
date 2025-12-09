"""Grab Transport Tool - MCP integration for Grab ride booking."""

from dataclasses import dataclass

from app.shared.utils.geo_utils import haversine_distance

from .base_tool import MCPBaseTool, ToolResult, ToolStatus


@dataclass
class RideEstimate:
    """Estimated ride information."""

    provider: str
    ride_type: str
    price_min: int
    price_max: int
    currency: str
    duration_minutes: int
    distance_km: float


class GrabTransportTool(MCPBaseTool):
    """
    Grab Transport Tool for ride booking.

    Currently provides mock estimates.
    TODO: Integrate with actual Grab API when available.
    """

    @property
    def name(self) -> str:
        return "grab_transport"

    @property
    def description(self) -> str:
        return "Book a Grab ride between two locations in Da Nang"

    def get_tool_spec(self) -> dict:
        """Get OpenAI-style function spec."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "from_lat": {
                        "type": "number",
                        "description": "Pickup latitude",
                    },
                    "from_lng": {
                        "type": "number",
                        "description": "Pickup longitude",
                    },
                    "to_lat": {
                        "type": "number",
                        "description": "Dropoff latitude",
                    },
                    "to_lng": {
                        "type": "number",
                        "description": "Dropoff longitude",
                    },
                    "ride_type": {
                        "type": "string",
                        "enum": ["GrabCar", "GrabBike", "GrabCar Plus"],
                        "description": "Type of ride",
                    },
                },
                "required": ["from_lat", "from_lng", "to_lat", "to_lng"],
            },
        }

    async def validate_params(self, params: dict) -> tuple[bool, str | None]:
        """Validate ride parameters."""
        required = ["from_lat", "from_lng", "to_lat", "to_lng"]
        for field in required:
            if field not in params:
                return False, f"Missing required field: {field}"

        # Validate coordinates are in Da Nang area
        for prefix in ["from", "to"]:
            lat = params.get(f"{prefix}_lat", 0)
            lng = params.get(f"{prefix}_lng", 0)
            if not (15.9 <= lat <= 16.2 and 108.1 <= lng <= 108.4):
                return False, f"Coordinates must be in Da Nang area"

        return True, None

    async def estimate_ride(
        self,
        from_lat: float,
        from_lng: float,
        to_lat: float,
        to_lng: float,
        ride_type: str = "GrabCar",
    ) -> RideEstimate:
        """
        Estimate ride cost and duration (mock implementation).

        Args:
            from_lat, from_lng: Pickup coordinates
            to_lat, to_lng: Dropoff coordinates
            ride_type: Type of Grab ride

        Returns:
            RideEstimate with price and duration
        """
        # Calculate distance
        distance_km = haversine_distance(
            (from_lat, from_lng),
            (to_lat, to_lng),
        )

        # Base prices per km (VND) - mock data
        price_per_km = {
            "GrabBike": 4000,
            "GrabCar": 12000,
            "GrabCar Plus": 15000,
        }

        base_price = {
            "GrabBike": 10000,
            "GrabCar": 25000,
            "GrabCar Plus": 35000,
        }

        # Calculate estimate
        rate = price_per_km.get(ride_type, 12000)
        base = base_price.get(ride_type, 25000)

        estimated_price = base + int(distance_km * rate)

        # Add variance (±15%)
        price_min = int(estimated_price * 0.85)
        price_max = int(estimated_price * 1.15)

        # Estimate duration (avg 25 km/h in city)
        duration_minutes = max(5, int(distance_km / 25 * 60))

        return RideEstimate(
            provider="grab",
            ride_type=ride_type,
            price_min=price_min,
            price_max=price_max,
            currency="VND",
            duration_minutes=duration_minutes,
            distance_km=round(distance_km, 2),
        )

    async def execute(self, params: dict) -> ToolResult:
        """Execute ride estimation."""
        # Validate
        is_valid, error = await self.validate_params(params)
        if not is_valid:
            return ToolResult(status=ToolStatus.FAILED, error=error)

        try:
            estimate = await self.estimate_ride(
                from_lat=params["from_lat"],
                from_lng=params["from_lng"],
                to_lat=params["to_lat"],
                to_lng=params["to_lng"],
                ride_type=params.get("ride_type", "GrabCar"),
            )

            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "provider": estimate.provider,
                    "ride_type": estimate.ride_type,
                    "estimate_price": f"{estimate.price_min:,}₫ - {estimate.price_max:,}₫",
                    "price_min": estimate.price_min,
                    "price_max": estimate.price_max,
                    "currency": estimate.currency,
                    "duration_minutes": estimate.duration_minutes,
                    "distance_km": estimate.distance_km,
                },
            )
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=str(e),
            )


# Singleton instance
grab_transport_tool = GrabTransportTool()
