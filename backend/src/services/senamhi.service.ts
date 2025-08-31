import axios from "axios";
import * as cheerio from "cheerio";
import qs from "qs"; // para serializar form-urlencoded
import { Station, MeteorologicalData } from "../types/station";
import { sleep } from "../utils/sleep";
import { getDataByYearCache } from "../controllers/cache.controller";
import { parseDateString } from "../utils/parsedDate";
import config from "../config/config";
import { concatenateUrlWithParams } from "../utils/url";

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
      t_e: "M",
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
): Promise<MeteorologicalData[]> => {
  try {
    // Preparar datos para form-urlencoded
    const period = `${year.toString()}${month.toString().padStart(2, "0")}`;
    const formData = qs.stringify({
      estaciones: station.code,
      CBOFiltro: period, // Ej: 202503
      t_e: "M",
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

    // Extraer datos diarios
    let dailyData: MeteorologicalData[] = [];

    let dataStartIndex = 1;
    if (station.status != "AUTOMATICA") {
      dataStartIndex = 2;
    }

    const rows = $("#dataTable tr");

    rows.slice(dataStartIndex).each((_, row) => {
      const cols = $(row).find("td");
      const dateString = cols.eq(0).text().trim();
      const date = parseDateString(dateString);

      if (!date) throw new Error(`Formato de fecha inválido: ${dateString}`);

      if (station.status === "AUTOMATICA") {
        dailyData.push({
          type: "automatic",
          year: date.year,
          month: date.month,
          day: date.day,
          hour: cols.eq(1).text().trim() || "00:00",
          temp: parseFloat(cols.eq(2).text().trim()) || 0.0,
          precipitation: parseFloat(cols.eq(3).text().trim()) || 0.0,
          humidity: parseFloat(cols.eq(4).text().trim()) || 0.0,
          windDirection: parseFloat(cols.eq(5).text().trim()) || 0.0,
          windSpeed: parseFloat(cols.eq(6).text().trim()) || 0.0,
        });
      } else {
        dailyData.push({
          type: "conventional",
          year: date.year,
          month: date.month,
          day: date.day,
          tempMax: parseFloat(cols.eq(1).text().trim()) || 0.0,
          tempMin: parseFloat(cols.eq(2).text().trim()) || 0.0,
          humidity: parseFloat(cols.eq(3).text().trim()) || 0.0,
          precipitation: parseFloat(cols.eq(4).text().trim()) || 0.0,
        });
      }
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
    let data: MeteorologicalData[] = [];
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
  let result: MeteorologicalData[] = [];
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
