---
title: "Publicar versiones de Garúa en GitHub y PyPI"
description: "Prepara una versión de Garúa, configura Trusted Publishing y publica el paquete y su release mediante GitHub Actions."
---

# Publicar una versión

La web y el paquete tienen flujos distintos:

| Acción | Resultado |
| --- | --- |
| Push a `dev` o pull request | Ejecuta las pruebas. No publica. |
| Push a `main` | Ejecuta pruebas y despliega la documentación mediante `docs.yml`. |
| Push de una etiqueta `vX.Y.Z` | Valida, prueba, construye y publica en PyPI; después crea el release de GitHub. |

Un release no es necesario para que Google rastree la documentación. Los cambios
SEO estarán disponibles al desplegar `main`; indexar las páginas depende de Google.

## Configuración inicial

Antes de subir la primera etiqueta:

1. En GitHub, crea el environment **`pypi`** en el repositorio
   `danyneyra/garua`. Restringe los despliegues a etiquetas `v*`. Puedes activar
   revisión manual si quieres aprobar cada publicación.
2. En PyPI, abre el proyecto `garua` → **Manage → Publishing** y añade un
   Trusted Publisher de GitHub con estos valores exactos:

   | Campo | Valor |
   | --- | --- |
   | Owner | `danyneyra` |
   | Repository | `garua` |
   | Workflow | `release.yml` |
   | Environment | `pypi` |

No se necesita un token permanente de PyPI: `publish-pypi` solicita una credencial
temporal con OIDC. Esta configuración debe realizarla quien administra el proyecto.
Consulta la [guía oficial de PyPI](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).

## Preparar y publicar

1. En `dev`, actualiza la versión en `pyproject.toml`, `settings.py`, `uv.lock`
   y `CITATION.cff`. Haz coincidir la fecha de citación con la del changelog.
2. Revisa y guarda los cambios en commits, sube `dev` y comprueba las pruebas.
3. Integra los cambios en `main` y comprueba Actions: pruebas y despliegue de la web.
4. Sobre el commit que quieres publicar, que ya debe pertenecer a `main`, crea
   y sube una etiqueta. Para esta publicación:

   ```bash
   git tag -a v0.31.0 -m "Garúa 0.31.0"
   git push origin v0.31.0
   ```

Subir la etiqueta inicia una publicación real. El workflow comprueba que el
commit pertenece al historial de `main`, valida versión y fecha, ejecuta la matriz
de pruebas, compila la documentación y construye wheel y sdist. PyPI y GitHub
reciben los mismos archivos. Las notas se extraen del changelog sin sus tablas
desplegables; incluyen un enlace al detalle de esa versión.

Para validar las notas localmente, sin publicar:

```bash
uv run --locked python scripts/prepare_release.py --tag v0.31.0
```

Se guardan en `reports/release-notes.md`. Los artefactos del workflow se conservan
como `release-bundle`, incluso si falla el paso de publicación.

## Si falla la publicación

- Si falla la validación o las pruebas, no se publica el paquete.
- Si falta el Trusted Publisher, revisa los cuatro valores de PyPI y el environment.
- Si PyPI se publicó correctamente pero falla GitHub, reejecuta **solo los jobs
  fallidos**, para no intentar volver a subir la versión a PyPI.
- Si PyPI recibió solo parte de los archivos, revisa los artefactos antes de
  completar manualmente la publicación. No se omiten duplicados automáticamente.
- No muevas ni reutilices una etiqueta de una versión ya publicada. Las
  correcciones posteriores deben tener otra versión.

El flujo no hace commits ni merges, no sube cambios a `main` y no publica al
ejecutar las pruebas localmente. La configuración de ramas protegidas y los
permisos de las cuentas se administran en GitHub y PyPI.
