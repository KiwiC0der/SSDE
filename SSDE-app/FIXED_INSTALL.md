# SSDE Installation - Fixed Dependencies

## Problem Summary
The original installation had version conflicts:
- NumPy 2.x was being installed (MediaPipe requires NumPy 1.x)
- OpenCV 4.13.x requires NumPy 2.x (conflicts with MediaPipe)
- opencv-contrib-python conflicts with opencv-python

## Solution Applied
1. **NumPy 1.26.4** installed first (compatible with MediaPipe)
2. **OpenCV 4.9.0.80** installed (compatible with NumPy 1.x)
3. **opencv-contrib-python** removed (conflicts with opencv-python)

## Current Working Versions
- NumPy: 1.26.4 ✅
- OpenCV: 4.9.0.80 ✅
- Pygame: 2.6.1 ✅
- MediaPipe: 0.10.32 ✅
- MSS: 10.1.0 ✅
- pywin32: 306 ✅

## How to Run
```powershell
cd C:\Users\Noname\Desktop\SSDE\SSDE-app
python run.py
```

## If You Need to Reinstall
If dependencies get messed up again, run:
```powershell
cd C:\Users\Noname\Desktop\SSDE\SSDE-app
python -m pip install "numpy>=1.24.0,<2.0" --force-reinstall --no-deps
python -m pip install "opencv-python>=4.8.0,<4.10.0" --force-reinstall --no-deps
python -m pip install pygame>=2.5.0 mss>=9.0.0 pywin32>=306 mediapipe>=0.10.0
python -m pip uninstall opencv-contrib-python -y
```

## Notes
- The `--no-deps` flag prevents pip from automatically upgrading NumPy to 2.x
- MediaPipe will complain about missing opencv-contrib-python, but this is safe to ignore
- The application should now run without errors
