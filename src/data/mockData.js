// Mock Data for Da Nang Tourism Super Agent

import { href } from "react-router-dom";

export const userProfile = {
  name: "Traveler",
  avatar:
    "https://lh3.googleusercontent.com/aida-public/AB6AXuC4AbK2oqcAKCpO22pKEVLJAJX-ykLdvx4F_Fbd1guobduyYlqflxJ9Xg_YxZamXw1Yf5D8E3dV1yPxtTkh3dD7tbnuQDS4JSLpyH1Qhfz-HIIc8VGvr_cdLNPSHtHzHwwbqYqpbbvwQoATOps1aS_wd0ZnutjXbCK1Q4Z6Jrm2puLxFA_F3BG4I2JkD5NGcHaaevRGRSHwwo2zSEr-MqkyOgAHh78eyJtLXposdyL9qXuZ2N2UXxy7HVzDENkfqqRH0MBK_zHkKUeS",
  location: { lat: 16.0544, lng: 108.2022 },
};

export const aiAgent = {
  name: "Super Agent",
  avatar:
    "https://lh3.googleusercontent.com/aida-public/AB6AXuBPT4cRaJeVkKTOOImkcsyQXerboBrqLHhuLLV1t-i9YjdYe2FxKPsUxgthNKtXtbmg6q-c5tIcmJc-AS_8QDaOa9syh65MFnSf8WOoCtGXRpDBlqts1VUW5XcPN4kgUwAFkJ6yekABQ8o78dntl19IDXJ_8n8lZ0Sm-ONw8dKxG5uOqjDZpJ7QvRXm4IzmVM70xbc66qDQgxHw-cCxV0suqbDqDBKtgMCfB43hPI61zl2UyFaJTNuJtwcb7snC7e2zRmQisB9d8FRk",
};

export const chatMessages = [
  {
    id: 1,
    type: "date-separator",
    content: "Today, 9:41 AM",
  },
  {
    id: 2,
    type: "ai",
    sender: aiAgent,
    content:
      "Xin chào! Welcome to Da Nang! 🌴 I can help you plan your trip. Are you looking for relaxation, cultural sites, or a food adventure today?",
    timestamp: "9:41 AM",
  },
  {
    id: 3,
    type: "user",
    content:
      "I want to visit the Marble Mountains and then get some local food nearby. Can you help me plan that?",
    timestamp: "9:42 AM",
    status: "Read",
  },
  {
    id: 4,
    type: "ai",
    sender: aiAgent,
    content:
      "I've added **Marble Mountains** to your itinerary for this morning. It's best to visit early to avoid the heat.\n\nI also found a highly-rated **Mì Quảng** place nearby for lunch. Check the updated itinerary on the right!",
    timestamp: "9:42 AM",
    additionalText:
      '<button class="bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl px-4 py-2 text-primary dark:text-sky-400 text-sm font-semibold w-full flex items-center justify-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"><span>View Itinerary Details</span><span class="material-symbols-outlined text-[16px]">arrow_right_alt</span></button>',
  },
];

export const tripMetadata = {
  title: "Da Nang Cultural Tour",
  dateRange: "Dec 15 - Dec 17",
  duration: "3 days",
};

export const destinations = [
  {
    id: "marble-mountains",
    name: "Marble Mountains",
    description: "Limestone hills with caves & temples.",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBrrTDjrH1hvbtNSdknnos-WIrvVccd2Ryt5RsDQhP2DprYZ2zz-wMDHV4TJXjTKPoISFoHRzRdpU447YYJCtNvC7LYtmpHHZXUsRUNYu0_d7XPyZQ3ESCmspngn3DH-0GkZYVKeuJSNUAZIPRQh6C07uwK_MCy7JeRfKsHh-NQdgbuaXe6YB3cdAEjBV3J8jE9Jhjaf6Q2tupEjzSJo0zO4HU4iJostMn9TZBsLKD2SE81FRXKLkkQ-I2JjR2bR9uwYkoL0Y7qnwFq",
    location: { lat: 16.0019, lng: 108.2626 },
    rating: 4.6,
    reviews: 2400,
    type: "Sightseeing",
    duration: "1.5 hrs",
    cost: "40k VND",
    photoCount: "1.2k",
    openNow: true,
    entryFee: "40k VND",
  },
  {
    id: "mi-quang-ba-mua",
    name: "Mì Quảng Bà Mua",
    location: { lat: 16.05653, lng: 108.2084 },
    description: "Local Cuisine • Lunch",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuAuajKaysFsmhJPOzOEjqvmfqsx1AoKro4zAldb3m5FqXTW1tPjZMjHRaTGK4tj06JrqVgK1DbrQvJwTQSRuesuytCrB1Ed1PWqO05X5u8JgHG_chdTmnxejPsUfkYv2zcHTSkJv9F3aAzLIWp1Y4LOEhq0jBWiZDvCPF7iSlZ2v-Iy30tvPS8xbvm2vzT4xkIj7l3CmNNoxgLoXGFGfUSw2fzx5rJxUHW-dvDJsjJ4MU-UithTvjB0lGsV_Dnv9hENY_CaaxldwpNI",
    rating: 4.5,
    type: "Restaurant",
    isTopPick: true,
    duration: "1 hr",
    photoCount: "850",
    openNow: true,
    entryFee: "Free",
  },
  {
    id: "ba-na-hills",
    name: "Bà Nà Hills",
    description: "Mountain resort with Golden Bridge",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuDHpvF5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8",
    location: { lat: 15.9943, lng: 107.9988 },
    rating: 4.8,
    reviews: 8500,
    type: "Theme Park",
    duration: "4 hrs",
    cost: "700k VND",
    photoCount: "5.2k",
    openNow: true,
    entryFee: "700k VND",
  },
  {
    id: "han-market",
    name: "Hàn Market",
    description: "Traditional market with local goods",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuCKzOH9kOBKW4_h5F5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8hNqGd",
    location: { lat: 16.0677, lng: 108.2208 },
    rating: 4.3,
    reviews: 1200,
    type: "Shopping",
    duration: "2 hrs",
    cost: "Free",
    photoCount: "890",
    openNow: true,
    entryFee: "Free",
  },
  {
    id: "son-tra-peninsula",
    name: "Sơn Trà Peninsula",
    description: "Nature reserve with rare monkeys",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBNature5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5",
    location: { lat: 16.1068, lng: 108.27 },
    rating: 4.7,
    reviews: 3400,
    type: "Nature",
    duration: "3 hrs",
    cost: "Free",
    photoCount: "2.1k",
    openNow: true,
    entryFee: "Free",
  },
];

export const itineraryItems = [
  {
    day: 1,
    title: "Cultural Exploration",
    date: "Oct 24",
    totalCost: "1.2m VND",
    totalTime: "45 mins",
    stops: [
      {
        id: "start",
        time: "08:30 AM",
        type: "start",
        name: "Start from Hotel",
        locationName: "Hyatt Regency Danang",
        location: { lat: 16.012855984, lng: 108.263785 },
        nextTravel: {
          type: "drive",
          duration: "10 min",
          mode: "taxi",
          label: "Book Grab",
          price: "20k VND", // Assumed based on HTML
        },
      },
      {
        id: "marble-mountains",
        time: "09:00 AM",
        type: "destination",
        destinationId: "marble-mountains", // Links to destinations array
        destination: destinations[0],
        nextTravel: {
          type: "drive",
          duration: "20 min",
          mode: "taxi",
          label: "Book Grab",
          price: "150k VND", // Assumed based on HTML
        },
      },
      {
        id: "lunch-mi-quang",
        time: "11:00 AM",
        type: "destination",
        destinationId: "mi-quang-ba-mua",
        destination: destinations[1],
        isTopPick: true,
      },
    ],
  },
  {
    day: 2,
    title: "Beach & Relaxation",
    date: "Oct 25",
  },
];

export const grabBooking = {
  carType: "GrabCar 4-seater",
  carDescription: "Compact • AC",
  price: "150k₫",
  eta: "~ 4 min away",
  carImage:
    "https://lh3.googleusercontent.com/aida-public/AB6AXuArh9M0CbTeNgekUl-epGu9t3dIh2yKDlknPlDSb-U3hd8aAGBa1kEEVNKHmyaXDPtPqexVTB6F217yQj-KZEzcp4nMWS9DpBiYPXLAthiEST93RqbkRDgJk1WyJgZVvPx2yRPiFjzOY_TBlM95dobRkfe029FsNPGaSerUAeHBXfVLwzALPRmCmX2DC7vg3BfRseE3kBL5dOkcfkSg6kHiQSXaJPh6q-sYGJzjvoEUwhohg7jUcr0CXFxMkHWCVG_xmIGKcuvq0E7t",
};

export const suggestionChips = [
  { id: 1, icon: "add_location", label: "Add stop" },
  { id: 2, icon: "schedule", label: "Change time" },
];

export const tripContext = {
  type: "Cultural Visit",
  budget: "Moderate Budget",
  icon: "temple_buddhist",
};

// Bookings Data
export const mockBookings = [
  {
    id: "BK1734354000001",
    userId: "user-001",
    stopId: "marble-mountains",
    bookingType: "ticket",
    status: "confirmed",
    price: "40k VND",
    serviceName: "Marble Mountains Entry Ticket",
    bookingDetails: {
      quantity: 1,
      date: "2024-10-24",
      time: "09:00 AM",
    },
    createdAt: "2024-10-20T10:30:00Z",
    confirmedAt: "2024-10-20T10:30:05Z",
  },
  {
    id: "BK1734354000002",
    userId: "user-001",
    stopId: "marble-mountains",
    bookingType: "transportation",
    status: "confirmed",
    price: "150k VND",
    serviceName: "GrabCar to Mì Quảng Bà Mua",
    bookingDetails: {
      carType: "GrabCar 4-seater",
      pickupTime: "10:30 AM",
      from: "Marble Mountains",
      to: "Mì Quảng Bà Mua",
    },
    createdAt: "2024-10-20T11:00:00Z",
    confirmedAt: "2024-10-20T11:00:03Z",
  },
  {
    id: "BK1734354000003",
    userId: "user-001",
    stopId: "lunch-mi-quang",
    bookingType: "reservation",
    status: "pending",
    serviceName: "Mì Quảng Bà Mua - Table Reservation",
    bookingDetails: {
      partySize: 2,
      date: "2024-10-24",
      time: "11:00 AM",
      specialRequests: "Window seat preferred",
    },
    createdAt: "2024-10-20T12:00:00Z",
  },
];

// Enhanced Stops/Destinations Data (extends destinations array)
export const allStops = [
  ...destinations,
  {
    id: "my-khe-beach",
    name: "My Khe Beach",
    description: "One of the most beautiful beaches in Vietnam",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuCWqXzVxKzOH9kOBKW4_h5F5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8",
    location: { lat: 16.0397, lng: 108.2372 },
    rating: 4.7,
    reviews: 3200,
    type: "Beach",
    duration: "3 hrs",
    cost: "Free",
    photoCount: "2.5k",
    openNow: true,
    entryFee: "Free",
  },
  {
    id: "be-man-seafood",
    name: "Bé Mặn Seafood",
    description: "Fresh seafood by the beach",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBPzVxKzOH9kOBKW4_h5F5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8",
    location: { lat: 16.0421, lng: 108.2401 },
    rating: 4.5,
    reviews: 1800,
    type: "Restaurant",
    duration: "1.5 hrs",
    photoCount: "980",
    openNow: true,
    entryFee: "Free",
    isTopPick: true,
  },
  {
    id: "dragon-bridge",
    name: "Dragon Bridge",
    description: "Iconic bridge that breathes fire on weekends",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuDragonBridgeImagePlaceholder",
    location: { lat: 16.0608, lng: 108.2278 },
    rating: 4.8,
    reviews: 5200,
    type: "Landmark",
    duration: "1 hr",
    cost: "Free",
    photoCount: "3.8k",
    openNow: true,
    entryFee: "Free",
  },
];

// User Preferences Data
export const userPreferences = {
  userId: "user-001",
  travelStyle: "cultural-explorer",
  budgetLevel: "moderate",
  preferredTransport: ["walking", "taxi", "public-transport"],
  dietaryRestrictions: [],
  interests: ["history", "food", "photography", "beaches"],
  preferredLanguage: "vi",
  notifications: {
    bookingReminders: true,
    priceAlerts: true,
    recommendations: true,
  },
  savedLocations: [
    { name: "Hyatt Regency Danang", lat: 16.012855984, lng: 108.263785 },
  ],
  recentSearches: ["Marble Mountains", "Mì Quảng", "My Khe Beach"],
};
