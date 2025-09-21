import { DataPeriodBase } from "./station";

// Datos convencionales meteorológicos
export interface MeteorologicalConventionalData extends DataPeriodBase {
  type: "conventional";
  tempMax: number | null; // Temperatura máxima
  tempMin: number | null; // Temperatura mínima
  humidity: number | null; // Humedad
  precipitation: number | null; // Precipitación
}

// Datos automáticos meteorológicos
export interface MeteorologicalAutomaticData extends DataPeriodBase {
  type: "automatic";
  hour: string | null;
  temp: number | null; // Temperatura
  precipitation: number | null; // Precipitación
  humidity: number | null; // Humedad
  windDirection: number | null; // Dirección del viento
  windSpeed: number | null; // Velocidad del viento
}

// Unión de tipos de datos
export type MeteorologicalData =
  | MeteorologicalConventionalData
  | MeteorologicalAutomaticData;

// Data parqa response
export type MeteorologicalDataResponse = Omit<MeteorologicalData, "type">;

// Headers para exportar (en español)
export const MET_CONVENTIONAL_HEADERS = [
  "Año",
  "Mes",
  "Día",
  "Temp. Máx (°C)",
  "Temp. Mín (°C)",
  "Humedad (%)",
  "Precipitación (mm)",
];

export const MET_AUTOMATIC_HEADERS = [
  "Año",
  "Mes",
  "Día",
  "Hora",
  "Temperatura (°C)",
  "Precipitación (mm)",
  "Humedad (%)",
  "Dir. Viento (°)",
  "Vel. Viento (m/s)",
];
