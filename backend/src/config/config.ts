import dotenv  from "dotenv";

// Configurar dotenv
dotenv.config();

const config = {
    // Configuración del servidor
    server: {
        port: process.env.PORT || 3000,
        host: process.env.HOST || 'localhost',
        env: process.env.NODE_ENV || 'development'
    },

    // Configuración de apis
    apis: {
        senamhiDataUrl: process.env.SENAMHI_DATA_URL || '',
        senamhiStationUrl: process.env.SENAMHI_STATION_URL || ''
    },

    // Configuración de CORS
    cors: {
        origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
        credentials: process.env.CORS_CREDENTIALS === 'true' || false
    }
}

export default config;