import { api } from "@/api/api";

// Descargar datos por periodo año/mes
export async function downloadDataByPeriod(
  name: string,
  code: string,
  year: string,
  month: string,
  format?: string
) {
  const response = await api.get(`/senamhi/${code}/period/${year}/${month}`, {
    params: { format: format || "csv" },
    responseType: "blob",
  });

  // Crear un enlace para descargar el archivo
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${name}_${code}_${year}-${month}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Descargar datos por periodo año/mes
export async function downloadDataByYear(
  name: string,
  code: string,
  year: string,
  format?: string
) {
  // Realizar la solicitud a la API y capturar error si ocurre
  try {
    const response = await api.get(`/senamhi/${code}/year/${year}`, {
      params: { format: format || "csv" },
      responseType: "blob",
    });

    // Crear un enlace para descargar el archivo
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${name}_${code}_${year}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error("Error al descargar datos por año:", error);
    throw new Error("No se pudo descargar los datos");
  }
}

// Descargar datos por rango de años
export async function downloadDataByRange(
  name: string,
  code: string,
  yearStart: string,
  yearEnd: string,
  format?: string
) {
  const response = await api.get(
    `/senamhi/${code}/range/${yearStart}/${yearEnd}`,
    {
      params: { format: format || "csv" },
      responseType: "blob",
    }
  );

  // Crear un enlace para descargar el archivo
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${name}_${code}_${yearStart}-${yearEnd}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
