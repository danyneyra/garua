import { Link } from "@heroui/link";
import { HeartFilledIcon } from "@/components/icons";
import { Navbar } from "@/components/navbar";

export default function DefaultLayout({
  children,
}: {
  readonly children: React.ReactNode;
}) {
  return (
    <div className="font-sans relative flex flex-col h-screen">
      <Navbar />
      <div className="w-full h-14 bg-red-400 top-0 left-0 items-center justify-center flex flex-col text-center">
        <p className="text-white">
          ⚠️ Servicio de descarga temporalmente no disponible.
        </p>
      </div>
      <main className="font-sans container mx-auto max-w-7xl px-6 flex-grow pt-4">
        {children}
      </main>
      <footer className="w-full flex flex-col items-center justify-center py-3 gap-3">
        <Link
          isExternal
          className="flex items-center gap-1 text-current"
          href="https://github.com/danyneyra"
          title="Garua"
        >
          <span className="text-default-600">Desarrollado con </span>
          <HeartFilledIcon className="text-[#6a7cce]" />
          <p className="text-[#6a7cce]">Dany Daniel</p>
        </Link>
        <p className="text-[0.7em] text-foreground-400 text-center">
          Garúa no es un servicio oficial del{" "}
          <a
            href="https://www.senamhi.gob.pe/?p=estaciones"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#6a7cce]"
          >SENAMHI</a>. Los datos provienen de consultas públicas en su portal.
        </p>
      </footer>
    </div>
  );
}
