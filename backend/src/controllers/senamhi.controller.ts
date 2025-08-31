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
import {
  MET_AUTOMATIC_HEADERS,
  MET_CONVENTIONAL_HEADERS,
  MeteorologicalData,
  MeteorologicalDataResponse,
  Station,
} from "../types/station";

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
    const response: MeteorologicalDataResponse[] = data.map((row) => {
      const { type, ...rest } = row;
      return rest;
    });

    if (format === "csv") {
      const headers =
        station.status === "AUTOMATICA"
          ? MET_AUTOMATIC_HEADERS
          : MET_CONVENTIONAL_HEADERS;
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
    });

    if (format === "csv") {
      const cached = await getDataByYearCache(station, year, true);

      res.setHeader("Content-Type", "text/csv");
      res.setHeader(
        "Content-Disposition",
        `attachment; filename="${station.name}_${station.code}_${year}.csv"`
      );

      // Header CSV
      const headers =
        station.status === "AUTOMATICA"
          ? MET_AUTOMATIC_HEADERS
          : MET_CONVENTIONAL_HEADERS;
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
      const data: MeteorologicalDataResponse[] | null =
        await getDataByYearCache(station, year, false, controller.signal);
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
    });

    if (format === "csv") {
      await _handleCsvYearRangeResponse(res, station, startYear, endYear, controller);
    } else {
      const data: MeteorologicalDataResponse[] | null =
        await senamhiService.getDataByYearRange(
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
  const headers =
    station.status === "AUTOMATICA"
      ? MET_AUTOMATIC_HEADERS
      : MET_CONVENTIONAL_HEADERS;
  res.write(`${headers.join(",")}\n`);

  // Procesar año por año
  for (let year = startYear; year <= endYear; year++) {
    if (controller.signal.aborted) break;
    const cached = await getDataByYearCache(
      station,
      year,
      true
    );
    if (cached) {
      _writeCsvData(cached, res);
    } else {
      await _processYearDataToCsv(station, year, res, controller.signal);
    }
  }

  // Finalizar respuesta
  if (!controller.signal.aborted) res.end();
}

// Formatea una fila de datos a CSV
function _formatRowToCsv(row: MeteorologicalData): string {
  if (row.type === "conventional") {
    return `${row.year},${row.month},${row.day},${row.tempMax},${row.tempMin},${row.humidity},${row.precipitation}`;
  } else {
    return `${row.year},${row.month},${row.day},${row.hour},${row.temp},${row.precipitation},${row.humidity},${row.windDirection},${row.windSpeed}`;
  }
}

// Escribe los datos en formato CSV
function _writeCsvData(data: MeteorologicalData[], res: Response) {
  data.forEach((row) => {
    const csvRow = _formatRowToCsv(row);
    res.write(`${csvRow}\n`);
  });
}

// Maneja errores durante el streaming de datos
function handleStreamError(err: unknown, year: number, res: Response) {
  if (!res.headersSent) {
    res.status(500).json({
      error: `No se pudo completar la descarga de datos del año ${year}.`,
      details: (err as Error).message,
    });
  } else {
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
  const yearData: MeteorologicalDataResponse[] = [];

  for (let month = 1; month <= 12; month++) {
    try {
      if (signal?.aborted) break;
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
      handleStreamError(err, year, res);
      return;
    }
  }

  // Guardar en caché después de procesar
  if (!signal?.aborted) await saveDataByYearCache(station, year, yearData);
}
