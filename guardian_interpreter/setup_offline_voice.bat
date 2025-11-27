@echo off
REM setup_offline_voice.bat
REM Windows setup script for offline voice explanation system

echo Setting up Offline Voice Explanation System for Guardian Node...
echo.

REM Create necessary directories
echo Creating directory structure...
if not exist "skills\audio_explanations" mkdir skills\audio_explanations
if not exist "skills\audio_explanations\audio_files" mkdir skills\audio_explanations\audio_files
if not exist "skills\audio_explanations\cache" mkdir skills\audio_explanations\cache

REM Install Python packages (offline-compatible only)
echo Installing Python packages...
pip install pyttsx3 edge-tts pygame

REM Create offline audio configuration
echo Creating offline audio configuration...
(
echo {
echo   "tts_service": "edge_tts_offline",
echo   "voice_settings": {
echo     "child": {
echo       "voice_name": "en-US-JennyNeural",
echo       "pitch": "+10Hz",
echo       "rate": "+10%%"
echo     },
echo     "teen": {
echo       "voice_name": "en-US-AriaNeural", 
echo       "pitch": "0Hz",
echo       "rate": "0%%"
echo     },
echo     "adult": {
echo       "voice_name": "en-US-DavisNeural",
echo       "pitch": "0Hz", 
echo       "rate": "0%%"
echo     }
echo   },
echo   "output_format": "mp3",
echo   "sample_rate": 24000,
echo   "cache_enabled": true,
echo   "offline_mode": true
echo }
) > skills\audio_config.json

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Run 'python skills/audio_pre_recorder.py --record' to pre-record explanations
echo 2. Test with 'python skills/offline_voice_explain.py --risk phishing --age teen'
echo 3. All audio files will be cached locally for true offline operation
echo.
pause