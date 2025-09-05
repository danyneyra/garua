import { Link } from "@heroui/link";
import {
  Navbar as HeroUINavbar,
  NavbarContent,
  NavbarItem,
} from "@heroui/navbar";

import { siteConfig } from "@/config/site";
import { ThemeSwitch } from "@/components/theme-switch";
import { GithubIcon } from "@/components/icons";
import garuaLogo from "@/assets/garua-logo.svg";

export const Navbar = () => {
  return (
    <HeroUINavbar maxWidth="xl" position="sticky">
      <NavbarContent
        className="sm:flex basis-1/5 sm:basis-full"
        justify="start"
      >
        <NavbarItem className="sm:flex gap-2">
          <a href="./">
            <img src={garuaLogo} alt="Garúa" className="w-32 h-auto" />
          </a>
        </NavbarItem>
      </NavbarContent>
      <NavbarContent className="sm:flex basis-1/5 sm:basis-full" justify="end">
        <NavbarItem className="sm:flex gap-3">
          <Link isExternal href={siteConfig.links.github} title="GitHub">
            <GithubIcon className="text-default-500" />
          </Link>
          <ThemeSwitch />
        </NavbarItem>
      </NavbarContent>
    </HeroUINavbar>
  );
};
