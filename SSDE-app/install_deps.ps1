# PowerShell script to install SSDE dependencies in correct order
# Run from SSDE-app directory: .\install_deps.ps1

Write-Host "Installing SSDE dependencies..." -ForegroundColor Green

# Step 1: Install NumPy 1.x first
Write-Host "Step 1: Installing NumPy 1.x..." -ForegroundColor Yellow
pip install "numpy>=1.24.0,<2.0" --force-reinstall

# Step 2: Install OpenCV compatible with NumPy 1.x
Write-Host "Step 2: Installing OpenCV 4.9.x..." -ForegroundColor Yellow
pip install "opencv-python>=4.8.0,<4.10.0" --force-reinstall

# Step 3: Uninstall opencv-contrib-python if present (conflicts with opencv-python)
Write-Host "Step 3: Removing conflicting opencv-contrib-python..." -ForegroundColor Yellow
pip uninstall opencv-contrib-python -y 2>$null

# Step 4: Install remaining dependencies
Write-Host "Step 4: Installing other dependencies..." -ForegroundColor Yellow
pip install pygame>=2.5.0
pip install mss>=9.0.0
pip install pywin32>=306

# Step 5: Install MediaPipe (will try to install opencv-contrib but we'll prevent it)
Write-Host "Step 5: Installing MediaPipe..." -ForegroundColor Yellow
pip install mediapipe>=0.10.0

# Step 6: Ensure opencv-contrib-python is removed (MediaPipe may have installed it)
Write-Host "Step 6: Final cleanup..." -ForegroundColor Yellow
pip uninstall opencv-contrib-python -y 2>$null

# Step 7: Verify NumPy version
Write-Host "`nVerifying installation..." -ForegroundColor Green
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
python -c "import pygame; print(f'Pygame version: {pygame.__version__}')"

Write-Host "`nInstallation complete! Run: python run.py" -ForegroundColor Green
