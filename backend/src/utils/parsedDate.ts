type ParsedDate = {
  year: number;
  month: number;
  day: number;
  date: Date;
};

export function parseDateString(input: string): ParsedDate | null {
  const parts = input.trim().split(/[-/]/).map(Number);

  if (parts.length !== 3 || parts.some(isNaN)) {
    return null;
  }

  let year: number, month: number, day: number;

  if (parts[0] > 31) {
    // Caso: YYYY-MM-DD o YYYY/MM/DD
    [year, month, day] = parts;
  } else if (parts[2] > 31) {
    // Caso: DD/MM/YYYY
    [day, month, year] = parts;
  } else {
    // Ambiguo → asumimos formato DD/MM/YYYY
    [day, month, year] = parts;
  }

  // Validar fecha
  const date = new Date(year, month - 1, day);
  if (
    date.getFullYear() !== year ||
    date.getMonth() + 1 !== month ||
    date.getDate() !== day
  ) {
    return null; // Fecha inválida (ej: 31/02/2024)
  }

  return { year, month, day, date };
}