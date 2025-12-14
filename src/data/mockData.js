// Mock Data for Da Nang Tourism Super Agent

export const userProfile = {
  name: "Traveler",
  avatar:
    "https://lh3.googleusercontent.com/aida-public/AB6AXuC4AbK2oqcAKCpO22pKEVLJAJX-ykLdvx4F_Fbd1guobduyYlqflxJ9Xg_YxZamXw1Yf5D8E3dV1yPxtTkh3dD7tbnuQDS4JSLpyH1Qhfz-HIIc8VGvr_cdLNPSHtHzHwwbqYqpbbvwQoATOps1aS_wd0ZnutjXbCK1Q4Z6Jrm2puLxFA_F3BG4I2JkD5NGcHaaevRGRSHwwo2zSEr-MqkyOgAHh78eyJtLXposdyL9qXuZ2N2UXxy7HVzDENkfqqRH0MBK_zHkKUeS",
  location: { lat: 16.0544, lng: 108.2022 },
};

export const aiAgent = {
  name: "Local Agent",
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
      "Great choice! The Marble Mountains (Ngũ Hành Sơn) are beautiful this time of day.",
    timestamp: "9:42 AM",
    hasInfoCard: true,
    infoCard: {
      name: "Marble Mountains",
      image:
        "https://lh3.googleusercontent.com/aida-public/AB6AXuBrrTDjrH1hvbtNSdknnos-WIrvVccd2Ryt5RsDQhP2DprYZ2zz-wMDHV4TJXjTKPoISFoHRzRdpU447YYJCtNvC7LYtmpHHZXUsRUNYu0_d7XPyZQ3ESCmspngn3DH-0GkZYVKeuJSNUAZIPRQh6C07uwK_MCy7JeRfKsHh-NQdgbuaXe6YB3cdAEjBV3J8jE9Jhjaf6Q2tupEjzSJo0zO4HU4iJostMn9TZBsLKD2SE81FRXKLkkQ-I2JjR2bR9uwYkoL0Y7qnwFq",
      rating: 4.6,
      reviews: "2.4k",
      openUntil: "5:30 PM",
    },
    additionalText:
      "I've mapped a route for you. It's a **20-minute drive** from your current location.\n\nA GrabCar is available for roughly **150k VND**. Check the details on the right panel.",
  },
];

export const destinations = [
  {
    id: "marble-mountains",
    name: "Marble Mountains",
    description:
      "A cluster of five marble and limestone hills located in Ngũ Hành Sơn District, south of Da Nang city.",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuADIyE03c13yakVCeeoFPOtTxrU3zh4BY2IYmSYUfbWlzsFy78UIDIwGNGOvQL5SJRa-cPaf6hHXmG-SH4xJTIfxXoxd9YTGsBIJ6DXP-luwo9SAuJaJ4gDTBAs_EduNwDOtnzcrOJQUOy8c9v0disPQBFh4dlP7eph8lT42iVyvzB7HGFplf1Qr3-SJ6wFEMbuF-IGxttJmVGdCMRDVStlEn5jkiztnx6fX-iXtCacuQSMx4HuTi6Y43IZBbSnbnocD4mN8tCWkFzt",
    location: { lat: 16.0019, lng: 108.2626 },
    rating: 4.6,
    reviews: 2400,
    openNow: true,
    openUntil: "5:30 PM",
    duration: "20 min",
    entryFee: "40k VND",
    photoCount: 12,
    icon: "temple_buddhist",
  },
];

export const suggestionChips = [
  { id: 1, icon: "restaurant", label: "Seafood nearby" },
  { id: 2, icon: "local_cafe", label: "Coffee shops" },
  { id: 3, icon: "local_taxi", label: "Book ride" },
];

export const grabBooking = {
  carType: "GrabCar 4-seater",
  carDescription: "Compact • AC",
  price: "150k₫",
  eta: "~ 4 min away",
  carImage:
    "https://lh3.googleusercontent.com/aida-public/AB6AXuArh9M0CbTeNgekUl-epGu9t3dIh2yKDlknPlDSb-U3hd8aAGBa1kEEVNKHmyaXDPtPqexVTB6F217yQj-KZEzcp4nMWS9DpBiYPXLAthiEST93RqbkRDgJk1WyJgZVvPx2yRPiFjzOY_TBlM95dobRkfe029FsNPGaSerUAeHBXfVLwzALPRmCmX2DC7vg3BfRseE3kBL5dOkcfkSg6kHiQSXaJPh6q-sYGJzjvoEUwhohg7jUcr0CXFxMkHWCVG_xmIGKcuvq0E7t",
};

export const tripContext = {
  type: "Cultural Visit",
  budget: "Moderate Budget",
  icon: "temple_buddhist",
};

export const navigationLinks = [
  { id: 1, label: "Home", href: "#", active: true },
  { id: 2, label: "My Trips", href: "#", active: false },
  { id: 3, label: "My bookings", href: "#", active: false },
  { id: 4, label: "Saved Places", href: "#", active: false },
];

export const contextualTabs = [
  { id: 1, label: "Map View", icon: "map", active: true },
  { id: 2, label: "Itinerary", icon: "calendar_month", active: false },
  { id: 3, label: "Bookings", icon: "receipt_long", active: false },
];
