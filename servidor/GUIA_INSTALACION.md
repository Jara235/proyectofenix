# 🚀 Guía de Instalación — Proyecto Fénix
## Servidor Windows 10 (Entorno de Desarrollo/Pruebas)

---

## PASO 1 — Instalar Docker Desktop

Docker es el único software que necesitas instalar manualmente. Instalará PostgreSQL y n8n automáticamente.

1. Descarga Docker Desktop en el servidor (vía Escritorio Remoto):
   **https://www.docker.com/products/docker-desktop/**

2. Ejecuta el instalador:
   - ✅ Selecciona **"Use WSL 2 instead of Hyper-V"**
   - ✅ Selecciona **"Add Docker to PATH"**

3. **Reinicia el servidor.**

4. Abre PowerShell y verifica:
   ```powershell
   docker --version
   docker compose version
   ```

---

## PASO 2 — Crear Estructura de Carpetas

```powershell
New-Item -ItemType Directory -Path "C:\fenix"
New-Item -ItemType Directory -Path "C:\fenix\sql"
New-Item -ItemType Directory -Path "C:\fenix\backups"
New-Item -ItemType Directory -Path "C:\fenix\evidencias"
```

---

## PASO 3 — Copiar los Archivos

Copia desde la carpeta `Proyecto fenix\servidor\` del equipo de desarrollo:

| Archivo | Destino en servidor |
|---------|---------------------|
| `docker-compose.yml` | `C:\fenix\` |
| `.env.example` | `C:\fenix\` |
| `sql\01_schema_v2.sql` | `C:\fenix\sql\` |
| `sql\02_datos_iniciales.sql` | `C:\fenix\sql\` |

---

## PASO 4 — Configurar Contraseñas (.env)

```powershell
Copy-Item "C:\fenix\.env.example" "C:\fenix\.env"
notepad "C:\fenix\.env"
```

Edita el archivo con tus valores:

```
POSTGRES_DB=fenix_db
POSTGRES_USER=fenix_admin
POSTGRES_PASSWORD=TU_CONTRASEÑA_SEGURA_AQUI

N8N_HOST=  ← dejar vacío por ahora (se llena en Paso 6)
N8N_ADMIN_USER=admin
N8N_ADMIN_PASSWORD=TU_CONTRASEÑA_SEGURA_AQUI

GEMINI_API_KEY=  ← obtener en https://aistudio.google.com/app/apikey
```

> ⚠️ Usa contraseñas de al menos 12 caracteres con mayúsculas, números y símbolos.

---

## PASO 5 — Levantar el Stack

```powershell
cd C:\fenix
docker compose up -d
```

Primera vez: descarga ~500 MB, toma 3-5 minutos. Verifica:

```powershell
docker compose ps
```

Debe mostrar:
```
NAME            STATUS          PORTS
fenix_postgres  Up (healthy)    0.0.0.0:5432->5432/tcp
fenix_n8n       Up              0.0.0.0:5678->5678/tcp
```

Prueba local: abre **http://localhost:5678** en el servidor → debe aparecer login de n8n.

---

## PASO 6 — Cloudflare Tunnel (Acceso Externo)

Para que los ingenieros accedan desde sus celulares en campo:

### 6.1 Descargar cloudflared

```powershell
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "C:\fenix\cloudflared.exe"
```

### 6.2 Crear túnel temporal

```powershell
C:\fenix\cloudflared.exe tunnel --url http://localhost:5678
```

Cloudflare mostrará una URL como:
```
https://palabras-random.trycloudflare.com
```

### 6.3 Actualizar .env con esa URL

```powershell
notepad "C:\fenix\.env"
```

Cambia: `N8N_HOST=palabras-random.trycloudflare.com`

Reinicia n8n:
```powershell
cd C:\fenix
docker compose restart n8n
```

### 6.4 Instalar como servicio (arranque automático)

```powershell
C:\fenix\cloudflared.exe service install
```

---

## PASO 7 — Verificación Final

Desde un celular con **datos móviles** (sin WiFi local), abre:
```
https://palabras-random.trycloudflare.com
```
✅ Debe aparecer el login de n8n.

---

## COMANDOS DE MANTENIMIENTO

```powershell
# Logs en tiempo real
docker compose logs n8n -f
docker compose logs postgres -f

# Reiniciar todo
docker compose restart

# Backup de la base de datos
$fecha = Get-Date -Format "yyyy-MM-dd"
docker exec fenix_postgres pg_dump -U fenix_admin fenix_db | Out-File "C:\fenix\backups\backup_$fecha.sql"

# Apagar el stack
docker compose down
```

---

## 🏭 CHECKLIST: Migración a Windows Server 2025 (Producción)

- [ ] Instalar Docker Desktop en Windows Server 2025
- [ ] Copiar carpeta `C:\fenix\` completa al nuevo servidor
- [ ] Hacer backup final: `docker exec fenix_postgres pg_dump -U fenix_admin fenix_db > backup_final.sql`
- [ ] Actualizar `.env` con dominio definitivo / IP pública
- [ ] `docker compose up -d` en nuevo servidor
- [ ] Restaurar backup de datos
- [ ] Configurar Cloudflare con dominio propio (grupotrujano.com.mx)
- [ ] Apagar servidor anterior

**Tiempo estimado de migración: ~2 horas**

---

## 📋 Resumen de Puertos

| Servicio | Puerto | Acceso |
|----------|--------|--------|
| PostgreSQL | 5432 | Solo interno (NO exponer) |
| n8n / API | 5678 | Cloudflare Tunnel → HTTPS |
| PWA Fénix (Fase 2) | 3000 | Cloudflare Tunnel → HTTPS |
