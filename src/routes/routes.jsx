import LandingPage from "../pages/LandingPage";
import AiMapView from "../pages/AiMapView";
import AiItinerary from "../pages/AiItinerary";
import BookingPage from "../pages/BookingPage";
import LoginPage from "../pages/LoginPage";

const appRoutes = [
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/map",
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
