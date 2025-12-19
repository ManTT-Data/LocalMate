import L from "leaflet";

/**
 * Creates custom map marker icons for different stop types
 */
export const createCustomIcon = (stop) => {
  const isStart = stop.type === "start";

  let html = "";

  if (isStart) {
    html = `
         <div class="relative flex items-center justify-center transform -translate-y-1/2">
            <div class="size-10 rounded-2xl bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center text-white shadow-xl border-2 border-white overflow-hidden">
                <span class="material-symbols-outlined text-[20px]">home_pin</span>
            </div>
            <div class="absolute -bottom-1 bg-white dark:bg-slate-900 border border-slate-200 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-lg whitespace-nowrap text-slate-800 dark:text-white">${stop.locationName || "Start"
      }</div>
         </div>
        `;
  } else {
    html = `
        <div class="flex flex-col items-center" style="transform: translate(-50%, -100%);">
            <div class="relative flex flex-col items-center">
                <div class="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md p-1.5 rounded-2xl shadow-2xl flex items-center gap-2 hover:scale-110 transition-all duration-300 border border-white/50 dark:border-slate-800">
                     <div class="w-9 h-9 rounded-xl bg-cover bg-center shrink-0 shadow-inner" style="background-image: url('${stop.destination?.image}')"></div>
                     <div class="flex flex-col pr-2">
                        <span class="font-bold text-xs whitespace-nowrap text-slate-800 dark:text-white">${stop.destination?.name}</span>
                        <span class="text-[9px] text-slate-500 uppercase font-semibold tracking-wider">${stop.destination?.type || 'Destination'}</span>
                     </div>
                </div>
                <!-- Triangle pointer -->
                <div class="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-white dark:border-t-slate-900 shadow-xl" style="margin-top: -1px;"></div>
            </div>
        </div>
        `;
  }

  return new L.DivIcon({
    className: "custom-marker-itinerary",
    html: html,
    iconSize: null,
    iconAnchor: isStart ? [20, 20] : [0, 0],
  });
};

/**
 * Extracts route positions from GeoJSON route data
 */
export const extractRoutePositions = (routeData) => {
  if (!routeData || !routeData.features || !routeData.features[0]) return [];

  const geometry = routeData.features[0].geometry;

  if (geometry.type === "LineString") {
    return geometry.coordinates.map((coord) => [coord[1], coord[0]]);
  } else if (geometry.type === "MultiLineString") {
    return geometry.coordinates.flat().map((coord) => [coord[1], coord[0]]);
  }

  return [];
};

/**
 * Extracts waypoints from stops array
 */
export const extractWaypoints = (stops) => {
  return stops
    .map((stop) => {
      // Try to get coordinates from multiple sources (in priority order)
      // 1. From snapshot
      if (stop.snapshot?.lat && stop.snapshot?.lng) {
        return { lat: stop.snapshot.lat, lng: stop.snapshot.lng };
      }
      // 2. From destination directly
      if (stop.destination?.lat && stop.destination?.lng) {
        return { lat: stop.destination.lat, lng: stop.destination.lng };
      }
      // 3. From location or destination.location
      return stop.location || stop.destination?.location;
    })
    .filter((location) => location && location.lat && location.lng);
};
