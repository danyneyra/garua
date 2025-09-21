import cache from "../config/cache";
import {
  Station,
} from "../types/station/station";
import senamhiService from "../services/senamhi.service";
import { MeteorologicalData, MeteorologicalDataResponse } from "../types/station/meteorologicalStation";
import { HydrologicalData, HydrologicalDataResponse } from "../types/station/hydrologicalStation";

export async function saveDataByYearCache(
  station: Station,
  year: number,
  data: (MeteorologicalDataResponse | HydrologicalDataResponse)[]
) {
  // Crear key
  const key = `${station.code}_${year}`;
  // Alamacena en caché
  cache.set(key, data);
}

export async function getDataByPeriodCache(
  station: Station,
  year: number,
  month: number
) {
  // Crear key
  const key = `${station.code}_${year}${month}`;

  // Revisar información en caché
  const dataCache = cache.get<(MeteorologicalData | HydrologicalData)[]>(key);
  if (dataCache) {
    console.log(`[CACHE] hit: ${key}`);
    return dataCache;
  } else {
    // Realizar consulta a api Senamhi
    console.log(`[CACHE] miss: ${key}, fetching from API...`);
    const data = await senamhiService.getDataByPeriod(station, year, month);
    // Alamacena en caché
    cache.set(key, data);
    return data;
  }
}

export async function getDataByYearCache(
  station: Station,
  year: number,
  modeCache: boolean = false,
  signal?: AbortSignal
) {
  // Crear key
  const key = `${station.code}_${year}`;

  // Revisar información en caché
  const dataCache = cache.get<(MeteorologicalData | HydrologicalData)[]>(key);
  if (dataCache) {
    console.log(`[CACHE] hit: ${key}`);
    return dataCache;
  } else {
    // Comprobar si solo se pide obtener cache
    if (modeCache) return null;

    // Realizar consulta a api Senamhi
    console.log(`[CACHE] miss: ${key}, fetching from API...`);
    const data = await senamhiService.getDataByYear(station, year, signal);
    // Alamacena en caché
    if (!signal?.aborted) cache.set(key, data);
    return data;
  }
}
