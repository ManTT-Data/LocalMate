# Itinerary Components Architecture

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                      ItineraryList                          │
│  (Main container with DragDropContext)                      │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    DayHeader                          │ │
│  │  (Sticky header for each day)                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              Timeline Container                       │ │
│  │                                                       │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │         Droppable (Stops)                       │ │ │
│  │  │                                                 │ │ │
│  │  │  ┌───────────────────────────────────────────┐ │ │ │
│  │  │  │  Draggable → TimelineStop                 │ │ │ │
│  │  │  │                                           │ │ │ │
│  │  │  │  ├─ TimelineDot                          │ │ │ │
│  │  │  │  ├─ DestinationCard / StartLocationCard │ │ │ │
│  │  │  │  │   └─ DragHandle (if draggable)       │ │ │ │
│  │  │  │  └─ TravelBadge                          │ │ │ │
│  │  │  └───────────────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  │                                                       │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │         Droppable (Plan Items)                  │ │ │
│  │  │                                                 │ │ │
│  │  │  ┌───────────────────────────────────────────┐ │ │ │
│  │  │  │  Draggable → PlanItem                     │ │ │ │
│  │  │  │                                           │ │ │ │
│  │  │  │  ├─ TimelineDot                          │ │ │ │
│  │  │  │  ├─ DragHandle                           │ │ │ │
│  │  │  │  └─ Item Content                         │ │ │ │
│  │  │  └───────────────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      ItineraryMap                           │
│  (Map visualization with routes)                            │
│                                                             │
│  ├─ MapContainer                                           │
│  │   ├─ TileLayer                                          │
│  │   ├─ Polyline (route)                                   │
│  │   ├─ Markers (created via mapUtils.createCustomIcon)   │
│  │   └─ FitBounds                                          │
│  └─────────────────────────────────────────────────────────│
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────────┐
│  PlanContext     │
│  (User's plan)   │
└────────┬─────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌──────────────┐   ┌──────────────────┐
│ ItineraryList│   │ useItineraryStore│
│              │   │ (Zustand)        │
└──────┬───────┘   └────────┬─────────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐   ┌──────────────────┐
│  PlanItem    │   │  TimelineStop    │
│              │   │                  │
└──────────────┘   └──────────────────┘
                            │
                            ├─────────────┐
                            │             │
                            ▼             ▼
                   ┌──────────────┐  ┌──────────────┐
                   │DestinationCard│  │BookingModal │
                   └──────────────┘  └──────────────┘
```

## Shared Components Usage

```
┌─────────────────┐
│  TimelineDot    │ ◄─────┬─────────────┬──────────────┐
└─────────────────┘       │             │              │
                          │             │              │
                   ┌──────────┐  ┌──────────┐  ┌──────────┐
                   │PlanItem  │  │Timeline  │  │Future    │
                   │          │  │Stop      │  │Components│
                   └──────────┘  └──────────┘  └──────────┘

┌─────────────────┐
│  DragHandle     │ ◄─────┬─────────────┬──────────────┐
└─────────────────┘       │             │              │
                          │             │              │
                   ┌──────────┐  ┌──────────┐  ┌──────────┐
                   │PlanItem  │  │Destination│ │Future    │
                   │          │  │Card       │  │Components│
                   └──────────┘  └──────────┘  └──────────┘

┌─────────────────┐
│  TravelBadge    │ ◄─────┬─────────────┬──────────────┐
└─────────────────┘       │             │              │
                          │             │              │
                   ┌──────────┐  ┌──────────┐  ┌──────────┐
                   │Timeline  │  │Future    │  │Future    │
                   │Stop      │  │Components│  │Components│
                   └──────────┘  └──────────┘  └──────────┘
```

## Constants & Utilities Flow

```
┌─────────────────────────────────────────────────────────┐
│                    constants.js                         │
│  ┌────────────┬──────────┬──────────┬─────────────┐   │
│  │  COLORS    │  SIZES   │ Z_INDEX  │ DND_TYPES   │   │
│  └────────────┴──────────┴──────────┴─────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
       ▼               ▼               ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│PlanItem  │   │Timeline  │   │Itinerary │   │DayHeader │
│          │   │Stop      │   │List      │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘

┌─────────────────────────────────────────────────────────┐
│                    mapUtils.js                          │
│  ┌─────────────────┬──────────────┬─────────────────┐  │
│  │createCustomIcon │extractRoute  │extractWaypoints │  │
│  │                 │Positions     │                 │  │
│  └─────────────────┴──────────────┴─────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
                ┌──────────────┐
                │ItineraryMap  │
                │              │
                └──────────────┘
```

## Component Responsibilities

### Main Components

**ItineraryList**

- Manages DragDropContext
- Renders day headers
- Handles drag-and-drop logic
- Coordinates timeline and plan items

**ItineraryMap**

- Displays map with routes
- Renders custom markers
- Fits bounds to route
- Integrates with routing API

**TimelineStop**

- Displays individual stop
- Handles booking modal
- Supports drag-and-drop
- Shows travel information

**PlanItem**

- Displays user-added items
- Supports drag-and-drop
- Handles item removal
- Shows item actions

**DayHeader**

- Displays day information
- Sticky positioning
- Shows date and title

### Sub-Components

**TimelineDot**

- Visual indicator for timeline
- Supports multiple variants
- Configurable colors and icons

**DragHandle**

- Visual drag indicator
- Consistent across components
- Shows dragging state

**TravelBadge**

- Displays travel duration
- Shows travel mode
- Handles booking interaction

**DestinationCard**

- Shows destination info
- Displays booking status
- Handles booking actions
- Supports drag-and-drop

**StartLocationCard**

- Displays start location
- Shows location name
- Simple, non-interactive

### Utilities

**constants.js**

- Centralized configuration
- Color palette
- Size definitions
- Z-index layers
- DnD types
- Animation values

**mapUtils.js**

- Map marker creation
- Route processing
- Waypoint extraction
- GeoJSON handling

## Import Patterns

### Recommended

```javascript
// Use index.js for clean imports
import {
  ItineraryList,
  ItineraryMap,
  COLORS,
  SIZES,
} from "./components/Itinerary";
```

### Alternative

```javascript
// Direct imports still work
import ItineraryList from "./components/Itinerary/ItineraryList";
import { COLORS } from "./components/Itinerary/constants";
```

## State Management

```
┌──────────────────────────────────────────────────────┐
│                   State Sources                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────┐         ┌──────────────────┐   │
│  │  PlanContext   │         │ useItineraryStore│   │
│  │  (React Context)│        │  (Zustand)       │   │
│  └────────┬───────┘         └────────┬─────────┘   │
│           │                          │              │
│           │ User's plan items        │ Itinerary    │
│           │ Add/Remove/Reorder       │ data & routes│
│           │                          │              │
│           ▼                          ▼              │
│  ┌─────────────────────────────────────────────┐   │
│  │         Component State                     │   │
│  │  - Booking modal (TimelineStop)            │   │
│  │  - Route data (ItineraryMap)               │   │
│  │  - Drag state (via DnD library)            │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```
