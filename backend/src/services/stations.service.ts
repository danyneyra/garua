import estaciones from "../data/estaciones";
import { Station, StationSearch } from "../types/station/station";
import { capitalizeWords } from "../utils/string";

export function getAllStations(): Station[] {
  return estaciones.filter((station) => station.stationType === "M");
}

export function findStationByCode(code: string): Station | undefined {
  return estaciones.find(
    (e) => e.code.toLowerCase() === code.toLocaleLowerCase()
  );
}

export function searchStationsByName(
  name: string,
  limit: number = 6
): StationSearch[] {
  const term = name.toString().toLowerCase();
  const searchData = estaciones
    .filter(
      (e) => e.name.toLowerCase().includes(term)
    )
    .slice(0, limit);
  const dataResponse: StationSearch[] = searchData.map((item) => ({
    name: capitalizeWords(item.name),
    code: item.code,
    type: item.status == "AUTOMATICA" ? "AUTOMATIC" : "CONVENTIONAL",
    stationType: item.stationType
  }));
  return dataResponse;
}
