from ultralytics import YOLO
import cv2
from pathlib import Path
import os

class MenuEPP:
    def __init__(self):
        self.model_path = r"C:\Users\Angel Del C\Desktop\OroParaIA\PruebaRealTime\best.pt"
        self.clases = [
            'Fall-Detected', 'Gloves', 'Goggles', 'Hardhat', 'Ladder',
            'Mask', 'NO-Gloves', 'NO-Goggles', 'NO-Hardhat', 'NO-Mask',
            'NO-Safety Vest', 'Person', 'Safety Cone', 'Safety Vest'
        ]
        
        # ============================================================
        # CONFIGURACIÓN DE PINES GPIO JETSON NANO (BCM)
        # ============================================================
        
        # --- PINES PARA LCD I2C (4 pines) ---
        # La pantalla LCD con módulo I2C usa comunicación I2C
        # Bus I2C-1 de Jetson Nano (pines físicos 3 y 5):
        self.lcd_sda = 2          # GPIO 2 (Pin físico 3) - SDA (Datos I2C)
        self.lcd_scl = 3          # GPIO 3 (Pin físico 5) - SCL (Clock I2C)
        # Alimentación LCD:
        # VCC -> Pin físico 1 o 17 (3.3V) o Pin físico 2 o 4 (5V según tu LCD)
        # GND -> Pin físico 6, 9, 14, 20, 25, 30, 34, 39 (cualquier GND)
        
        # --- PIN PARA SERVO MOTOR (1 pin + alimentación) ---
        self.servo_pin = 33       # GPIO 13 (Pin físico 33) - PWM para control servo
        # Alimentación Servo:
        # VCC -> Pin físico 2 o 4 (5V)
        # GND -> Pin físico 6, 9, 14, 20, 25, 30, 34, 39 (cualquier GND)
        
        # --- PINES DE SEÑAL DIGITAL (8 pines totales) ---
        # Cuando SE DETECTAN todas las clases (EPP completo):
        self.pines_detectado = [
            17,  # GPIO 17 (Pin físico 11) - Señal 1 (HIGH cuando detectado)
            18,  # GPIO 18 (Pin físico 12) - Señal 2 (HIGH cuando detectado)
            27,  # GPIO 27 (Pin físico 13) - Señal 3 (HIGH cuando detectado)
            22   # GPIO 22 (Pin físico 15) - Señal 4 (HIGH cuando detectado)
        ]
        
        # Cuando NO se detectan todas las clases (EPP incompleto):
        self.pines_no_detectado = [
            23,  # GPIO 23 (Pin físico 16) - Señal 5 (HIGH cuando NO detectado)
            24,  # GPIO 24 (Pin físico 18) - Señal 6 (HIGH cuando NO detectado)
            25,  # GPIO 25 (Pin físico 22) - Señal 7 (HIGH cuando NO detectado)
            5    # GPIO 5  (Pin físico 29) - Señal 8 (HIGH cuando NO detectado)
        ]
        
        # Dirección I2C de la pantalla LCD (normalmente 0x27 o 0x3F)
        self.lcd_address = 0x27
        
    def limpiar(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _inicializar_hardware(self):
        """Inicializa LCD, Servo y GPIO"""
        try:
            # Inicializar I2C para LCD
            import board
            import busio
            from adafruit_character_lcd.character_lcd_i2c import Character_LCD_I2C
            
            i2c = busio.I2C(board.SCL, board.SDA)
            self.lcd = Character_LCD_I2C(i2c, 16, 2, self.lcd_address)  # LCD 16x2
            self.lcd.clear()
            self.lcd.message = "Sistema EPP\nIniciando..."
            
            # Inicializar GPIO
            import Jetson.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            
            # Configurar servo
            GPIO.setup(self.servo_pin, GPIO.OUT)
            self.servo_pwm = GPIO.PWM(self.servo_pin, 50)  # 50Hz para servo
            self.servo_pwm.start(0)
            
            # Configurar pines de detección
            for pin in self.pines_detectado:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            for pin in self.pines_no_detectado:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            
            return True
        except Exception as e:
            print(f"⚠️  Hardware no disponible: {e}")
            self.lcd = None
            self.servo_pwm = None
            return False
    
    def _mostrar_lcd(self, linea1, linea2=""):
        """Muestra mensaje en LCD 16x2"""
        if self.lcd:
            try:
                self.lcd.clear()
                self.lcd.message = f"{linea1[:16]}\n{linea2[:16]}"
            except:
                pass
    
    def _abrir_puerta(self):
        """Abre la puerta moviendo el servo a 90 grados"""
        if self.servo_pwm:
            try:
                # Ciclo de trabajo para 90 grados: ~7.5%
                self.servo_pwm.ChangeDutyCycle(7.5)
                import time
                time.sleep(1)
                self.servo_pwm.ChangeDutyCycle(0)  # Detener señal
            except:
                pass
    
    def _cerrar_puerta(self):
        """Cierra la puerta moviendo el servo a 0 grados"""
        if self.servo_pwm:
            try:
                # Ciclo de trabajo para 0 grados: ~2.5%
                self.servo_pwm.ChangeDutyCycle(2.5)
                import time
                time.sleep(1)
                self.servo_pwm.ChangeDutyCycle(0)  # Detener señal
            except:
                pass
    
    def _activar_pines_acceso_permitido(self):
        """Activa pines cuando SE detectan todos los EPP (pines_detectado=HIGH)"""
        try:
            import Jetson.GPIO as GPIO
            # Activar pines de detección (señal HIGH = EPP completo)
            for pin in self.pines_detectado:
                GPIO.output(pin, GPIO.HIGH)
            # Desactivar pines de no detección
            for pin in self.pines_no_detectado:
                GPIO.output(pin, GPIO.LOW)
        except:
            pass
    
    def _activar_pines_acceso_denegado(self):
        """Activa pines cuando NO se detectan todos los EPP (pines_no_detectado=HIGH)"""
        try:
            import Jetson.GPIO as GPIO
            # Desactivar pines de detección
            for pin in self.pines_detectado:
                GPIO.output(pin, GPIO.LOW)
            # Activar pines de no detección (señal HIGH = falta EPP)
            for pin in self.pines_no_detectado:
                GPIO.output(pin, GPIO.HIGH)
        except:
            pass
    
    def menu_principal(self):
        while True:
            self.limpiar()
            print("=" * 60)
            print(" " * 18 + "🔧 DETECCIÓN EPP")
            print("=" * 60)
            print(f"\n📦 Modelo: {Path(self.model_path).name}")
            print(f"🔌 Hardware Jetson Nano:")
            print(f"   • LCD I2C: SDA=GPIO{self.lcd_sda}, SCL=GPIO{self.lcd_scl}")
            print(f"   • Servo Motor: GPIO{self.servo_pin}")
            print(f"   • Pines Detectado (HIGH): {self.pines_detectado}")
            print(f"   • Pines NO Detectado (HIGH): {self.pines_no_detectado}")
            print("\n  [1] 📹 Detección en Vivo (Cámara)")
            print("  [2] 🎬 Detección por Video")
            print("  [3] 🔧 Test Hardware (LCD + Servo)")
            print("  [4] ⚡ Optimizar Modelo (ONNX)")
            print("  [5] 🔄 Cambiar Modelo")
            print("  [0] ❌ Salir")
            print("\n" + "=" * 60)
            
            opcion = input("\n➤ Selecciona: ").strip()
            
            if opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            elif opcion == '1':
                self.deteccion_vivo()
            elif opcion == '2':
                self.deteccion_video()
            elif opcion == '3':
                self.test_hardware()
            elif opcion == '4':
                self.optimizar()
            elif opcion == '5':
                self.cambiar_modelo()
            else:
                print("\n❌ Opción inválida")
                input("\nPresiona Enter...")
    
    def deteccion_vivo(self):
        """Detección en tiempo real con cámara"""
        self.limpiar()
        print("=" * 60)
        print(" " * 18 + "📹 DETECCIÓN EN VIVO")
        print("=" * 60)
        
        # Configuración
        print("\nUmbral de confianza (0.1-1.0, default 0.25): ", end="")
        try:
            conf = float(input().strip() or "0.25")
            conf = max(0.1, min(1.0, conf))
        except:
            conf = 0.25
        
        print("Tamaño de imagen (default 640, menor=más rápido): ", end="")
        try:
            imgsz = int(input().strip() or "640")
            imgsz = max(320, min(1280, (imgsz // 32) * 32))
        except:
            imgsz = 640
        
        print(f"\n🔄 Cargando modelo (conf={conf}, imgsz={imgsz})...")
        
        try:
            model = YOLO(self.model_path)
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("❌ No se puede acceder a la cámara")
                input("\nPresiona Enter...")
                return
            
            print("✅ Iniciando detección")
            print("💡 Presiona 'q' para salir\n")
            
            # Inicializar hardware
            hw_ok = self._inicializar_hardware()
            
            if hw_ok:
                self._mostrar_lcd("Sistema EPP", "Detectando...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detección con resize
                results = model(frame, conf=conf, imgsz=imgsz, verbose=False)
                annotated = results[0].plot()
                
                # Control de hardware según detecciones
                if hw_ok:
                    if len(results[0].boxes) > 0:
                        self._activar_pines_acceso_permitido()
                        self._mostrar_lcd("ACCESO PERMITIDO", "EPP Completo OK")
                        self._abrir_puerta()
                    else:
                        self._activar_pines_acceso_denegado()
                        self._mostrar_lcd("ACCESO DENEGADO", "Falta EPP!")
                        self._cerrar_puerta()
                
                cv2.imshow('Detección en Vivo - Presiona Q para salir', annotated)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if hw_ok:
                self._mostrar_lcd("Sistema EPP", "Detenido")
                self._cleanup_gpio()
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona Enter...")
    
    def deteccion_video(self):
        """Detección en video con selección de clases"""
        self.limpiar()
        print("=" * 60)
        print(" " * 18 + "🎬 DETECCIÓN POR VIDEO")
        print("=" * 60)
        
        # Paso 1: Seleccionar clases
        clases_objetivo = self._seleccionar_clases()
        if clases_objetivo is None:
            return
        
        # Paso 2: Configuración
        self.limpiar()
        print("=" * 60)
        print(" " * 18 + "⚙️  CONFIGURACIÓN")
        print("=" * 60)
        
        if clases_objetivo:
            print(f"\n🎯 Clases: {', '.join(clases_objetivo[:3])}{'...' if len(clases_objetivo) > 3 else ''} ({len(clases_objetivo)} total)")
        else:
            print("\n🎯 Clases: TODAS (14)")
        
        print("\nRuta del video: ", end="")
        video = input().strip().strip('"')
        
        if not Path(video).exists():
            print("\n❌ Archivo no encontrado")
            input("\nPresiona Enter...")
            return
        
        print("Umbral de confianza (default 0.25): ", end="")
        try:
            conf = float(input().strip() or "0.25")
            conf = max(0.1, min(1.0, conf))
        except:
            conf = 0.25
        
        print("Tamaño de imagen para detección (default 640, mayor=más lento): ", end="")
        try:
            imgsz = int(input().strip() or "640")
            # Validar que sea múltiplo de 32
            imgsz = max(320, min(1280, (imgsz // 32) * 32))
        except:
            imgsz = 640
        
        print("¿Guardar video procesado? (s/n): ", end="")
        guardar = input().lower().strip() == 's'
        
        print("¿Mostrar durante procesamiento? (s/n): ", end="")
        mostrar = input().lower().strip() == 's'
        
        # Paso 3: Procesar
        print("\n" + "-" * 60)
        print("🔄 Procesando...")
        print("-" * 60 + "\n")
        
        self._procesar_video(video, clases_objetivo, conf, guardar, mostrar, imgsz)
        
        input("\nPresiona Enter...")
    
    def _seleccionar_clases(self):
        """Interfaz para seleccionar clases a detectar"""
        self.limpiar()
        print("=" * 60)
        print(" " * 15 + "🎯 SELECCIÓN DE CLASES")
        print("=" * 60)
        print("\n📋 CLASES DISPONIBLES:\n")
        
        for i, clase in enumerate(self.clases, 1):
            print(f"  [{i:2d}] {clase}")
        
        print("\n" + "=" * 60)
        print("💡 COMANDOS:")
        print("  • Número (1-14)  → Agregar/Quitar clase")
        print("  • 'todos'        → Todas las clases")
        print("  • 'ver'          → Ver selección actual")
        print("  • 'limpiar'      → Vaciar selección")
        print("  • 'listo'        → Iniciar procesamiento")
        print("  • 'salir'        → Volver al menú")
        print("=" * 60)
        
        seleccionadas = []
        
        while True:
            # Mostrar estado
            if seleccionadas:
                print(f"\n📌 Seleccionadas ({len(seleccionadas)}): {', '.join(seleccionadas[:3])}{'...' if len(seleccionadas) > 3 else ''}")
            else:
                print("\n📌 Ninguna clase seleccionada")
            
            cmd = input("\n➤ Comando: ").strip().lower()
            
            if cmd == 'listo':
                if not seleccionadas:
                    print("\n⚠️  No has seleccionado nada")
                    print("¿Usar TODAS las clases? (s/n): ", end="")
                    if input().lower() == 's':
                        return None  # None = todas las clases
                    continue
                return seleccionadas
            
            elif cmd == 'salir':
                return None
            
            elif cmd == 'todos':
                seleccionadas = self.clases.copy()
                print(f"✅ {len(seleccionadas)} clases agregadas")
            
            elif cmd == 'ver':
                if seleccionadas:
                    print("\n" + "="*50)
                    for i, c in enumerate(seleccionadas, 1):
                        print(f"  {i}. {c}")
                    print("="*50)
                else:
                    print("\n❌ Lista vacía")
            
            elif cmd == 'limpiar':
                seleccionadas.clear()
                print("✅ Lista limpiada")
            
            else:
                try:
                    num = int(cmd)
                    if 1 <= num <= len(self.clases):
                        clase = self.clases[num - 1]
                        if clase in seleccionadas:
                            seleccionadas.remove(clase)
                            print(f"➖ Quitado: {clase}")
                        else:
                            seleccionadas.append(clase)
                            print(f"✅ Agregado: {clase}")
                    else:
                        print(f"❌ Número fuera de rango (1-{len(self.clases)})")
                except:
                    print("❌ Comando no válido")
    
    def _procesar_video(self, video_path, clases_objetivo, conf, guardar, mostrar, imgsz=640):
        """Procesa el video con las clases seleccionadas"""
        try:
            model = YOLO(self.model_path)
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print("❌ No se puede abrir el video")
                return
            
            # Info del video
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"📊 Video: {width}x{height} @ {fps}fps | {total_frames} frames")
            print(f"🎯 Confianza: {conf} | Tamaño detección: {imgsz}px")
            print(f"💡 Nota: Frames se redimensionan a {imgsz}px para detección, luego se restauran")
            
            # Video de salida
            writer = None
            if guardar:
                output_path = f"output_{Path(video_path).stem}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                print(f"💾 Guardando en: {output_path}")
            
            # Inicializar hardware
            hw_ok = self._inicializar_hardware()
            
            if hw_ok:
                self._mostrar_lcd("Procesando", "Video...")
            
            # Contadores
            detecciones_totales = {clase: 0 for clase in self.clases}
            frame_num = 0
            todas_detectadas_count = 0
            
            print("\n🔄 Procesando frames...\n")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_num += 1
                
                # Detección con tamaño de imagen especificado
                results = model(frame, conf=conf, imgsz=imgsz, verbose=False)
                
                # Filtrar por clases objetivo
                if clases_objetivo:
                    boxes = results[0].boxes
                    clases_detectadas = set()
                    
                    for box in boxes:
                        clase_nombre = model.names[int(box.cls[0])]
                        if clase_nombre in clases_objetivo:
                            clases_detectadas.add(clase_nombre)
                            detecciones_totales[clase_nombre] += 1
                    
                    # Verificar si se detectaron TODAS las clases objetivo
                    todas_detectadas = len(clases_detectadas) == len(clases_objetivo)
                    
                    if todas_detectadas:
                        todas_detectadas_count += 1
                    
                    # Control hardware
                    if hw_ok:
                        if todas_detectadas:
                            self._activar_pines_acceso_permitido()
                            self._mostrar_lcd("ACCESO PERMITIDO", "Puede entrar")
                            self._abrir_puerta()
                        else:
                            self._activar_pines_acceso_denegado()
                            faltante = list(faltantes)[0] if faltantes else "EPP"
                            self._mostrar_lcd("ACCESO DENEGADO", f"Falta {faltante[:12]}")
                            self._cerrar_puerta()
                    
                    # Frame anotado
                    annotated = results[0].plot()
                    
                    # Panel de estado
                    panel_color = (0, 255, 0) if todas_detectadas else (0, 165, 255)  # Verde o naranja
                    cv2.rectangle(annotated, (10, 10), (400, 100), panel_color, -1)
                    cv2.rectangle(annotated, (10, 10), (400, 100), (255, 255, 255), 2)
                    
                    status = "✅ TODAS DETECTADAS" if todas_detectadas else "🔍 BUSCANDO..."
                    cv2.putText(annotated, status, (20, 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    
                    faltantes = set(clases_objetivo) - clases_detectadas
                    if faltantes:
                        texto = f"Faltan: {', '.join(list(faltantes)[:2])}"
                        cv2.putText(annotated, texto, (20, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
                else:
                    # Detectar todas las clases
                    annotated = results[0].plot()
                    for box in results[0].boxes:
                        clase_nombre = model.names[int(box.cls[0])]
                        detecciones_totales[clase_nombre] += 1
                
                # Guardar frame
                if writer:
                    writer.write(annotated)
                
                # Mostrar
                if mostrar:
                    cv2.imshow('Procesando Video - Presiona Q para salir', annotated)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\n⚠️  Procesamiento cancelado por el usuario")
                        break
                
                # Progreso
                if frame_num % 30 == 0:
                    progreso = (frame_num / total_frames) * 100
                    print(f"⏳ Frame {frame_num}/{total_frames} ({progreso:.1f}%)")
            
            # Limpiar
            cap.release()
            if writer:
                writer.release()
            cv2.destroyAllWindows()
            
            if hw_ok:
                self._mostrar_lcd("Proceso", "Completado")
                self._cleanup_gpio()
            
            # Resumen
            print("\n" + "=" * 60)
            print("✅ PROCESAMIENTO COMPLETADO")
            print("=" * 60)
            print(f"\n📊 Frames procesados: {frame_num}/{total_frames}")
            
            if clases_objetivo:
                print(f"\n🎯 Frames con TODAS las clases: {todas_detectadas_count} ({(todas_detectadas_count/frame_num)*100:.1f}%)")
                print("\n📈 Detecciones por clase:")
                for clase in clases_objetivo:
                    count = detecciones_totales[clase]
                    print(f"  • {clase}: {count}")
            else:
                print("\n📈 Detecciones totales:")
                for clase, count in detecciones_totales.items():
                    if count > 0:
                        print(f"  • {clase}: {count}")
            
            if guardar:
                print(f"\n💾 Video guardado: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def optimizar(self):
        """Optimiza el modelo a formato ONNX"""
        self.limpiar()
        print("=" * 60)
        print(" " * 15 + "⚡ OPTIMIZACIÓN DE MODELO")
        print("=" * 60)
        print("\n🔄 Exportando modelo a formato ONNX...")
        print("(Compatible con Jetson Nano)\n")
        
        try:
            model = YOLO(self.model_path)
            output = model.export(format='onnx', imgsz=640, simplify=True)
            print(f"\n✅ Modelo exportado: {output}")
            print("\n💡 Para usar el modelo ONNX:")
            print(f"   model = YOLO('{output}')")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona Enter...")
    
    def test_hardware(self):
        """Prueba el LCD, Servo y pines GPIO"""
        self.limpiar()
        print("=" * 60)
        print(" " * 15 + "🔧 TEST DE HARDWARE")
        print("=" * 60)
        print("\n🔄 Inicializando hardware...\n")
        
        try:
            if self._inicializar_hardware():
                print("✅ Hardware inicializado correctamente\n")
                
                # Test LCD
                print("📟 Probando LCD...")
                self._mostrar_lcd("TEST LCD", "Linea 2")
                import time
                time.sleep(2)
                
                # Test Servo - Abrir
                print("🚪 Probando Servo - Abriendo puerta...")
                self._mostrar_lcd("Probando Servo", "Abriendo...")
                self._abrir_puerta()
                time.sleep(2)
                
                # Test Servo - Cerrar
                print("🚪 Probando Servo - Cerrando puerta...")
                self._mostrar_lcd("Probando Servo", "Cerrando...")
                self._cerrar_puerta()
                time.sleep(2)
                
                # Test pines de acceso permitido (señal HIGH)
                print("✅ Probando pines de acceso permitido (GPIOs 17,18,27,22 = HIGH)...")
                self._mostrar_lcd("ACCESO", "PERMITIDO")
                self._activar_pines_acceso_permitido()
                time.sleep(3)
                
                # Test pines de acceso denegado (señal HIGH)
                print("❌ Probando pines de acceso denegado (GPIOs 23,24,25,5 = HIGH)...")
                self._mostrar_lcd("ACCESO", "DENEGADO")
                self._activar_pines_acceso_denegado()
                time.sleep(3)
                
                # Apagar todo
                print("🔌 Apagando todos los pines...")
                self._mostrar_lcd("Test", "Completado")
                for pin in self.pines_detectado + self.pines_no_detectado:
                    try:
                        import Jetson.GPIO as GPIO
                        GPIO.output(pin, GPIO.LOW)
                    except:
                        pass
                
                time.sleep(1)
                self._cleanup_gpio()
                
                print("\n✅ Test completado exitosamente")
            else:
                print("❌ No se pudo inicializar el hardware")
                print("   Verifica conexiones y que estés en Jetson Nano")
                
        except Exception as e:
            print(f"\n❌ Error durante el test: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nPresiona Enter...")
    
    def cambiar_modelo(self):
        """Cambia la ruta del modelo"""
        self.limpiar()
        print("=" * 60)
        print(" " * 18 + "🔄 CAMBIAR MODELO")
        print("=" * 60)
        print(f"\n📦 Modelo actual: {self.model_path}\n")
        print("Nueva ruta del modelo (.pt o .onnx): ", end="")
        nueva_ruta = input().strip().strip('"')
        
        if Path(nueva_ruta).exists():
            self.model_path = nueva_ruta
            print(f"\n✅ Modelo actualizado: {Path(nueva_ruta).name}")
        else:
            print("\n❌ Archivo no encontrado")
        
        input("\nPresiona Enter...")
    
    def _cleanup_gpio(self):
        """Limpia la configuración GPIO"""
        try:
            import Jetson.GPIO as GPIO
            GPIO.cleanup()
        except:
            pass

if __name__ == "__main__":
    menu = MenuEPP()
    menu.menu_principal()
