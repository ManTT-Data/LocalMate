"""Grab Transport Tool - MCP integration for Grab booking."""

from dataclasses import dataclass

from app.shared.utils.geo_utils import haversine_distance

from .base_tool import MCPBaseTool, ToolResult, ToolStatus


@dataclass
class BookingResult:
    """Booking result from Grab."""

    provider: str
    booking_id: str
    status: str
    ride_type: str
    pickup_location: str
    dropoff_location: str
    estimated_price: str
    estimated_arrival: str
    deep_link: str


class GrabTransportTool(MCPBaseTool):
    """
    Grab Transport Tool for ride booking.

    Supports booking rides between two locations.
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
                    "action": {
                        "type": "string",
                        "enum": ["book", "estimate"],
                        "description": "Action to perform",
                    },
                    "from_lat": {
                        "type": "number",
                        "description": "Pickup latitude",
                    },
                    "from_lng": {
                        "type": "number",
                        "description": "Pickup longitude",
                    },
                    "from_name": {
                        "type": "string",
                        "description": "Pickup location name",
                    },
                    "to_lat": {
                        "type": "number",
                        "description": "Dropoff latitude",
                    },
                    "to_lng": {
                        "type": "number",
                        "description": "Dropoff longitude",
                    },
                    "to_name": {
                        "type": "string",
                        "description": "Dropoff location name",
                    },
                    "ride_type": {
                        "type": "string",
                        "enum": ["GrabCar", "GrabBike", "GrabCar Plus"],
                        "description": "Type of ride",
                    },
                },
                "required": ["action", "from_lat", "from_lng", "to_lat", "to_lng"],
            },
        }

    async def book_ride(
        self,
        from_lat: float,
        from_lng: float,
        from_name: str,
        to_lat: float,
        to_lng: float,
        to_name: str,
        ride_type: str = "GrabCar",
    ) -> BookingResult:
        """
        Book a Grab ride.

        Args:
            from_lat, from_lng: Pickup coordinates
            from_name: Pickup location name
            to_lat, to_lng: Dropoff coordinates
            to_name: Dropoff location name
            ride_type: Type of Grab ride

        Returns:
            BookingResult with booking details
        """
        import uuid

        # Calculate distance and estimate
        distance_km = haversine_distance(
            (from_lat, from_lng),
            (to_lat, to_lng),
        )

        # Price calculation (VND)
        price_per_km = {"GrabBike": 4000, "GrabCar": 12000, "GrabCar Plus": 15000}
        base_price = {"GrabBike": 10000, "GrabCar": 25000, "GrabCar Plus": 35000}

        rate = price_per_km.get(ride_type, 12000)
        base = base_price.get(ride_type, 25000)
        estimated_price = base + int(distance_km * rate)

        # Generate booking ID and deep link
        booking_id = f"GRAB-{uuid.uuid4().hex[:8].upper()}"
        deep_link = f"grab://book?pickup={from_lat},{from_lng}&dropoff={to_lat},{to_lng}&type={ride_type}"

        return BookingResult(
            provider="grab",
            booking_id=booking_id,
            status="pending",
            ride_type=ride_type,
            pickup_location=from_name,
            dropoff_location=to_name,
            estimated_price=f"{estimated_price:,}₫",
            estimated_arrival="5-10 phút",
            deep_link=deep_link,
        )

    async def execute(self, params: dict) -> ToolResult:
        """Execute ride booking or estimation."""
        action = params.get("action", "book")

        # Validate required params
        required = ["from_lat", "from_lng", "to_lat", "to_lng"]
        for field in required:
            if field not in params:
                return ToolResult(
                    status=ToolStatus.FAILED,
                    error=f"Missing required field: {field}",
                )

        try:
            if action == "book":
                result = await self.book_ride(
                    from_lat=params["from_lat"],
                    from_lng=params["from_lng"],
                    from_name=params.get("from_name", "Điểm đón"),
                    to_lat=params["to_lat"],
                    to_lng=params["to_lng"],
                    to_name=params.get("to_name", "Điểm đến"),
                    ride_type=params.get("ride_type", "GrabCar"),
                )

                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    data={
                        "action": "book",
                        "booking_id": result.booking_id,
                        "status": result.status,
                        "ride_type": result.ride_type,
                        "pickup": result.pickup_location,
                        "dropoff": result.dropoff_location,
                        "estimated_price": result.estimated_price,
                        "estimated_arrival": result.estimated_arrival,
                        "deep_link": result.deep_link,
                    },
                )
            else:
                # Estimate only
                distance_km = haversine_distance(
                    (params["from_lat"], params["from_lng"]),
                    (params["to_lat"], params["to_lng"]),
                )
                ride_type = params.get("ride_type", "GrabCar")
                price_per_km = {"GrabBike": 4000, "GrabCar": 12000, "GrabCar Plus": 15000}
                base_price = {"GrabBike": 10000, "GrabCar": 25000, "GrabCar Plus": 35000}

                rate = price_per_km.get(ride_type, 12000)
                base = base_price.get(ride_type, 25000)
                price = base + int(distance_km * rate)

                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    data={
                        "action": "estimate",
                        "ride_type": ride_type,
                        "distance_km": round(distance_km, 2),
                        "estimated_price": f"{price:,}₫",
                        "duration_minutes": max(5, int(distance_km / 25 * 60)),
                    },
                )

        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=str(e),
            )


# Singleton instance
grab_transport_tool = GrabTransportTool()
