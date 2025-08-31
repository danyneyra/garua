
/** Capitaliza solo la primera letra de una palabra */
export function capitalize(word: string): string {
  return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
}

/** Capitaliza todas las palabras de un texto */
export function capitalizeWords(text: string): string {
  return text
    .split(" ")
    .map(capitalize)
    .join(" ");
}
