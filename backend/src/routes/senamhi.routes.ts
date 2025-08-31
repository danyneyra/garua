// src/routes/senamhiRoutes.ts
import { Router } from "express";
import {
  getDataByPeriod,
  getDataByYear,
  getDataByYearRange,
  getSationData,
} from "../controllers/senamhi.controller";
import {
  validateEndYear,
  validateFormat,
  validateMonth,
  validateStartYear,
  validateYear,
} from "../utils/validators";
import { validateRequest } from "../middlewares/validateRequest";

const router = Router();

router.get(
  "/:cod/period/:year/:month",
  validateYear(),
  validateMonth(),
  validateFormat(),
  validateRequest,
  getDataByPeriod
);

// Obtener datos por año completo
router.get("/:cod/year/:year", validateYear(), validateFormat(), validateRequest, getDataByYear);

// Obtener datos por rango de años
router.get(
  "/:cod/range/:startYear/:endYear",
  validateStartYear(),
  validateEndYear(),
  validateFormat(),
  validateRequest,
  getDataByYearRange
);

// Obtener información de estación
router.get("/:cod", getSationData);

export default router;
