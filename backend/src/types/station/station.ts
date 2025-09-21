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
  stationType: StationType;
  department?: string;
  province?: string;
  district?: string;
  altitude?: number;
  dataAvailableSince?: number; 
}

// Información para la búsqueda
export interface StationSearch extends Pick<StationBase, "name" | "code" | "stationType"> {
  type: DataMode;
}

// Estación Meteorológica
export interface MeteorologicalStation extends StationBase {
  stationType: "M";
  mode?: DataMode;
}

// Estación Hidrológica
export interface HydrologicalStation extends StationBase {
  stationType: "H";
  mode?: DataMode;
}

// Estaciones
export type Station = MeteorologicalStation | HydrologicalStation;

export interface DataPeriodBase {
  year: number;
  month: number;
  day: number;
}