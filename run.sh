#!/bin/bash

echo "🏥 Medizinische Gesprächszusammenfassung - Streamlit App"
echo "========================================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit ist nicht installiert."
    echo "📦 Installiere Abhängigkeiten..."
    pip install -r requirements.txt
    echo "✅ Installation abgeschlossen!"
    echo ""
fi

echo "🚀 Starte Streamlit App..."
echo ""
echo "Die App öffnet sich automatisch in Ihrem Browser."
echo "Falls nicht, öffnen Sie: http://localhost:8501"
echo ""
echo "Zum Beenden drücken Sie: Strg+C"
echo ""
echo "========================================================="
echo ""

streamlit run app.py
