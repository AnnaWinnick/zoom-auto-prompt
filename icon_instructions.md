# Adding an Icon to Your Application

To add a custom icon to your Zoom Recording Prompt application, follow these steps:

## 1. Create an Icon File

Create or download a 1024x1024 PNG image for your icon.

macOS requires icons in the `.icns` format. You can convert your PNG to ICNS using tools like:
- **IconSet Creator** (App Store)
- **Image2icon** (https://img2icnsapp.com/)
- **Command-line tools** like `iconutil`

## 2. Converting PNG to ICNS Using iconutil

If you prefer using the command line:

1. Create an iconset folder:
```bash
mkdir MyIcon.iconset
```

2. Generate images at different sizes:
```bash
# Generate the various icon sizes
sips -z 16 16     original.png --out MyIcon.iconset/icon_16x16.png
sips -z 32 32     original.png --out MyIcon.iconset/icon_16x16@2x.png
sips -z 32 32     original.png --out MyIcon.iconset/icon_32x32.png
sips -z 64 64     original.png --out MyIcon.iconset/icon_32x32@2x.png
sips -z 128 128   original.png --out MyIcon.iconset/icon_128x128.png
sips -z 256 256   original.png --out MyIcon.iconset/icon_128x128@2x.png
sips -z 256 256   original.png --out MyIcon.iconset/icon_256x256.png
sips -z 512 512   original.png --out MyIcon.iconset/icon_256x256@2x.png
sips -z 512 512   original.png --out MyIcon.iconset/icon_512x512.png
sips -z 1024 1024 original.png --out MyIcon.iconset/icon_512x512@2x.png
```

3. Create the .icns file:
```bash
iconutil -c icns MyIcon.iconset
```

## 3. Add the Icon to Your Application

Once you have your `.icns` file, you can:

1. Update the `setup.py` file to include the icon:
```python
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'requests', 'pyautogui', 'dotenv', 'psutil'],
    'iconfile': 'MyIcon.icns',  # Add this line
    'plist': {
        # ... existing plist settings ...
    }
}
```

2. Rebuild your application:
```bash
./build_macos.sh
```

## Suggested Icon Design

For a Zoom Recording Prompt app, consider an icon that combines:
- Zoom's video camera concept
- A recording element (red dot or circle)
- A notification/prompt visual cue

Keep the design simple and recognizable at smaller sizes.
