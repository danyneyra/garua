import { Input } from "@heroui/input";
import { Listbox, ListboxItem } from "@heroui/listbox";
import { Tabs, Tab } from "@heroui/tabs";
import { useMemo, useRef, useState } from "react";

import { SearchIcon, WeatherIcon } from "@/components/icons";
import DefaultLayout from "@/layouts/default";
import { useDebouncedSearch } from "@/features/search/hooks/useSearch";
import { Station, StationDataYears } from "@/types/station";
import { useStation } from "@/features/search/hooks/useStation";
import { ObjectGeneric } from "@/types/object";
import FormPeriodDownload from "@/pages/Forms/FormPeriodDownload";
import FormYearDownload from "./Forms/FormYearDownload";
import FormRangeDownload from "./Forms/FormRangeDownload";
import BirdCrazy from "@/lotties/birdCrazy";
import MiniMap from "@/components/map";

export default function IndexPage() {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [stationQuery, setStationQuery] = useState<Station>();
  const inputRef = useRef<HTMLInputElement | null>(null);

  const { data, isLoading } = useDebouncedSearch(query);

  // Mutaciones
  const {
    mutateAsync: fetchStation,
    error: errorFetchStation,
    isPending,
  } = useStation();

  const handleSelect = async (key: React.Key) => {
    const value = key.toString();
    console.log("Selected: ", value);
    setOpen(false);

    // Consultar estación
    try {
      const dataStation = await fetchStation(value);
      setStationQuery(dataStation);
    } catch (error) {
      console.error("No se pudo consultar estación", error);
    }
  };

  // Detectar años disponibles
  const years: StationDataYears = useMemo(() => {
    const yearNow = new Date().getFullYear();
    const yearNowStr = yearNow.toString();
    let yearsAvalibles: ObjectGeneric[] = [];

    if (!stationQuery?.dataAvailableSince) {
      yearsAvalibles.push({ key: yearNowStr, name: yearNowStr });
      return {
        yearStart: yearNowStr,
        yearEnd: yearNowStr,
        avalibles: yearsAvalibles,
      };
    }

    for (
      let index = stationQuery.dataAvailableSince;
      index <= yearNow;
      index++
    ) {
      yearsAvalibles.push({
        key: index.toString(),
        name: index.toString(),
      });
    }
    return {
      yearStart: yearsAvalibles[0].name,
      yearEnd: yearsAvalibles[yearsAvalibles.length - 1].name,
      avalibles: yearsAvalibles,
    };
  }, [stationQuery]);

  return (
    <DefaultLayout>
      <section className="w-full md:min-w-2xl flex justify-center">
        <div className="flex flex-col gap-4 items-center justify-center md:max-w-2xl text-center">
          <h1 className="text-4xl font-bold">
            Descarga datos meteorológicos oficiales del SENAMHI sin
            complicaciones
          </h1>
          <p className="px-6 md:px-0 text-foreground-500">
            Descarga información oficial del SENAMHI en un solo archivo, por año
            o rangos de años, de cualquier estación metereólogica.
          </p>
        </div>
      </section>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="relative w-full md:max-w-2xl items-center justify-center">
          <Input
            ref={inputRef}
            autoComplete="off"
            className="w-full md:min-w-2xl"
            label="Buscar estación"
            radius="full"
            startContent={<SearchIcon />}
            value={query}
            variant="bordered"
            onValueChange={(val) => {
              setQuery(val);
              setOpen(val.length > 0);
            }}
          />
          {open && !isLoading && data && (
            <div className="absolute z-50 mt-1 w-full md:min-w-2xl rounded-xl border border-foreground-300 shadow-lg bg-white dark:bg-default">
              <Listbox
                aria-label="Sugerencias de búsqueda"
                selectionMode="single"
                onAction={handleSelect}
                emptyContent="No hay resultados"
              >
                {data?.results?.map((item) => (
                  <ListboxItem key={item.code} textValue={item.name}>
                    {item.name} - {item.code}
                  </ListboxItem>
                ))}
              </Listbox>
            </div>
          )}
        </div>
        {isPending && (
          <div className="flex flex-col items-center justify-center gap-2">
            <BirdCrazy />
          </div>
        )}

        {!errorFetchStation && stationQuery && !isPending && (
          <>
            <div className="flex flex-col w-full min-w-[320px] md:max-w-2xl gap-1 items-start py-3 px-6 md:px-4 rounded-b-[3rem] rounded-t-2xl bg-gradient-to-tr from-[#b3c1fa] to-[#6a7cce] opacity-90">
              <div className="flex flex-col gap-4 md:flex-row w-full md:justify-around items-start">
                <div className="flex flex-col gap-1 pt-2">
                  <WeatherIcon />
                  <div className="bg-[#6a7cce] flex rounded-full w-fit items-center text-center text-[0.75em] text-white px-2 py-1 gap-1">
                    <span className="font-semibold">
                      {stationQuery.status === "AUTOMATICA"
                        ? "Automática"
                        : "Convencional"}
                    </span>
                  </div>
                  <div className="flex flex-col dark:text-black">
                    <div className="flex w-full gap-2 items-center">
                      <h2 className="font-bold">{stationQuery.name}</h2>

                      <span className="text-[0.85em] text-black-500">
                        {stationQuery.code}
                      </span>
                    </div>
                    <span className="text-[0.75em]">
                      {stationQuery.department} / {stationQuery.province} /{" "}
                      {stationQuery.district}
                    </span>
                    <div className="flex gap-2 text-[0.8em]">
                      <span>Lat: {stationQuery.latitude}</span>
                      <span>Lon: {stationQuery.longitude}</span>
                    </div>
                    <div className="flex gap-2 text-[0.8em]">
                      <span>Altitud: {stationQuery.altitude} msnm</span>
                    </div>
                  </div>
                </div>
                <MiniMap
                  latitude={stationQuery.latitude}
                  longitude={stationQuery.longitude}
                  markerText={stationQuery.name}
                />
              </div>
            </div>
            <div className="flex w-full flex-col md:max-w-2xl px-2 md:px-6">
              <Tabs
                aria-label="Seleccionar período de datos"
                variant="solid"
                color="warning"
                radius="full"
                classNames={{
                  base: "justify-around",
                  cursor: "bg-[#6a7cce]",
                  tab: "bg-[#dbe0f2] hover:bg-[#ccd7ff]",
                  tabList: "gap-6 bg-transparent mb-3",
                  tabContent:
                    "group-data-[selected=true]:text-white text-black",
                }}
              >
                <Tab key="period" title="Período">
                  <FormPeriodDownload
                    nameStation={stationQuery.name}
                    codeStation={stationQuery.code}
                    years={years}
                  />
                </Tab>
                <Tab key="year" title="Año">
                  <FormYearDownload
                    codeStation={stationQuery.code}
                    years={years}
                  />
                </Tab>
                <Tab key="range" title="Rango de años">
                  <FormRangeDownload
                    codeStation={stationQuery.code}
                    years={years}
                  />
                </Tab>
              </Tabs>
            </div>
          </>
        )}
      </section>
    </DefaultLayout>
  );
}
