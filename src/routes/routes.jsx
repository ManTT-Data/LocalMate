import AiMapView from "../pages/AiMapView";
import AiItinerary from "../pages/AiItinerary";

const appRoutes = [
  {
    path: "/",
    element: <AiMapView />,
  },
  {
    path: "/ai-itinerary",
    element: <AiItinerary />,
  },
];

export default appRoutes;
