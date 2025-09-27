import mcp
from mcp.server.fastmcp import FastMCP
import requests
import os
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
import io
from rembg import remove

# Create an MCP server
mcp = FastMCP(
    "image_processor",
    # description="Crop, resize, convert and remove the background of your images.",
)


@mcp.tool()
async def download_img(path=str, url=str | list[str], file_name=None):
    """
    Downloads an image from a URL.

    Args:
        url (str): The URL of the image to download.
        file_name (str, optional): The name to save the image with.
        path (str): The directory where the image will be saved.
        If not specified, the filename from the URL will be used.
        Default is None.

    Returns:
        bool: True if the download was successful, False otherwise.
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
async def crop_img(input_path: str, output_path: str, left: int, top: int, right: int, bottom: int):
    """
    Crops an image using the specified coordinates.
    
    Args:
        input_path (str): Path to the input image.
        output_path (str): Path where the cropped image will be saved.
        left (int): X coordinate of the left edge of the crop.
        top (int): Y coordinate of the top edge of the crop.
        right (int): X coordinate of the right edge of the crop.
        bottom (int): Y coordinate of the bottom edge of the crop.
    
    Returns:
        dict: Operation result with crop information.
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            return {"success": False, "error": f"File {input_path} does not exist"}
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Open the image
        with Image.open(input_path) as image:
            # Get original dimensions
            original_width, original_height = image.size
            
            # Validate coordinates
            if left < 0 or top < 0 or right > original_width or bottom > original_height:
                return {
                    "success": False,
                    "error": f"Invalid coordinates. Image: {original_width}x{original_height}, Crop: ({left},{top},{right},{bottom})"
                }
            
            if left >= right or top >= bottom:
                return {"success": False, "error": "Invalid crop coordinates"}
            
            # Crop the image
            cropped_image = image.crop((left, top, right, bottom))
            
            # Save the cropped image
            cropped_image.save(output_path)
            
            return {
                "success": True,
                "message": f"Image cropped successfully",
                "original_size": f"{original_width}x{original_height}",
                "cropped_size": f"{right-left}x{bottom-top}",
                "output_path": output_path
            }
            
    except Exception as e:
        return {"success": False, "error": f"Error cropping image: {str(e)}"}

@mcp.tool()
async def resize_img(input_path: str, output_path: str, width: int, height: int, maintain_aspect_ratio: bool = False):
    """
    Resizes an image to the specified dimensions.
    
    Args:
        input_path (str): Path to the input image.
        output_path (str): Path where the resized image will be saved.
        width (int): New width of the image.
        height (int): New height of the image.
        maintain_aspect_ratio (bool): If True, maintains the original aspect ratio (optional).
    
    Returns:
        dict: Operation result with resizing information.
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            return {"success": False, "error": f"File {input_path} does not exist"}
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Open the image
        with Image.open(input_path) as image:
            original_width, original_height = image.size
            
            # Validate dimensions
            if width <= 0 or height <= 0:
                return {"success": False, "error": "Dimensions must be greater than 0"}
            
            if maintain_aspect_ratio:
                # Calculate ratio to maintain aspect ratio
                ratio = min(width / original_width, height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            else:
                new_width = width
                new_height = height
            
            # Resize the image using LANCZOS for better quality
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save the resized image
            resized_image.save(output_path)
            
            return {
                "success": True,
                "message": "Image resized successfully",
                "original_size": f"{original_width}x{original_height}",
                "new_size": f"{new_width}x{new_height}",
                "aspect_ratio_maintained": maintain_aspect_ratio,
                "output_path": output_path
            }
            
    except Exception as e:
        return {"success": False, "error": f"Error resizing image: {str(e)}"}

@mcp.tool()
async def convert_img(input_path: str, output_path: str, target_format: str, quality: int = 95):
    """
    Converts an image to a specific format (JPEG, PNG, GIF, WEBP).
    
    Args:
        input_path (str): Path to the input image.
        output_path (str): Path where the converted image will be saved.
        target_format (str): Target format ('JPEG', 'PNG', 'GIF', 'WEBP').
        quality (int): Image quality for lossy formats (1-100, optional).
    
    Returns:
        dict: Operation result with conversion information.
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            return {"success": False, "error": f"File {input_path} does not exist"}
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate target format
        supported_formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
        target_format = target_format.upper()
        if target_format not in supported_formats:
            return {
                "success": False,
                "error": f"Unsupported format: {target_format}. Supported formats: {', '.join(supported_formats)}"
            }
        
        # Validate quality
        if not (1 <= quality <= 100):
            return {"success": False, "error": "Quality must be between 1 and 100"}
        
        # Open the image
        with Image.open(input_path) as image:
            original_format = image.format
            original_mode = image.mode
            
            # Prepare the image according to target format
            if target_format == 'JPEG':
                # JPEG doesn't support transparency, convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save with specified quality
                image.save(output_path, format=target_format, quality=quality, optimize=True)
                
            elif target_format == 'PNG':
                # PNG supports transparency, keep original mode or convert to RGBA
                if image.mode not in ('RGBA', 'RGB', 'L', 'LA'):
                    image = image.convert('RGBA')
                image.save(output_path, format=target_format, optimize=True)
                
            elif target_format == 'GIF':
                # GIF requires P (palette) or L (grayscale) mode
                if image.mode not in ('P', 'L'):
                    # Convert to P mode with optimized palette
                    image = image.convert('P', palette=Image.ADAPTIVE)
                image.save(output_path, format=target_format, optimize=True)
                
            elif target_format == 'WEBP':
                # WEBP supports both RGB and RGBA
                if image.mode not in ('RGB', 'RGBA'):
                    image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
                image.save(output_path, format=target_format, quality=quality, optimize=True)
            
            return {
                "success": True,
                "message": f"Image converted successfully from {original_format} to {target_format}",
                "original_format": original_format,
                "target_format": target_format,
                "original_mode": original_mode,
                "final_mode": image.mode,
                "output_path": output_path
            }
            
    except Exception as e:
        return {"success": False, "error": f"Error converting image: {str(e)}"}

@mcp.tool()
async def remove_bg(input_path: str, output_path: str, model_name: str = "u2net"):
    """
    Removes the background from an image using AI models.
    Now supports both local files and URLs.
    
    Args:
        input_path (str): Path to local image OR URL to image.
        output_path (str): Path where the image without background will be saved.
        model_name (str): AI model to use for background removal (optional).
        Options: 'u2net', 'u2netp', 'u2net_human_seg', 'silueta', 'isnet-general-use'
    
    Returns:
        dict: Operation result with background removal information.
    """
    temp_file_path = None
    
    try:
        # NEW SECTION: Detect if input is URL and download
        if input_path.startswith(('http://', 'https://')):
            # Create temporary directory
            temp_dir = "./temp_downloads"
            Path(temp_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate temporary filename
            parsed_url = urlparse(input_path)
            url_filename = os.path.basename(parsed_url.path)
            if not url_filename or '.' not in url_filename:
                url_filename = "temp_image.jpg"
            
            # Extract base name without extension for download_img
            base_name = os.path.splitext(url_filename)[0]
            
            # Download the image
            download_success = await download_img(temp_dir, input_path, base_name)
            
            if not download_success:
                return {"success": False, "error": f"Failed to download image from URL: {input_path}"}
            
            # Find the downloaded file (download_img may change the extension)
            downloaded_files = [f for f in os.listdir(temp_dir) if f.startswith(base_name)]
            if not downloaded_files:
                return {"success": False, "error": f"Downloaded file not found in {temp_dir}"}
            
            temp_file_path = os.path.join(temp_dir, downloaded_files[0])
            input_path = temp_file_path
        
        # Check if input file exists (now works for both local files and downloaded URLs)
        if not os.path.exists(input_path):
            return {"success": False, "error": f"File {input_path} does not exist"}
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate model name
        valid_models = ['u2net', 'u2netp', 'u2net_human_seg', 'silueta', 'isnet-general-use']
        if model_name not in valid_models:
            return {
                "success": False,
                "error": f"Invalid model: {model_name}. Valid models: {', '.join(valid_models)}"
            }
        
        # Open and process the image
        with Image.open(input_path) as input_image:
            original_format = input_image.format
            original_size = input_image.size
            
            # Convert image to bytes for rembg processing
            img_byte_arr = io.BytesIO()
            input_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Remove background using rembg
            from rembg import new_session
            session = new_session(model_name)
            output_bytes = remove(img_byte_arr, session=session)
            
            # Convert back to PIL Image
            output_image = Image.open(io.BytesIO(output_bytes))
            
            # Save the result
            output_image.save(output_path, format='PNG')
            
            return {
                "success": True,
                "message": "Background removed successfully",
                "original_format": original_format,
                "original_size": f"{original_size[0]}x{original_size[1]}",
                "model_used": model_name,
                "output_format": "PNG",
                "output_path": output_path
            }
            
    except Exception as e:
        return {"success": False, "error": f"Error removing background: {str(e)}"}
    
    finally:
        # Clean up temporary file if it was downloaded
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                # Try to remove temporary directory if it's empty
                temp_dir = os.path.dirname(temp_file_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except:
                pass  # Ignore cleanup errors

if __name__ == "__main__":
    mcp.run(transport="stdio")
