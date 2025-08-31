import { api } from "@/api/api";
import { Station } from "@/types/station";
import { useMutation } from "@tanstack/react-query";

async function fetchStation(code: string) {
  const { data } = await api.get(`/senamhi/${code}`);
  return data;
}

export function useStation() {
  return useMutation<Station, Error, string>({
    mutationFn: fetchStation,
  });
}