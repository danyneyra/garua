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
