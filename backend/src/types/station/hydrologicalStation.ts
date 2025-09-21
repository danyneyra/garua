import { DataPeriodBase } from "./station";

// Datos convencionales hidrológicos
export interface HydrologicalConventionalData extends DataPeriodBase {
  type: "conventional";
  riverlevel06: number | null; // Nivel del río a las 06:00
  riverlevel10: number | null; // Nivel del río a las 10:00
  riverlevel14: number | null; // Nivel del río a las 14:00
  riverlevel18: number | null; // Nivel del río a las 18:00
}

// Datos automáticos hidrológicos
export interface HydrologicalAutomaticData extends DataPeriodBase {
  type: "automatic";
  hour: string | null;
  riverLevel: number | null; // Nivel del río
  precipitation: number | null; // Precipitación
}

// Unión de tipos de datos
export type HydrologicalData =
  | HydrologicalAutomaticData
  | HydrologicalConventionalData;

// Data para response
export type HydrologicalDataResponse = Omit<HydrologicalData, "type">;

// Headers para exportar (en español)
export const HYD_CONVENTIONAL_HEADERS = [
  "Año",
  "Mes",
  "Día",
  "Nivel del río (m) 06",
  "Nivel del río (m) 10",
  "Nivel del río (m) 14",
  "Nivel del río (m) 18",
];

export const HYD_AUTOMATIC_HEADERS = [
  "Año",
  "Mes",
  "Día",
  "Hora",
  "Nivel del río (m)",
  "Precipitación (mm/hora)",
];
