import { Request, Response } from "express";
import {
  getAllStations,
  findStationByCode,
  searchStationsByName,
} from "../services/stations.service";

export const getStations = (req: Request, res: Response) => {
  const { cod, nom } = req.query;

  if (typeof cod === "string") {
    const station = findStationByCode(cod);
    return res.json(station ?? { error: "Station not found" });
  }

  if (typeof nom === "string") {
    return res.json(searchStationsByName(nom));
  }

  return res.json(getAllStations());
};

// Búsqueda directa por código usando rutas dinámicas
export const getStationByCode = (req: Request, res: Response) => {
  const { cod } = req.params;

  const station = findStationByCode(cod);

  if (!station) {
    return res.status(404).json({ error: "Station not found" });
  }

  return res.json(station);
};

// Búsqueda de estaciones
export const searchStations = (req: Request, res: Response) => {
  const q = req.query.q as string;

  console.log(q)

  const stations = searchStationsByName(q);

  return res.json({ results: stations });
};
