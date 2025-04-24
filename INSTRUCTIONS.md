# Creating Your GitHub Release

This document provides instructions for creating a GitHub release for your Zoom Recording Prompt application.

## Step 1: Build the Application

1. Make sure you have Python 3.8+ installed
2. Run the build script:
```bash
./build_macos.sh
```
3. This will create the application in the `dist` folder and a distribution ZIP

## Step 2: Test the Application

1. Try running the application from the distribution:
```bash
open dist/Zoom\ Recording\ Prompt.app
```
2. Set up your `.env` file in your home directory
3. Test that all features work as expected

## Step 3: Create a GitHub Repository (if you haven't already)

1. Create a new repository on GitHub named `zoom-auto-prompt`
2. Initialize the repository:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/zoom-auto-prompt.git
git push -u origin main
```

## Step 4: Create a GitHub Release

1. Go to your GitHub repository in a browser
2. Click on "Releases" on the right side
3. Click "Create a new release"
4. Set the tag version to `v1.0.0`
5. Set the release title to "Zoom Recording Prompt v1.0.0"
6. Copy and paste the contents of `RELEASE_TEMPLATE.md` into the description
7. Upload the `dist/Zoom Recording Prompt.zip` file as an asset
8. Click "Publish release"

## Step 5: Update Documentation Links

After publishing your release, update the following:

1. In the README.md file, update the release link:
```markdown
[Releases page](https://github.com/yourusername/zoom-auto-prompt/releases)
```
2. Update your repository link in setup.py

## Step 6: Sharing with Others

When sharing with others, provide:

1. A link to your GitHub repository
2. A direct link to the latest release
3. Instructions for:
   - Installing the application
   - Setting up Zoom API credentials
   - Configuration steps

## Maintenance Guidelines

For future updates:

1. Increment the version number in:
   - `setup.py`
   - Release title
   - Release tag
2. Document changes in the RELEASE_TEMPLATE.md file
3. Rebuild the application and create a new release

## Security Considerations

Remind users to:

1. Keep their `.env` file secure
2. Never share their Zoom API credentials
3. Be cautious about granting the application permissions
