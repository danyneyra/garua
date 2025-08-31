import { MONTHS } from "@/collections/dates";
import { downloadDataByPeriod } from "@/features/search/hooks/useDataDownload";
import { StationDataYears } from "@/types/station";
import { Button } from "@heroui/button";
import { Select, SelectItem } from "@heroui/select";
import { useState } from "react";

interface Props {
  readonly nameStation: string;
  readonly codeStation: string;
  readonly years: StationDataYears;
}

export default function FormPeriodDownload({
  nameStation,
  codeStation,
  years,
}: Props) {

  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    const formData = new FormData(event.currentTarget);
    const month = formData.get("month")?.toString() || "01";
    const year = formData.get("year")?.toString() || years.yearEnd;
    if (!codeStation) {
      alert("Por favor, seleccione una estación primero.");
      return;
    }
    try {
      await downloadDataByPeriod(nameStation, codeStation, year, month);
    } catch (error) {
      console.error("Error al descargar los datos:", error);
      alert(
        "Hubo un error al descargar los datos. Por favor, inténtelo de nuevo."
      );
    }finally {
      setIsLoading(false);
    }
  };
  return (
    <form aria-label="Descargar por período de año y mes" onSubmit={handleDownload} className="flex flex-col gap-3 px-3">
      <p className="text-[0.85em] font-semibold text-left">
        Descargar por período (mes/año):
      </p>
      <div className="w-full flex gap-2">
        <Select
          aria-label="Mes"
          name="month"
          items={MONTHS}
          defaultSelectedKeys={["01"]}
          disallowEmptySelection
          selectionMode="single"
        >
          {(item) => <SelectItem key={item.key}>{item.name}</SelectItem>}
        </Select>
        <Select
          aria-label="Año"
          name="year"
          items={years.avalibles}
          disallowEmptySelection
          defaultSelectedKeys={[years.yearEnd]}
          selectionMode="single"
        >
          {(item) => <SelectItem key={item.key}>{item.name}</SelectItem>}
        </Select>
      </div>
      <div className="w-full flex justify-center md:justify-end pt-2">
        <Button isLoading={isLoading} type="submit" radius="full" className="bg-[#6a7cce] text-white">
          Descargar CSV
        </Button>
      </div>
    </form>
  );
}
