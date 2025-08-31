import { apiURL } from "@/api/api";
import { StationDataYears } from "@/types/station";
import { Button } from "@heroui/button";
import { Select, SelectItem } from "@heroui/select";
import { useState } from "react";

interface Props {
  readonly codeStation: string;
  readonly years: StationDataYears;
}

export default function FormRangeDownload({ codeStation, years }: Props) {
  const [yearStartValue, setYearStartValue] = useState<string>(years.yearStart);
  const [yearEndValue, setYearEndValue] = useState<string>(years.yearEnd);

  const url = `${apiURL}/api/senamhi/${codeStation}/range/${yearStartValue}/${yearEndValue}`;

  const handleSelectionYearStartChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    setYearStartValue(e.target.value);
  };
  const handleSelectionYearEndChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    setYearEndValue(e.target.value);
  };

  return (
    <form
      aria-label="Descargar por rango de años"
      action={url}
      method="GET"
      target="_blank"
      className="flex flex-col gap-3 px-3"
    >
      <p className="text-[0.85em] font-semibold">
        Descargar por rango de años:
      </p>
      <div className="w-full flex gap-2">
        <input type="hidden" name="format" value="csv" />
        <Select
          aria-label="Año de inicio"
          name="yearStart"
          items={years.avalibles}
          selectedKeys={[yearStartValue]}
          disallowEmptySelection
          selectionMode="single"
          onChange={handleSelectionYearStartChange}
        >
          {(item) => <SelectItem key={item.key}>{item.name}</SelectItem>}
        </Select>
        <Select
          aria-label="Año de fin"
          name="yearEnd"
          items={years.avalibles}
          disallowEmptySelection
          selectedKeys={[yearEndValue]}
          selectionMode="single"
          onChange={handleSelectionYearEndChange}
        >
          {(item) => <SelectItem key={item.key}>{item.name}</SelectItem>}
        </Select>
      </div>
      <div className="w-full flex justify-center md:justify-end pt-2">
        <Button type="submit" radius="full" className="bg-[#6a7cce] text-white">
          Descargar CSV
        </Button>
      </div>
    </form>
  );
}
