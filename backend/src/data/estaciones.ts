import path from "path";
import fs from "fs";
import { Station } from "../types/station/station";

const filePath = path.join(__dirname, "../../data/estaciones.json");
const estaciones: Station[] = JSON.parse(fs.readFileSync(filePath, "utf8"));

export default estaciones;