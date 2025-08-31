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
      <main className="font-sans container mx-auto max-w-7xl px-6 flex-grow pt-12">
        {children}
      </main>
      <footer className="w-full flex items-center justify-center py-3">
        <Link
          isExternal
          className="flex items-center gap-1 text-current"
          href="https://github.com/danyneyra/"
          title="Garua"
        >
          <span className="text-default-600">Desarrollado con </span>
          <HeartFilledIcon className="text-[#6a7cce]" />
          <p className="text-[#6a7cce]">Dany Daniel</p>
        </Link>
      </footer>
    </div>
  );
}
