import LandingPage from "../pages/LandingPage";
import AiMapView from "../pages/AiMapView";
import AiItinerary from "../pages/AiItinerary";
import BookingPage from "../pages/BookingPage";
import LoginPage from "../pages/LoginPage";
import PageTransition from "../components/layout/PageTransition";

const appRoutes = [
  {
    path: "/",
    element: (
      <PageTransition>
        <LandingPage />
      </PageTransition>
    ),
  },
  {
    path: "/login",
    element: (
      <PageTransition>
        <LoginPage />
      </PageTransition>
    ),
  },
  {
    path: "/map",
    element: (
      <PageTransition>
        <AiMapView />
      </PageTransition>
    ),
  },
  {
    path: "/ai-itinerary",
    element: (
      <PageTransition>
        <AiItinerary />
      </PageTransition>
    ),
  },
  {
    path: "/booking",
    element: (
      <PageTransition>
        <BookingPage />
      </PageTransition>
    ),
  },
];

export default appRoutes;
