# Guía de Instalación en Dispositivos Móviles Android (Smartphones y Tablets)

Para desplegar **GMAO Industrial Pro** en los dispositivos móviles de los técnicos de planta, dispones de dos métodos industriales:

---

## 📲 Método 1: Instalación Inmediata PWA (Recomendado - 1 Clic sin cables)

Este es el método oficial utilizado por empresas como Google, Microsoft y Twitter para aplicaciones industriales en planta:

1. Asegúrate de que el servidor esté encendido en la PC o servidor local (`Iniciar_GMAO.bat`).
2. Conecta el teléfono Android a la red Wi-Fi de la empresa.
3. Abre el navegador Google Chrome o Edge en el celular e ingresa la dirección del servidor (ejemplo: `http://192.168.1.50:8000`).
4. Verás aparecer en la parte superior el botón verde: **"📲 Instalar App"**.
   - O pulsa los 3 puntos del menú de Chrome y selecciona: **"Instalar aplicación"** o **"Añadir a la pantalla de inicio"**.
5. ¡Listo! El sistema se instalará como una **aplicación independiente (APK nativa)** en el cajón de aplicaciones de Android, con icono propio, apertura en pantalla completa (sin barra de navegador), acceso a la cámara y soporte offline.

---

## 🛠️ Método 2: Compilación de APK Nativa (.apk) con Android Studio

Si tu empresa requiere distribuir un archivo instalador `.apk` físico vía USB, WhatsApp corporativo o sistema MDM:

### Pasos para compilar el APK:
1. Abre **Android Studio** en tu PC.
2. Selecciona **Open an Existing Project** y elige la carpeta `GMAO/android`.
3. Espera a que Gradle sincronice las dependencias.
4. Ve al menú: **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
5. Una vez finalizado, Android Studio generará el archivo:
   `android/app/build/outputs/apk/debug/app-debug.apk`
6. Transfiere ese archivo `.apk` al teléfono del técnico e instálalo permitiendo "Orígenes desconocidos".

---

## ⚙️ Configuración de IP en la App Android

Al abrir la aplicación Android nativa por primera vez, si no encuentra el servidor en la IP por defecto, mostrará un diálogo automático solicitando la IP:
* Ingrese la IP de la máquina servidor, por ejemplo: `192.168.1.50:8000`.
* La aplicación guardará esta configuración de forma persistente y se conectará automáticamente en cada arranque.
