# 🔌 DIAGRAMA DE CONEXIONES - JETSON NANO

## 📋 Resumen de Hardware

### Componentes:
- **1x Pantalla LCD 16x2 con módulo I2C** (Dirección: 0x27 o 0x3F)
- **1x Servo Motor** (SG90 o similar, 5V)
- **8x LEDs** (4 Verdes para acceso permitido, 4 Rojos para acceso denegado)
- **8x Resistencias** 220Ω-330Ω (una por cada LED)
- **Cables Dupont** macho-hembra
- **Protoboard** (opcional para organización)

---

## 🖥️ PANTALLA LCD 16x2 CON I2C (4 Pines)

### Conexiones LCD I2C → Jetson Nano:

| Pin LCD | Pin Jetson Nano | GPIO BCM | Pin Físico | Función |
|---------|-----------------|----------|------------|---------|
| **VCC** | 5V              | -        | Pin 2 o 4  | Alimentación 5V |
| **GND** | GND             | -        | Pin 6, 9, 14, 20, 25, 30, 34 o 39 | Tierra |
| **SDA** | I2C1_SDA        | GPIO 2   | **Pin 3**  | Datos I2C |
| **SCL** | I2C1_SCL        | GPIO 3   | **Pin 5**  | Reloj I2C |

```
LCD I2C          Jetson Nano
┌─────────┐      ┌──────────┐
│   VCC   │ ───► │ Pin 2 (5V)   │
│   GND   │ ───► │ Pin 6 (GND)  │
│   SDA   │ ───► │ Pin 3 (GPIO2)│
│   SCL   │ ───► │ Pin 5 (GPIO3)│
└─────────┘      └──────────┘
```

---

## 🚪 SERVO MOTOR (3 Pines)

### Conexiones Servo → Jetson Nano:

| Cable Servo | Pin Jetson Nano | GPIO BCM | Pin Físico | Función |
|-------------|-----------------|----------|------------|---------|
| **Rojo/VCC**   | 5V           | -        | Pin 2 o 4  | Alimentación 5V |
| **Marrón/GND** | GND          | -        | Pin 6, 9, 14, etc. | Tierra |
| **Naranja/Señal** | PWM       | GPIO 13  | **Pin 33** | Señal PWM |

```
Servo Motor      Jetson Nano
┌─────────┐      ┌──────────┐
│ Rojo    │ ───► │ Pin 4 (5V)    │
│ Marrón  │ ───► │ Pin 9 (GND)   │
│ Naranja │ ───► │ Pin 33 (GPIO13)│
└─────────┘      └──────────┘
```

**⚠️ IMPORTANTE:** Si el servo consume mucha corriente, usa una **fuente externa de 5V** para alimentarlo y conecta solo la tierra (GND) común con Jetson Nano.

---

## 🔌 PINES DE SEÑAL DIGITAL - ACCESO PERMITIDO (4 Pines)

Estos pines envían señal **HIGH (3.3V)** cuando el sistema **detecta TODOS los EPP** seleccionados.

### Pines de Señal "Detectado" → Jetson Nano:

| Pin # | GPIO BCM | Pin Físico | Estado | Uso |
|-------|----------|------------|--------|-----|
| Señal 1 | GPIO 17 | **Pin 11** | HIGH cuando detectado | Conectar a tu circuito externo |
| Señal 2 | GPIO 18 | **Pin 12** | HIGH cuando detectado | Conectar a tu circuito externo |
| Señal 3 | GPIO 27 | **Pin 13** | HIGH cuando detectado | Conectar a tu circuito externo |
| Señal 4 | GPIO 22 | **Pin 15** | HIGH cuando detectado | Conectar a tu circuito externo |

```
Señal Digital (GPIO 17, 18, 27, 22)

  Pin 11/12/13/15 ──────► Tu circuito/controlador externo
  (3.3V cuando HIGH)      (Relés, PLCs, etc.)
       │
       └──────► GND común
```

**Características:**
- **Voltaje HIGH**: 3.3V
- **Voltaje LOW**: 0V
- **Corriente máxima**: 50mA por pin
- **Uso**: Conectar a relés, optoacopladores, PLCs, controladores externos

---

## 🔌 PINES DE SEÑAL DIGITAL - ACCESO DENEGADO (4 Pines)

Estos pines envían señal **HIGH (3.3V)** cuando el sistema **NO detecta todos los EPP** (faltan elementos).

### Pines de Señal "No Detectado" → Jetson Nano:

| Pin # | GPIO BCM | Pin Físico | Estado | Uso |
|-------|----------|------------|--------|-----|
| Señal 5 | GPIO 23 | **Pin 16** | HIGH cuando NO detectado | Conectar a tu circuito externo |
| Señal 6 | GPIO 24 | **Pin 18** | HIGH cuando NO detectado | Conectar a tu circuito externo |
| Señal 7 | GPIO 25 | **Pin 22** | HIGH cuando NO detectado | Conectar a tu circuito externo |
| Señal 8 | GPIO 5  | **Pin 29** | HIGH cuando NO detectado | Conectar a tu circuito externo |

```
Señal Digital (GPIO 23, 24, 25, 5)

  Pin 16/18/22/29 ──────► Tu circuito/controlador externo
  (3.3V cuando HIGH)      (Alarmas, indicadores, etc.)
       │
       └──────► GND común
```

**Características:**
- **Voltaje HIGH**: 3.3V
- **Voltaje LOW**: 0V
- **Corriente máxima**: 50mA por pin
- **Uso**: Conectar a alarmas, buzzer, relés de alerta, indicadores externos

---

## 📊 TABLA RESUMEN DE TODOS LOS PINES

| Componente | GPIO BCM | Pin Físico | Función |
|------------|----------|------------|---------|
| **LCD - SDA** | GPIO 2 | **Pin 3** | Datos I2C |
| **LCD - SCL** | GPIO 3 | **Pin 5** | Reloj I2C |
| **Servo - Señal** | GPIO 13 | **Pin 33** | Control PWM |
| **Señal 1 (Detectado)** | GPIO 17 | **Pin 11** | HIGH = Acceso Permitido |
| **Señal 2 (Detectado)** | GPIO 18 | **Pin 12** | HIGH = Acceso Permitido |
| **Señal 3 (Detectado)** | GPIO 27 | **Pin 13** | HIGH = Acceso Permitido |
| **Señal 4 (Detectado)** | GPIO 22 | **Pin 15** | HIGH = Acceso Permitido |
| **Señal 5 (No Detectado)** | GPIO 23 | **Pin 16** | HIGH = Acceso Denegado |
| **Señal 6 (No Detectado)** | GPIO 24 | **Pin 18** | HIGH = Acceso Denegado |
| **Señal 7 (No Detectado)** | GPIO 25 | **Pin 22** | HIGH = Acceso Denegado |
| **Señal 8 (No Detectado)** | GPIO 5 | **Pin 29** | HIGH = Acceso Denegado |

### Alimentación:
- **5V**: Pins 2, 4 (LCD, Servo)
- **3.3V**: Pins 1, 17 (no usado)
- **GND**: Pins 6, 9, 14, 20, 25, 30, 34, 39 (común para todos)

---

## 🎨 DIAGRAMA VISUAL JETSON NANO 40-PIN HEADER

```
        3.3V  [ 1] [ 2]  5V       ◄─ LCD VCC, Servo VCC
    I2C SDA   [ 3] [ 4]  5V       ◄─ LCD SDA (GPIO 2)
    I2C SCL   [ 5] [ 6]  GND      ◄─ LCD SCL (GPIO 3), GND común
             [ 7] [ 8]
        GND   [ 9] [10]            ◄─ Servo GND
   Señal 1    [11] [12] Señal 2    ◄─ GPIO 17, GPIO 18 (Detectado)
   Señal 3    [13] [14] GND        ◄─ GPIO 27 (Detectado)
   Señal 4    [15] [16] Señal 5    ◄─ GPIO 22, GPIO 23 (Detectado/No Detectado)
             [17] [18] Señal 6     ◄─ GPIO 24 (No Detectado)
             [19] [20] GND
             [21] [22] Señal 7     ◄─ GPIO 25 (No Detectado)
             [23] [24]
        GND   [25] [26]
             [27] [28]
   Señal 8    [29] [30] GND        ◄─ GPIO 5 (No Detectado)
             [31] [32]
Servo Signal  [33] [34] GND        ◄─ GPIO 13 (PWM)
             [35] [36]
             [37] [38]
        GND   [39] [40]
```

---

## ⚙️ CONFIGURACIÓN DE SOFTWARE

### 1. Instalar Dependencias en Jetson Nano:

```bash
# Instalar librerías GPIO
sudo pip3 install Jetson.GPIO

# Instalar librerías para LCD I2C
sudo pip3 install adafruit-circuitpython-charlcd
sudo pip3 install adafruit-blinka

# Habilitar I2C (si no está habilitado)
sudo apt-get install -y i2c-tools
sudo i2cdetect -y -r 1  # Detectar dispositivos I2C

# Dar permisos GPIO al usuario
sudo groupadd -f -r gpio
sudo usermod -a -G gpio $USER
```

### 2. Dirección I2C de tu LCD:

Detecta la dirección I2C de tu pantalla:

```bash
sudo i2cdetect -y -r 1
```

Salida típica:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --  ◄─ Tu LCD está en 0x27
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
...
```

Si tu LCD está en **0x3F** en lugar de **0x27**, modifica esta línea en `menu_simple.py`:

```python
self.lcd_address = 0x3F  # Cambiar de 0x27 a 0x3F
```

---

## 🧪 PROBAR EL HARDWARE

Ejecuta el test de hardware desde el menú:

```bash
python3 menu_simple.py
```

Selecciona opción **[3] Test Hardware** para verificar:
- ✅ LCD muestra mensajes
- ✅ Servo se abre y cierra
- ✅ LEDs verdes se encienden (acceso permitido)
- ✅ LEDs rojos se encienden (acceso denegado)

---

## 🚀 FUNCIONAMIENTO DEL SISTEMA

### Cuando SE DETECTAN TODOS los EPP:
1. **LCD muestra**: "ACCESO PERMITIDO" / "Puede entrar"
2. **Pines Detectado** (GPIO 17, 18, 27, 22) envían señal **HIGH (3.3V)**
3. **Servo Motor** abre la puerta (90°)
4. **Pines No Detectado** (GPIO 23, 24, 25, 5) envían señal **LOW (0V)**

### Cuando NO se detectan todos los EPP:
1. **LCD muestra**: "ACCESO DENEGADO" / "Falta [EPP]"
2. **Pines No Detectado** (GPIO 23, 24, 25, 5) envían señal **HIGH (3.3V)**
3. **Servo Motor** cierra la puerta (0°)
4. **Pines Detectado** (GPIO 17, 18, 27, 22) envían señal **LOW (0V)**

---

## 📝 NOTAS IMPORTANTES

1. **Pines de Señal Digital**: Los 8 pines GPIO envían señales de 3.3V (HIGH) o 0V (LOW). Puedes conectarlos a:
   - Relés (usa módulo de relé de 3.3V o con optoacoplador)
   - PLCs (verifica compatibilidad de voltaje)
   - Optoacopladores
   - Módulos LED externos
   - Controladores de alarma
   - **⚠️ Corriente máxima**: 50mA por pin

2. **Servo Motor**: Si tienes problemas con el servo, verifica:
   - Alimentación externa de 5V (si consume >500mA)
   - Frecuencia PWM correcta (50Hz)
   - Duty cycle: 2.5% = 0°, 7.5% = 90°, 12.5% = 180°

3. **LCD I2C**: Si no detecta el LCD:
   - Verifica cableado SDA/SCL
   - Ejecuta `sudo i2cdetect -y -r 1`
   - Ajusta contraste del LCD (potenciómetro en módulo I2C)

4. **Permisos**: Ejecuta con `sudo` si hay errores de permisos GPIO.

---

## 🔧 COMANDOS ÚTILES

```bash
# Ver estado de pines GPIO
sudo cat /sys/kernel/debug/gpio

# Detectar dispositivos I2C
sudo i2cdetect -y -r 1

# Ver logs del sistema
dmesg | grep -i gpio
dmesg | grep -i i2c

# Ejecutar con permisos GPIO
sudo python3 menu_simple.py
```

---

## 📞 SOPORTE

Si tienes problemas:
1. Verifica conexiones físicas
2. Ejecuta el test de hardware (Opción 3)
3. Revisa la dirección I2C del LCD
4. Asegúrate de tener permisos GPIO

---

**✅ Sistema listo para control de acceso con detección de EPP**
