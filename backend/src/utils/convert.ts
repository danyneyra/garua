/**
 * Convierte un array de objetos JSON a CSV.
 * @param jsonArray Array de objetos.
 * @param headers Encabezados del CSV (opcional, en el mismo orden que las claves del objeto).
 * Si no se pasan headers, se usan los keys del primer objeto.
 * @param withHeaders Incluir encabezados o no, por defecto sí
 */
export function jsonToCsv(jsonArray: any[], headers?: string[], withHeaders = true): string {
  if (!Array.isArray(jsonArray) || jsonArray.length === 0) return "";
  
  const csvRows: string[] = [];
  const keys = Object.keys(jsonArray[0]);

  if (withHeaders) {
    const csvHeaders = headers ?? keys;
    // Cabeceras
    csvRows.push(csvHeaders.join(","));
  }
  

  // Filas
  for (const obj of jsonArray) {
    const values = keys.map((key) => {
      let val = obj[key];
      if (val === null || val === undefined) return "";
      if (typeof val === "string") {
        return `"${val.replace(/"/g, '""')}"`;
      }
      return String(val);
    });
    csvRows.push(values.join(","));
  }

  return csvRows.join("\n");
}