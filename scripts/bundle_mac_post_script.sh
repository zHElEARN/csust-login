APP_PATH="dist/CSUST Login.app"

find "$APP_PATH" -name "*__dot__app" -type d -exec rm -rf {} +

NOTIFICATOR_PATH=$(find "$APP_PATH" -name "Notificator.app" -type d | head -n 1)
osacompile -o /tmp/TempApplet.app -e 'return'
REAL_APPLET="/tmp/TempApplet.app/Contents/MacOS/applet"
TARGET_APPLET="$NOTIFICATOR_PATH/Contents/MacOS/applet"
rm -f "$TARGET_APPLET"
cp "$REAL_APPLET" "$TARGET_APPLET"
chmod +x "$TARGET_APPLET"
rm -rf /tmp/TempApplet.app
