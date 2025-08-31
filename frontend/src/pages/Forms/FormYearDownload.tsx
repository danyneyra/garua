import { apiURL } from "@/api/api";
import { StationDataYears } from "@/types/station";
import { Button } from "@heroui/button";
import { Select, SelectItem } from "@heroui/select";
import { useState } from "react";

interface Props {
  readonly codeStation: string;
  readonly years: StationDataYears;
}

export default function FormYearDownload({
  codeStation,
  years,
}: Props) {
  const [yearValue, setYearValue] = useState<string>(years.yearEnd);

  const url = `${apiURL}/api/senamhi/${codeStation}/year/${yearValue}`;

  const handleSelectionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setYearValue(e.target.value);
  };

  return (
    <form
      aria-label="Descargar por año"
      action={url}
      method="GET"
      target="_blank"
      className="flex flex-col gap-3 px-3"
    >
      <p className="text-[0.85em] font-semibold text-left">Descarga por año:</p>
      <input type="hidden" name="format" value="csv" />
      <div className="w-full flex gap-2">
        <Select
          aria-label="Año"
          items={years.avalibles}
          disallowEmptySelection
          selectedKeys={[yearValue]}
          selectionMode="single"
          className="w-full md:w-1/2"
          onChange={handleSelectionChange}
        >
          {(item) => <SelectItem key={item.key}>{item.name}</SelectItem>}
        </Select>
      </div>
      <div className="w-full flex justify-center pt-2">
        <Button type="submit" radius="full" className="bg-[#5D49F3] text-white">
          Descargar CSV
        </Button>
      </div>
    </form>
  );
}
