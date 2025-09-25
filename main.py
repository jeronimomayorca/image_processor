import mcp
from mcp.server.fastmcp import FastMCP
import requests
import os
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
import io

# Create an MCP server
mcp = FastMCP(
    "image_processor",
    # description="Crop, resize, convert and remove the background of your images.",
)


@mcp.tool()
async def download_image(path=str, url=str | list[str], file_name=None):
    """
    Descarga una imagen desde una URL.

    Args:
        url (str): La URL de la imagen a descargar.
        file_name (str, optional): El nombre con el que se guardará la imagen.
        path (str): El directorio donde se guardará la imagen.
        Si no se especifica, se usará el nombre
        del archivo de la URL. Por defecto es None.

    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario.
    """

    try:
        # Ensure the path directory exists
        Path(path).mkdir(parents=True, exist_ok=True)

        # Handle single URL or list of URLs
        urls = [url] if isinstance(url, str) else url
        downloaded_files = []

        for single_url in urls:
            # Download the image
            response = requests.get(single_url, stream=True, timeout=30)
            response.raise_for_status()

            # Verify it's an image by checking content type
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                print(
                    f"Warning: URL {single_url} doesn't appear to be an image (content-type: {content_type})"
                )

            # Determine filename and extension
            parsed_url = urlparse(single_url)
            url_filename = os.path.basename(parsed_url.path)
            
            # Extract extension from URL first
            url_extension = ""
            if url_filename and "." in url_filename:
                url_extension = os.path.splitext(url_filename)[1].lower()
            
            # If no extension from URL, determine from content-type
            if not url_extension:
                if "png" in content_type.lower():
                    url_extension = ".png"
                elif "gif" in content_type.lower():
                    url_extension = ".gif"
                elif "webp" in content_type.lower():
                    url_extension = ".webp"
                elif "jpeg" in content_type.lower() or "jpg" in content_type.lower():
                    url_extension = ".jpg"
                else:
                    url_extension = ".jpg"  # default
            
            # Determine final filename
            if file_name:
                # If custom filename provided, ensure it has the correct extension
                if "." in file_name:
                    # User provided extension, but use the original extension from URL/content-type
                    base_name = os.path.splitext(file_name)[0]
                    filename = f"{base_name}{url_extension}"
                else:
                    # No extension in custom name, add the original extension
                    filename = f"{file_name}{url_extension}"
            else:
                # Use filename from URL or generate one
                if url_filename and "." in url_filename:
                    filename = url_filename
                else:
                    filename = f"image_{len(downloaded_files) + 1}{url_extension}"

            # Full file path
            file_path = os.path.join(path, filename)

            # Validate image using PIL
            try:
                image_data = response.content
                image = Image.open(io.BytesIO(image_data))
                image.verify()  # Verify it's a valid image

                # Save the image
                with open(file_path, "wb") as f:
                    f.write(image_data)

                downloaded_files.append(file_path)
                print(f"Successfully downloaded: {single_url} -> {file_path}")

            except Exception as img_error:
                print(f"Error validating image from {single_url}: {img_error}")
                return False

        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


@mcp.tool()
async def say_hi(name=str):
    """
    Greets a person to indicate I'm working well.

    Args:
        name (str): El nombre de la persona a saludar.

    Returns:
        str: Un saludo personalizado.
    """
    return f"Hola, {name}, estoy funcionando de maravilla!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
