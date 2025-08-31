import { Router } from "express";
import { getStations, getStationByCode, searchStations } from "../controllers/stations.controller";

const router = Router();

// Filtro por query params (nombre o código)
router.get("/", getStations);

// Búsqueda
router.get("/search", searchStations)

// Búsqueda directa por código (ruta dinámica)
router.get("/:cod", getStationByCode);



export default router;
