import { api } from "@/api/api";
import { ResultsSearch } from "@/types/station";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

async function search(query: string) {
  const { data } = await api.get(`/estaciones/search`, {
    params: {
      q: query,
    },
  });
  return data;
}

export function useSearch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: search,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["search"] });
    },
  });
}

export function useDebouncedSearch(query: string, delay = 500) {
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  // Debounce
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
    }, delay);

    return () => clearTimeout(handler);
  }, [query, delay]);

  // Tansack query
  return useQuery<ResultsSearch>({
    queryKey: ["search", debouncedQuery],
    queryFn: () => search(debouncedQuery),
    enabled: !!debouncedQuery,
    refetchOnWindowFocus: false
  });
}
