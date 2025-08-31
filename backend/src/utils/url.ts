/**
 * Convierte un objeto de parámetros a string de query
 * @param params - Objeto con los parámetros
 * @returns String de query (sin el '?' inicial)
 */
export function paramsToQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      if (Array.isArray(value)) {
        // Agregar múltiples valores para la misma clave
        value.forEach(v => searchParams.append(key, String(v)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  
  return searchParams.toString();
}

/**
 * Concatena una URL base con un objeto de parámetros
 * @param baseUrl - URL base
 * @param params - Objeto con los parámetros
 * @returns URL completa con parámetros
 */
export function concatenateUrlWithParams(baseUrl: string, params: Record<string, any>): string {
  if (!params || Object.keys(params).length === 0) {
    return baseUrl;
  }
  
  const queryString = paramsToQueryString(params);
  
  if (!queryString) {
    return baseUrl;
  }
  
  // Verificar si la URL ya tiene parámetros
  const separator = baseUrl.includes('?') ? '&' : '?';
  
  return `${baseUrl}${separator}${queryString}`;
}

/**
 * Versión más simple: agrega parámetros a una URL
 * @param url - URL base
 * @param params - Objeto de parámetros
 * @returns URL con parámetros concatenados
 */
export function addParamsToUrl(url: string, params: Record<string, any>): string {
  return concatenateUrlWithParams(url, params);
}
