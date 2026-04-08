# 🖼️ Image Processor MCP Server

A powerful Model Context Protocol (MCP) server for image processing, designed to empower AI models with advanced image manipulation capabilities. From basic editing to AI-powered background removal, this server provides a comprehensive toolkit for programmatic image handling.

## ✨ Features

- **🚀 AI Background Removal**: Seamlessly remove backgrounds using state-of-the-art models (u2net, etc.).
- **📥 Smart Downloader**: Download images from single or multiple URLs with automatic format detection.
- **📐 Precision Cropping**: Crop images using exact pixel coordinates.
- **🖼️ Flexible Resizing**: Scale images with optional aspect ratio preservation and high-quality interpolation.
- **🔄 Format Conversion**: Convert between JPEG, PNG, GIF, and WEBP with quality control and transparency handling.

## 🛠️ Tech Stack

- **[Python 3.13+](https://www.python.org/)**: Leveraging the latest Python features.
- **[FastMCP](https://github.com/modelcontextprotocol/python-sdk)**: High-performance framework for MCP server development.
- **[Pillow (PIL)](https://python-pillow.org/)**: The industry-standard library for image processing in Python.
- **[rembg](https://github.com/danielgatis/rembg)**: AI-driven background removal tool.
- **[uv](https://github.com/astral-sh/uv)**: Ultra-fast Python package and environment manager.

## 🚀 Getting Started

### Prerequisites

- **Python 3.13** or higher.
- **uv** installed. If you don't have it, install it via:
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp-image-processor
   ```

2. **Sync dependencies**:
   ```bash
   uv sync
   ```

## ⚙️ Configuration

To use this server with an MCP-compatible client (like Claude Desktop or IDEs), add the following configuration:

### Claude Desktop Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "image-processor": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-image-processor",
        "run",
        "main.py"
      ]
    }
  }
}
```

> [!IMPORTANT]
> Ensure you provide the **absolute path** to the project directory.

## 🧰 Available Tools

| Tool | Description |
|------|-------------|
| `download_img` | Downloads one or multiple images from URLs to a local path. |
| `crop_img` | Crops a local image using (left, top, right, bottom) coordinates. |
| `resize_img` | Resizes an image. Supports aspect ratio locking and custom dimensions. |
| `convert_img` | Converts images between JPEG, PNG, GIF, and WEBP. |
| `remove_bg` | Removes the background using AI models (u2net, isnet, etc.). |

## 🖥️ Manual Execution

For testing or development purposes, you can run the server manually:

```bash
uv run main.py
```

The server communicates via `stdio` by default, as per the MCP specification.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
