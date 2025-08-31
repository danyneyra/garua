import { ObjectGeneric } from "./object";

type StatusStation = "REAL" | "DIFERIDO" | "AUTOMATICA";
type StationCategory = 'EAA'| 'PE'|'CP'| 'HLM'|'MAP'|'EHA'| 'EHMA'|'CO'|'EMA'|'PLU'| 'EAMA'| 'HLG';
export type StationType = "M" | "H"; // M = Metereólogica ; H = Hidrólogica
type DataMode = "CONVENTIONAL" | "AUTOMATIC";


// Información básica de la estación
export interface StationBase {
  name: string;
  code: string;
  codeOld: string;
  category: StationCategory;
  latitude: number;
  longitude: number;
  status: StatusStation;
  department?: string;
  province?: string;
  district?: string;
  altitude?: number;
  dataAvailableSince?: number; 
}

// Información para la búsqueda
type StationSearch = Pick<StationBase, "name" | "code">

// Resultados de búsqueda
export interface ResultsSearch {
    results: StationSearch[];
}

// Estación Meteorológica
export interface MeteorologicalStation extends StationBase {
  stationType: "METEOROLOGICAL";
  mode?: DataMode;
}

// Estación Hidrológica
export interface HydrologicalStation extends StationBase {
  stationType: "HYDROLOGICAL";
  mode?: DataMode;
}

// Estaciones
export type Station = MeteorologicalStation | HydrologicalStation;

interface DataPeriodBase {
  year: number;
  month: number;
  day: number;
}

export interface StationDataYears {
  yearStart: string;
  yearEnd: string;
  avalibles: ObjectGeneric[];
}

// Datos convencionales meteorológicos
export interface MeteorologicalConventionalData extends DataPeriodBase {
  type: "conventional"
  tempMax: number | null;
  tempMin: number | null;
  humidity: number | null;
  precipitation: number | null;
}

// Datos automáticos meteorológicos
export interface MeteorologicalAutomaticData extends DataPeriodBase {
  type: "automatic"
  hour: string | null;
  temp: number | null;
  precipitation: number | null;
  humidity: number | null;
  windDirection: number | null;
  windSpeed: number | null;
}


// Unión de tipos de datos
export type MeteorologicalData = MeteorologicalConventionalData | MeteorologicalAutomaticData;

// Data parqa response
export type MeteorologicalDataResponse = Omit<MeteorologicalData, "type">

// Headers para exportar (en español)
export const MET_CONVENTIONAL_HEADERS = [
  "Año", "Mes", "Día", "Temp. Máx (°C)", "Temp. Mín (°C)", "Humedad (%)", "Precipitación (mm)"
];

export const MET_AUTOMATIC_HEADERS = [
  "Año", "Mes", "Día", "Hora", "Temperatura (°C)", "Precipitación (mm)", "Humedad (%)", "Dir. Viento (°)", "Vel. Viento (m/s)"
];