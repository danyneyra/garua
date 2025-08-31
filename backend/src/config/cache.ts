import NodeCache from "node-cache"

const cache = new  NodeCache({
    stdTTL: 6 * 60 * 60, // 1 hora de almacenamiento de cache
    checkperiod: 60 * 10 // Limpieza de cache expirada
})

export default cache;