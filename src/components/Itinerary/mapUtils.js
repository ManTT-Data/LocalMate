import L from "leaflet";

/**
 * Creates custom map marker icons for different stop types
 */
export const createCustomIcon = (stop) => {
  const isStart = stop.type === "start";

  let html = "";

  if (isStart) {
    html = `
         <div class="relative flex items-center justify-center ">
            <div class="size-10 rounded-lg bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-400 shadow-md border-2 border-white dark:border-slate-800">
                <span class="material-symbols-outlined text-[20px]">home_pin</span>
            </div>
            <div class="absolute -bottom-2 bg-white text-white dark:bg-slate-900 px-2 py-0.5 rounded text-[10px] font-bold shadow-md whitespace-nowrap">${
              stop.locationName || "Start"
            }</div>
         </div>
        `;
  } else {
    html = `
        <div class="flex flex-col items-center" style="transform: translate(-50%, -100%);">
            <div class="relative flex flex-col items-center">
                <div class="bg-slate-900 text-white p-1 rounded-lg shadow-lg flex items-center gap-2 hover:scale-110 transition-transform border border-slate-700">
                     <div class="w-8 h-8 rounded bg-cover bg-center shrink-0" style="background-image: url('${stop.destination?.image}')"></div>
                     <span class="font-bold text-xs whitespace-nowrap pr-2">${stop.destination?.name}</span>
                </div>
                <!-- Triangle pointer -->
                <div class="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-slate-900 -mt-[1px]"></div>
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
    .filter((stop) => stop.location || stop.destination?.location)
    .map((stop) => stop.location || stop.destination.location);
};
