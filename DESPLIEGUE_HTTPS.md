# 🚀 Despliegue con HTTPS para Usar la Cámara

## ⚠️ Problema: La Cámara Requiere HTTPS

Los navegadores modernos requieren una conexión segura (HTTPS) para acceder a la cámara por razones de seguridad. `localhost` funciona, pero si quieres acceder desde otros dispositivos o usar la cámara, necesitas HTTPS.

## 🌐 Soluciones para Desplegar con HTTPS

### Opción 1: Streamlit Cloud (RECOMENDADO - GRATIS)

**Ventajas:**
- ✅ Completamente gratis
- ✅ HTTPS automático
- ✅ Fácil de configurar
- ✅ Actualización automática desde GitHub

**Pasos:**

1. **Ir a Streamlit Cloud**
   - Visita: https://streamlit.io/cloud
   - Haz clic en "Sign up" o "Get started"

2. **Conectar con GitHub**
   - Inicia sesión con tu cuenta de GitHub
   - Autoriza a Streamlit Cloud

3. **Crear Nueva App**
   - Clic en "New app"
   - Selecciona tu repositorio: `junnior123456/Metodos_numericos2`
   - Branch: `master`
   - Main file path: `app.py`
   - Clic en "Deploy"

4. **Esperar Despliegue**
   - Toma 2-5 minutos
   - Obtendrás una URL como: `https://tu-app.streamlit.app`

5. **¡Listo!**
   - Tu app estará disponible con HTTPS
   - La cámara funcionará perfectamente
   - Cada push a GitHub actualizará automáticamente

**URL de tu app será algo como:**
```
https://metodos-numericos2-junnior123456.streamlit.app
```

---

### Opción 2: Render (GRATIS)

**Pasos:**

1. Ir a https://render.com
2. Crear cuenta gratuita
3. "New" → "Web Service"
4. Conectar repositorio de GitHub
5. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
6. Deploy

---

### Opción 3: Heroku (GRATIS con limitaciones)

**Pasos:**

1. Crear cuenta en https://heroku.com
2. Instalar Heroku CLI
3. Crear archivo `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
4. Crear archivo `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   headless = true
   port = $PORT
   enableCORS = false
   " > ~/.streamlit/config.toml
   ```
5. Comandos:
   ```bash
   heroku login
   heroku create tu-app-metodos-numericos
   git push heroku master
   ```

---

### Opción 4: Railway (GRATIS)

**Pasos:**

1. Ir a https://railway.app
2. Conectar con GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Seleccionar tu repositorio
5. Railway detectará automáticamente Streamlit
6. Deploy

---

### Opción 5: Localhost con HTTPS (Para Desarrollo)

Si quieres probar localmente con HTTPS:

**Usando ngrok (Temporal):**

1. Descargar ngrok: https://ngrok.com/download
2. Ejecutar tu app Streamlit:
   ```bash
   streamlit run app.py
   ```
3. En otra terminal:
   ```bash
   ngrok http 8501
   ```
4. Obtendrás una URL HTTPS temporal como:
   ```
   https://abc123.ngrok.io
   ```

**Nota:** La URL de ngrok cambia cada vez que lo ejecutas (versión gratuita).

---

## 📋 Archivos Necesarios para Despliegue

Tu repositorio ya tiene todo lo necesario:
- ✅ `requirements.txt` - Dependencias
- ✅ `app.py` - Aplicación principal
- ✅ `utils/` - Módulos auxiliares

---

## 🎯 Recomendación Final

**Para tu proyecto, te recomiendo Streamlit Cloud porque:**

1. Es completamente gratis
2. Configuración en 5 minutos
3. HTTPS automático
4. Actualización automática desde GitHub
5. Perfecto para proyectos académicos
6. No requiere configuración adicional
7. Soporta cámara sin problemas

---

## 🚀 Pasos Rápidos para Streamlit Cloud

```bash
# 1. Tu código ya está en GitHub ✅

# 2. Ir a https://streamlit.io/cloud

# 3. Sign up con GitHub

# 4. New app → Seleccionar:
#    - Repository: junnior123456/Metodos_numericos2
#    - Branch: master
#    - Main file: app.py

# 5. Deploy

# 6. Esperar 2-5 minutos

# 7. ¡Listo! Tu app estará en:
#    https://metodos-numericos2-xxxxx.streamlit.app
```

---

## 🔒 Seguridad de la Cámara

Una vez desplegado con HTTPS:
- ✅ La cámara funcionará en todos los navegadores
- ✅ Los usuarios podrán tomar fotos de ejercicios
- ✅ Funciona en móviles y tablets
- ✅ Conexión segura garantizada

---

## 📱 Acceso desde Móvil

Con HTTPS podrás:
1. Abrir la app desde tu celular
2. Usar la cámara para capturar ejercicios
3. Resolver problemas en tiempo real
4. Compartir el link con compañeros

---

## 🆘 Solución de Problemas

**Problema:** "La cámara no funciona en localhost"
- **Solución:** Usa `localhost` (funciona) o despliega con HTTPS

**Problema:** "Quiero compartir con compañeros"
- **Solución:** Despliega en Streamlit Cloud y comparte el link

**Problema:** "La app es lenta"
- **Solución:** Streamlit Cloud tiene recursos limitados en plan gratuito, pero suficientes para este proyecto

---

## 📞 Soporte

Si tienes problemas con el despliegue:
1. Revisa la documentación de Streamlit Cloud
2. Verifica que `requirements.txt` esté actualizado
3. Revisa los logs en el dashboard de Streamlit Cloud

---

**¡Tu código ya está listo para desplegarse! Solo falta elegir la plataforma.** 🎉

**Recomendación:** Empieza con Streamlit Cloud, es la más fácil y rápida.
