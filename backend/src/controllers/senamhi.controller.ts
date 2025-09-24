import { Request, Response } from "express";
import { findStationByCode } from "../services/stations.service";
import senamhiService from "../services/senamhi.service";
import {
  getDataByPeriodCache,
  getDataByYearCache,
  saveDataByYearCache,
} from "./cache.controller";
import { PeriodParams, RangeYearsParams, YearParams } from "../types/request";
import { jsonToCsv } from "../utils/convert";
import { Station } from "../types/station/station";
import {
  MET_AUTOMATIC_HEADERS,
  MET_CONVENTIONAL_HEADERS,
  MeteorologicalData,
  MeteorologicalDataResponse,
} from "../types/station/meteorologicalStation";
import {
  HYD_AUTOMATIC_HEADERS,
  HYD_CONVENTIONAL_HEADERS,
  HydrologicalData,
  HydrologicalDataResponse,
} from "../types/station/hydrologicalStation";

export async function getSationData(req: Request, res: Response) {
  const { cod } = req.params;

  // Buscar estación
  const station = findStationByCode(cod);
  if (!station) {
    return res.status(404).json({ error: "Estación no encontrada" });
  }

  try {
    const dataSation = await senamhiService.getStationInfo(station);
    return res.json(dataSation);
  } catch (error) {
    console.error("Error al obtener información de la estación:", error);
    return res
      .status(500)
      .json({ error: "Error al obtener información de la estación" });
  }
}

export async function getDataByPeriod(req: Request, res: Response) {
  try {
    const { cod, year, month } = req.params as unknown as PeriodParams;
    const format = (req.query.format as string) || "json";

    // Buscar estación
    const station = findStationByCode(cod);
    if (!station) {
      return res.status(404).json({ error: "Estación no encontrada" });
    }

    // Realizando consulta
    const data = await getDataByPeriodCache(station, year, month);
    const response: (MeteorologicalDataResponse | HydrologicalDataResponse)[] =
      data.map((row) => {
        const { type, ...rest } = row;
        return rest;
      });

    if (format === "csv") {
      let headers;
      if (station.status === "AUTOMATICA") {
        headers =
          station.stationType === "M"
            ? MET_AUTOMATIC_HEADERS
            : HYD_AUTOMATIC_HEADERS;
      } else {
        headers =
          station.stationType === "M"
            ? MET_CONVENTIONAL_HEADERS
            : HYD_CONVENTIONAL_HEADERS;
      }
      const csv = jsonToCsv(response, headers);
      res.header("Content-Type", "text/csv");
      res.attachment(
        `${station.name.trim()}_${station.code}_${year}_${month}.csv`
      );
      res.send(csv);
    } else {
      res.json(response);
    }
  } catch (error) {
    console.error("Error obteniendo datos por periodo: ", error);
    let errorMessage = "Error obteniendo datos por periodo";
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    res.status(500).json({ error: errorMessage });
  }
}

export async function getDataByYear(req: Request, res: Response) {
  try {
    const { cod, year } = req.params as unknown as YearParams;
    const format = (req.query.format as string) || "json";

    // Buscar estación
    const station = findStationByCode(cod);
    if (!station) {
      return res.status(404).json({ error: "Estación no encontrada" });
    }

    // Manejar cancelación por parte del cliente
    const controller = new AbortController();
    req.on("close", () => {
      controller.abort();
      console.log(`Cliente desconectado durante descarga de datos del año ${year} para estación ${station.code}`);
    });

    if (format === "csv") {
      const cached = await getDataByYearCache(station, year, true);

      res.setHeader("Content-Type", "text/csv");
      res.setHeader(
        "Content-Disposition",
        `attachment; filename="${station.name}_${station.code}_${year}.csv"`
      );

      // Header CSV
      let headers;
      if (station.status === "AUTOMATICA") {
        headers =
          station.stationType === "M"
            ? MET_AUTOMATIC_HEADERS
            : HYD_AUTOMATIC_HEADERS;
      } else {
        headers =
          station.stationType === "M"
            ? MET_CONVENTIONAL_HEADERS
            : HYD_CONVENTIONAL_HEADERS;
      }
      res.write(`${headers.join(",")}\n`);

      // Comprobar año en cache
      if (cached) {
        _writeCsvData(cached, res);
        return res.end();
      }

      await _processYearDataToCsv(station, year, res, controller.signal);
      // Finalizar respuesta
      if (!controller.signal.aborted) res.end();
    } else {
      const data:
        | (MeteorologicalDataResponse | HydrologicalDataResponse)[]
        | null = await getDataByYearCache(
        station,
        year,
        false,
        controller.signal
      );
      res.json(data);
    }
  } catch (error) {
    console.error("Error obteniendo datos por año: ", error);
    let errorMessage = "Error obteniendo datos por periodo";
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    res.status(500).json({ error: errorMessage });
  }
}

export async function getDataByYearRange(req: Request, res: Response) {
  try {
    const { cod, startYear, endYear } =
      req.params as unknown as RangeYearsParams;
    const format = (req.query.format as string) || "json";

    // Validar años
    if (startYear >= endYear) throw new Error("El rango de años es inválido");

    // Buscar estación
    const station = findStationByCode(cod);
    if (!station) {
      return res.status(404).json({ error: "Estación no encontrada" });
    }

    // Manejar cancelación por parte del cliente
    const controller = new AbortController();
    req.on("close", () => {
      controller.abort();
      console.log(`Cliente desconectado durante descarga de rango ${startYear}-${endYear} para estación ${station.code}`);
    });

    if (format === "csv") {
      await _handleCsvYearRangeResponse(
        res,
        station,
        startYear,
        endYear,
        controller
      );
    } else {
      const data:
        | (MeteorologicalDataResponse | HydrologicalDataResponse)[]
        | null = await senamhiService.getDataByYearRange(
        station,
        startYear,
        endYear,
        false,
        controller.signal
      );
      res.json(data);
    }
  } catch (error) {
    console.error("Error obteniendo datos por rango de años: ", error);
    let errorMessage = "Error obteniendo datos por rango de años";
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    res.status(500).json({ error: errorMessage });
  }
}

// Response en CSV para rango de años
async function _handleCsvYearRangeResponse(
  res: Response,
  station: Station,
  startYear: number,
  endYear: number,
  controller: AbortController
) {
  res.setHeader("Content-Type", "text/csv");
  res.setHeader(
    "Content-Disposition",
    `attachment; filename="${station.name}_${station.code}_${startYear}-${endYear}.csv"`
  );

  // Header CSV
  let headers;
  if (station.status === "AUTOMATICA") {
    headers =
      station.stationType === "M"
        ? MET_AUTOMATIC_HEADERS
        : HYD_AUTOMATIC_HEADERS;
  } else {
    headers =
      station.stationType === "M"
        ? MET_CONVENTIONAL_HEADERS
        : HYD_CONVENTIONAL_HEADERS;
  }
  res.write(`${headers.join(",")}\n`);

  // Procesar año por año
  for (let year = startYear; year <= endYear; year++) {
    try {
      if (controller.signal.aborted) {
        // Escribir mensaje de cancelación en el archivo CSV
        const cancelMessage = `\n# CANCELADO: Descarga interrumpida por el usuario en el año ${year}`;
        const timestampLine = `\n# TIMESTAMP: ${new Date().toISOString()}`;
        res.write(cancelMessage);
        res.write(timestampLine);
        break;
      }
      
      const cached = await getDataByYearCache(station, year, true);
      if (cached) {
        _writeCsvData(cached, res);
      } else {
        await _processYearDataToCsv(station, year, res, controller.signal);
      }
    } catch (err) {
      console.error(`Error procesando año ${year}:`, err);
      handleStreamError(err, year, res);
      return;
    }
  }

  // Finalizar respuesta
  if (!controller.signal.aborted) res.end();
}

// Formatea una fila de datos a CSV
function _formatRowToCsv(row: (MeteorologicalData | HydrologicalData)): string {
  const baseData = `${row.year},${row.month},${row.day}`;
  
  // Detect station type by checking specific properties
  const isMeteorologicalConventional = 'tempMax' in row && 'tempMin' in row;
  const isMeteorologicalAutomatic = 'temp' in row && 'windDirection' in row && 'windSpeed' in row;
  const isHydrologicalConventional = 'riverlevel06' in row && 'riverlevel10' in row && 'riverlevel14' in row && 'riverlevel18' in row;
  const isHydrologicalAutomatic = 'riverLevel' in row && !('riverlevel06' in row);

  if (isMeteorologicalConventional) {
    // Meteorological Conventional
    const data = row as any;
    return `${baseData},${data.tempMax ?? ''},${data.tempMin ?? ''},${data.humidity ?? ''},${data.precipitation ?? ''}`;
  } 
  else if (isMeteorologicalAutomatic) {
    // Meteorological Automatic  
    const data = row as any;
    return `${baseData},${data.hour ?? ''},${data.temp ?? ''},${data.precipitation ?? ''},${data.humidity ?? ''},${data.windDirection ?? ''},${data.windSpeed ?? ''}`;
  }
  else if (isHydrologicalConventional) {
    // Hydrological Conventional
    const data = row as any;
    return `${baseData},${data.riverlevel06 ?? ''},${data.riverlevel10 ?? ''},${data.riverlevel14 ?? ''},${data.riverlevel18 ?? ''}`;
  }
  else if (isHydrologicalAutomatic) {
    // Hydrological Automatic
    const data = row as any;
    return `${baseData},${data.hour ?? ''},${data.riverLevel ?? ''},${data.precipitation ?? ''}`;
  }
  
  // Fallback (shouldn't happen with proper data)
  throw new Error(`Tipo de estación no reconocido para los datos: ${JSON.stringify(row)}`);
}

// Escribe los datos en formato CSV
function _writeCsvData(data: (MeteorologicalData | HydrologicalData)[], res: Response) {
  data.forEach((row) => {
    const csvRow = _formatRowToCsv(row);
    res.write(`${csvRow}\n`);
  });
}

// Maneja errores durante el streaming de datos
function handleStreamError(err: unknown, year: number, res: Response, month?: number) {
  const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
  const monthInfo = month ? ` mes ${month}` : '';
  
  if (!res.headersSent) {
    res.status(500).json({
      error: `No se pudo completar la descarga de datos del año ${year}.`,
      details: errorMessage,
    });
  } else {
    // Escribir error directamente en el archivo CSV que se está enviando
    const errorLine = `\n# ERROR: No se pudieron obtener datos del año ${year}${monthInfo}`;
    const detailsLine = `\n# DETALLES: ${errorMessage}`;
    const timestampLine = `\n# TIMESTAMP: ${new Date().toISOString()}`;
    
    try {
      res.write(errorLine);
      res.write(detailsLine);
      res.write(timestampLine);
      res.write('\n# La descarga se interrumpió debido al error anterior.\n');
    } catch (writeError) {
      console.error('Error escribiendo mensaje de error al stream:', writeError);
    }
    
    res.end();
  }
}

// Procesa los datos del año y los escribe al CSV
async function _processYearDataToCsv(
  station: Station,
  year: number,
  res: Response,
  signal?: AbortSignal
) {
  const yearData: (MeteorologicalDataResponse | HydrologicalDataResponse)[] = [];

  for (let month = 1; month <= 12; month++) {
    try {
      if (signal?.aborted) {
        // Escribir mensaje de cancelación en el archivo CSV
        const cancelMessage = `\n# CANCELADO: Descarga interrumpida por el usuario`;
        const timestampLine = `\n# TIMESTAMP: ${new Date().toISOString()}`;
        res.write(cancelMessage);
        res.write(timestampLine);
        break;
      }
      
      const monthData = await senamhiService.getDataByPeriod(
        station,
        year,
        month,
        signal
      );

      _writeCsvData(monthData, res);
      yearData.push(...monthData);
    } catch (err) {
      console.error(`Error al obtener datos de ${year}/${month}:`, err);
      handleStreamError(err, year, res, month);
      return;
    }
  }

  // Guardar en caché después de procesar
  if (!signal?.aborted) await saveDataByYearCache(station, year, yearData);
}
