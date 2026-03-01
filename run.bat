@echo off
echo ==========================================================
echo Medizinische Gespraechszusammenfassung - Streamlit App
echo ==========================================================
echo.

REM Check if streamlit is installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Streamlit ist nicht installiert.
    echo Installiere Abhaengigkeiten...
    pip install -r requirements.txt
    echo Installation abgeschlossen!
    echo.
)

echo Starte Streamlit App...
echo.
echo Die App oeffnet sich automatisch in Ihrem Browser.
echo Falls nicht, oeffnen Sie: http://localhost:8501
echo.
echo Zum Beenden druecken Sie: Strg+C
echo.
echo ==========================================================
echo.

streamlit run app.py

pause
