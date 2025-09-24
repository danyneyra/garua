import axios from "axios";
import * as cheerio from "cheerio";
import qs from "qs"; // para serializar form-urlencoded
import { Station } from "../types/station/station";
import { sleep } from "../utils/sleep";
import { getDataByYearCache } from "../controllers/cache.controller";
import { parseDateString } from "../utils/parsedDate";
import config from "../config/config";
import { concatenateUrlWithParams } from "../utils/url";
import { MeteorologicalData } from "../types/station/meteorologicalStation";
import { HydrologicalData } from "../types/station/hydrologicalStation";

const getStationInfo = async (station: Station) => {
  try {
    // Preparar datos para form-urlencoded
    const params = {
      cod: station.code,
      estado: station.status,
      tipo_esta: station.stationType,
      cate: station.category,
      cod_old: station.codeOld ?? "",
    };

    const url = concatenateUrlWithParams(config.apis.senamhiStationUrl, params);

    // Llamar API de SENAMHI
    const { data: html } = await axios.get(url);

    // Parseamos HTML
    const $ = cheerio.load(html);

    // Extraer info estación
    const years = $("#CBOFiltro option")
      .map((i, el) => Number($(el).text().trim().split("-")[0]))
      .get();
    const stationInfo: Station = {
      ...station,
      department: $("#frmData tr").eq(2).find("td").eq(1).text().trim(),
      province: $("#frmData tr").eq(2).find("td").eq(3).text().trim(),
      district: $("#frmData tr").eq(2).find("td").eq(5).text().trim(),
      altitude: Number(
        $("#frmData tr")
          .eq(3)
          .find("td")
          .eq(5)
          .text()
          .trim()
          .replace(/[^\d.-]/g, "")
      ),
      dataAvailableSince: Math.min(...years),
    };
    return stationInfo;
  } catch (error) {
    console.error("Error al consultar SENAMHI:", error);
    throw new Error("No se pudo obtener información");
  }
};

const getStationData = async (station: Station) => {
  try {
    // Preparar datos para form-urlencoded
    const formData = qs.stringify({
      estaciones: station.code,
      CBOFiltro: `202501`, // Ej: 202503
      t_e: station.stationType,
      estado: station.status,
      cod_old: station.codeOld,
    });

    // Llamar API de SENAMHI
    const { data: html } = await axios.post(
      config.apis.senamhiDataUrl,
      formData,
      {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }
    );

    // Parseamos HTML
    const $ = cheerio.load(html);

    // Extraer info estación
    const stationInfo: Station = {
      ...station,
      department: $("#tableHidden tr").eq(1).find("td").eq(1).text().trim(),
      province: $("#tableHidden tr").eq(1).find("td").eq(3).text().trim(),
      district: $("#tableHidden tr").eq(1).find("td").eq(5).text().trim(),
      altitude: Number(
        $("#frmData tr")
          .eq(3)
          .find("td")
          .eq(5)
          .text()
          .trim()
          .replace(/[^\d.-]/g, "")
      ),
    };
    return stationInfo;
  } catch (error) {
    console.error("Error al consultar SENAMHI:", error);
    throw new Error("No se pudo obtener información");
  }
};

const getDataByPeriod = async (
  station: Station,
  year: number,
  month: number,
  signal?: AbortSignal
): Promise<(MeteorologicalData | HydrologicalData)[]> => {
  try {
    // Preparar datos para form-urlencoded
    const period = `${year.toString()}${month.toString().padStart(2, "0")}`;
    const formData = qs.stringify({
      estaciones: station.code,
      CBOFiltro: period, // Ej: 202503
      t_e: station.stationType,
      estado: station.status,
      cod_old: station.codeOld,
    });

    // Llamar API de SENAMHI
    const { data: html } = await axios.post(
      config.apis.senamhiDataUrl,
      formData,
      {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        signal: signal,
      }
    );

    // Parseamos HTML
    const $ = cheerio.load(html);

    console.log(`Scraping SENAMHI: ${html}`);

    // Extraer datos diarios
    let dailyData: (MeteorologicalData | HydrologicalData)[] = [];

    let dataStartIndex = 1;
    if (station.status != "AUTOMATICA") {
      dataStartIndex = 2;
    }

    const rows = $("#dataTable tr");

    // Comprobar si hay datos
    if (rows.length === 0) {
      // Lanzar error si no hay datos
      throw new Error(
        `No se pudieron obtener datos para la estación ${station.name} en el periodo ${period}`
      );
    }

    rows.slice(dataStartIndex).each((_, row) => {
      const cols = $(row).find("td");
      const dateString = cols.eq(0).text().trim();
      const date = parseDateString(dateString);

      if (!date) throw new Error(`Formato de fecha inválido: ${dateString}`);

      // Define data mapping for different station configurations
      const dataConfigs = {
        'AUTOMATICA-M': {
          type: 'automatic' as const,
          fields: [
            { key: 'hour', index: 1, type: 'string' as const, default: '00:00' },
            { key: 'temp', index: 2, type: 'number' as const, default: 0.0 },
            { key: 'precipitation', index: 3, type: 'number' as const, default: 0.0 },
            { key: 'humidity', index: 4, type: 'number' as const, default: 0.0 },
            { key: 'windDirection', index: 5, type: 'number' as const, default: 0.0 },
            { key: 'windSpeed', index: 6, type: 'number' as const, default: 0.0 }
          ]
        },
        'AUTOMATICA-H': {
          type: 'automatic' as const,
          fields: [
            { key: 'hour', index: 1, type: 'string' as const, default: '00:00' },
            { key: 'riverLevel', index: 2, type: 'number' as const, default: 0.0 },
            { key: 'precipitation', index: 3, type: 'number' as const, default: 0.0 }
          ]
        },
        'CONVENCIONAL-M': {
          type: 'conventional' as const,
          fields: [
            { key: 'tempMax', index: 1, type: 'number' as const, default: 0.0 },
            { key: 'tempMin', index: 2, type: 'number' as const, default: 0.0 },
            { key: 'humidity', index: 3, type: 'number' as const, default: 0.0 },
            { key: 'precipitation', index: 4, type: 'number' as const, default: 0.0 }
          ]
        },
        'CONVENCIONAL-H': {
          type: 'conventional' as const,
          fields: [
            { key: 'riverlevel06', index: 1, type: 'number' as const, default: 0.0 },
            { key: 'riverlevel10', index: 2, type: 'number' as const, default: 0.0 },
            { key: 'riverlevel14', index: 3, type: 'number' as const, default: 0.0 },
            { key: 'riverlevel18', index: 4, type: 'number' as const, default: 0.0 }
          ]
        }
      };

      // Determine configuration key
      const statusKey = station.status === "AUTOMATICA" ? "AUTOMATICA" : "CONVENCIONAL";
      const configKey = `${statusKey}-${station.stationType}`;
      const config = dataConfigs[configKey as keyof typeof dataConfigs];

      if (!config) {
        throw new Error(`Configuración no encontrada para: ${configKey}`);
      }

      // Build data object dynamically
      const dataPoint: any = {
        type: config.type,
        year: date.year,
        month: date.month,
        day: date.day
      };

      // Extract field values based on configuration
      config.fields.forEach(field => {
        const cellText = cols.eq(field.index).text().trim();
        dataPoint[field.key] = field.type === 'number' 
          ? (parseFloat(cellText) || field.default)
          : (cellText || field.default);
      });

      dailyData.push(dataPoint);
    });
    console.log(
      `Se ha realizado consulta Estación: ${station.name}, Periodo: ${period}`
    );
    return dailyData;
  } catch (err) {
    // Cancelación explícita
    if (axios.isCancel(err)) {
      console.warn(`Petición cancelada: ${station.name} ${year}-${month}`);
      return [];
    }

    // Error de Axios (timeout, 500, etc.)
    if (axios.isAxiosError(err)) {
      console.error("Error Axios scraping:", {
        message: err.message,
        code: err.code,
        status: err.response?.status,
      });
      throw new Error(
        `Fallo al obtener datos del SENAMHI: ${
          err.response?.status ?? "desconocido"
        }`
      );
    }

    // Error inesperado
    if (err instanceof Error) {
      console.error("Error inesperado en scraping:", err.message);
      throw err;
    }

    // Fallback por si es un error no conocido
    console.error("Error desconocido en scraping:", err);
    throw new Error("Error desconocido en scraping");
  }
};

const getDataByYear = async (
  station: Station,
  year: number,
  signal?: AbortSignal
) => {
  try {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    // Si el año es el actual, solo hasta el mes actual
    const months =
      year === currentYear
        ? Array.from({ length: currentMonth }, (_, i) => i + 1)
        : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    let data: (MeteorologicalData | HydrologicalData)[] = [];
    for (const month of months) {
      if (signal?.aborted) break;
      const dataMonth = await getDataByPeriod(station, year, month, signal);
      data = [...data, ...dataMonth];
      await sleep(400);
    }
    return data;
  } catch (error) {
    console.error("Error al consultar SENAMHI:", error);
    throw error;
  }
};

const getDataByYearRange = async (
  station: Station,
  startYear: number,
  endYear: number,
  modeCache: boolean = false,
  signal?: AbortSignal
) => {
  let result: (MeteorologicalData | HydrologicalData)[] = [];
  for (let year = startYear; year <= endYear; year++) {
    if (signal?.aborted) break;
    const yearData = await getDataByYearCache(station, year, modeCache, signal);
    const checkData = yearData ?? [];
    result = [...result, ...checkData];
  }
  return result;
};

export default {
  getStationInfo,
  getStationData,
  getDataByPeriod,
  getDataByYear,
  getDataByYearRange,
};
