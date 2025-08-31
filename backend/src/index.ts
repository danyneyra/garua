import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import stationsRoutes from "./routes/stations.routes";
import senamhiRoutes from "./routes/senamhi.routes";
import config from "./config/config";

dotenv.config();
const app = express();

// Configurar CORS usando variables de entorno
console.log("CORS Origin:", config.cors.origin.split(','));
const corsOptions = {
  origin: config.cors.origin.split(','),
  credentials: config.cors.credentials,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));
app.use(express.json());

// Rutas
app.use("/api/estaciones", stationsRoutes);
app.use("/api/senamhi", senamhiRoutes);

const PORT = config.server.port || 4000;
app.listen(PORT, () => {
  console.log(`🚀 Backend listening on http://localhost:${PORT}`);
});
