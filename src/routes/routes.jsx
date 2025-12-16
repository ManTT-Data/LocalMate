import AiMapView from "../pages/AiMapView";
import AiItinerary from "../pages/AiItinerary";
import BookingPage from "../pages/BookingPage";

const appRoutes = [
  {
    path: "/",
    element: <AiMapView />,
  },
  {
    path: "/ai-itinerary",
    element: <AiItinerary />,
  },
  {
    path: "/booking",
    element: <BookingPage />,
  },
];

export default appRoutes;
