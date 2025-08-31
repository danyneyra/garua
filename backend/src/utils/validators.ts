import { param, query } from "express-validator";

// Validadores generales para routes
export const validateYear = () =>
  param("year")
    .isInt({ min: 1990, max: new Date().getFullYear() })
    .toInt()
    .withMessage("El año ingresado no es válido");

export const validateMonth = () =>
  param("month")
    .isInt({ min: 1, max: 12 })
    .toInt()
    .withMessage("El mes ingresado no es válido");

export const validateStartYear = () =>
  param("startYear")
    .isInt({ min: 1990, max: new Date().getFullYear() })
    .toInt()
    .withMessage("El año de inicio ingresado no es válido");

export const validateEndYear = () =>
  param("endYear")
    .isInt({ min: 1990, max: new Date().getFullYear() })
    .toInt()
    .withMessage("El año de finalzación ingresado no es válido");

export const validateFormat = () =>
  query("format")
  .optional()
  .isIn(["json", "csv"])
  .withMessage("El formato para exportar no es válido")
