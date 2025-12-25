# Image Processor MCP Server

Un servidor MCP (Model Context Protocol) potente para el procesamiento de imágenes, diseñado para permitir que los modelos de IA realicen operaciones comunes de edición y manipulación de imágenes.

## 🛠️ Stack Tecnológico

Este proyecto está construido con las siguientes tecnologías:

- **Python 3.13+**: Lenguaje de programación principal.
- **[FastMCP](https://github.com/modelcontextprotocol/python-sdk)**: Framework para la creación rápida de servidores MCP.
- **[Pillow (PIL)](https://python-pillow.org/)**: Biblioteca para la manipulación y procesamiento de imágenes.
- **[rembg](https://github.com/danielgatis/rembg)**: Herramienta basada en IA para la eliminación de fondos.
- **[Requests](https://requests.readthedocs.io/)**: Para la descarga de imágenes desde URLs.
- **[uv](https://github.com/astral-sh/uv)**: El administrador de paquetes y entornos de Python ultra rápido para la gestión de dependencias.

## 🚀 Instalación y Configuración

Siga estos pasos para configurar el proyecto en cualquier computadora:

### Prerrequisitos

- **Python 3.13** o superior.
- **uv** instalado. Si no tienes `uv`, puedes instalarlo con:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd image_processor
   ```

2. **Instalar dependencias**:
   Usa `uv` para sincronizar el entorno e instalar todas las dependencias necesarias:
   ```bash
   uv sync
   ```

## ⚙️ Configuración del Servidor MCP

Para usar este servidor en cualquier herramienta compatible con el Model Context Protocol (como Claude Desktop, IDEs con soporte MCP, etc.), debe añadir la configuración correspondiente.

### Ejemplo de Configuración (JSON)

Dependiendo de su cliente, deberá añadir un bloque similar a este en su archivo de configuración (por ejemplo, `settings.json` o la interfaz de configuración del cliente):

```json
{
  "mcpServers": {
    "image-processor": {
      "command": "uv",
      "args": [
        "--directory",
        "/ruta/donde/clonaste/el/repositorio",
        "run",
        "main.py"
      ]
    }
  }
}
```

> [!IMPORTANT]
> Reemplace `/ruta/donde/clonaste/el/repositorio` con la ruta absoluta real del proyecto en su sistema.

## 🛠️ Herramientas Disponibles

El servidor ofrece las siguientes herramientas para procesar imágenes:

- `download_img`: Descarga imágenes desde una o varias URLs.
- `crop_img`: Recorta una imagen local especificando las coordenadas (left, top, right, bottom).
- `resize_img`: Cambia el tamaño de una imagen, con opción de mantener la relación de aspecto.
- `convert_img`: Convierte imágenes entre formatos (JPEG, PNG, GIF, WEBP).
- `remove_bg`: Elimina el fondo de una imagen usando modelos de IA (u2net, etc.).

## 🖥️ Uso

Para iniciar el servidor MCP:

```bash
uv run main.py
```

El servidor utiliza el transporte `stdio` por defecto para comunicarse con los clientes MCP.
