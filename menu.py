"""
Sistema de Detección EPP con YOLO
Menú Principal - Gestión de detecciones en tiempo real y por video
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import cv2


class MenuPrincipal:
    """Menú interactivo para el sistema de detección EPP"""
    
    def __init__(self):
        self.model_path = self.buscar_modelo()
        self.running = True
        
    def buscar_modelo(self):
        """Busca el modelo disponible"""
        modelos_posibles = [
            "best.pt",
            "best.onnx",
            "../best.pt",
            "C:\\Users\\Angel Del C\\Desktop\\OroParaIA\\best.pt"
        ]
        
        for modelo in modelos_posibles:
            if Path(modelo).exists():
                return modelo
        
        return None
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_menu(self):
        """Muestra el menú principal"""
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 15 + "🛡️  SISTEMA DE DETECCIÓN EPP 🛡️")
        print("=" * 70)
        print()
        
        if self.model_path:
            print(f"📦 Modelo actual: {self.model_path}")
        else:
            print("⚠️  Advertencia: No se encontró ningún modelo")
        
        print()
        print("-" * 70)
        print("  [1] 📹 Detección en Tiempo Real (Cámara)")
        print("  [2] 🎬 Detección por Video Configurable")
        print("  [3] 🚨 Alerta de EPP Faltante (Cámara/Video)")
        print("  [4] ⚙️  Optimizar Modelo para Jetson Nano")
        print("  [5] 📊 Cambiar Modelo")
        print("  [6] ❌ Salir")
        print("-" * 70)
        print()
    
    def deteccion_tiempo_real(self):
        """Ejecuta detección en tiempo real con la cámara"""
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 20 + "📹 DETECCIÓN EN TIEMPO REAL")
        print("=" * 70)
        print()
        
        if not self.model_path:
            print("❌ Error: No hay modelo disponible")
            input("\nPresiona Enter para continuar...")
            return
        
        print(f"🔄 Cargando modelo: {self.model_path}")
        print()
        
        try:
            # Cargar modelo
            model = YOLO(self.model_path)
            print("✅ Modelo cargado correctamente")
            print()
            
            # Abrir cámara
            print("📷 Iniciando cámara...")
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("❌ Error: No se puede acceder a la cámara")
                input("\nPresiona Enter para continuar...")
                return
            
            print("✅ Cámara iniciada")
            print()
            print("-" * 70)
            print("💡 Instrucciones:")
            print("   • Presiona [ESC] para salir")
            print("   • Presiona [S] para tomar captura")
            print("-" * 70)
            print()
            input("Presiona Enter para comenzar...")
            
            frame_count = 0
            captures_dir = Path("captures")
            captures_dir.mkdir(exist_ok=True)
            
            while cap.isOpened():
                # Leer frame del video (IGUAL que main.py)
                ret, frame = cap.read()
                if not ret:
                    print("⚠️  No se pudo leer el frame")
                    break
                
                # Realizar inferencia de YOLO (IGUAL que main.py)
                results = model(frame)
                
                # Extraer resultados anotados (IGUAL que main.py)
                annotated_frame = results[0].plot()
                
                # Agregar contador de frames
                frame_count += 1
                cv2.putText(annotated_frame, f"Frame: {frame_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated_frame, "ESC: Salir | S: Captura", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Mostrar frame
                cv2.imshow("Detección EPP - Tiempo Real", annotated_frame)
                
                # Controles de teclado
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    print("\n🛑 Deteniendo detección...")
                    break
                elif key == ord('s') or key == ord('S'):  # Captura
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    capture_path = captures_dir / f"capture_{timestamp}.jpg"
                    cv2.imwrite(str(capture_path), annotated_frame)
                    print(f"📸 Captura guardada: {capture_path}")
            
            # Limpiar
            cap.release()
            cv2.destroyAllWindows()
            
            print("\n✅ Detección finalizada")
            print(f"📊 Total de frames procesados: {frame_count}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def deteccion_por_video(self):
        """Ejecuta detección configurable sobre un archivo de video"""
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 15 + "🎬 DETECCIÓN POR VIDEO CONFIGURABLE")
        print("=" * 70)
        print()
        
        if not self.model_path:
            print("❌ Error: No hay modelo disponible")
            input("\nPresiona Enter para continuar...")
            return
        
        # PASO 1: Configurar clases a detectar
        clases_objetivo = self._configurar_clases_interactivo()
        
        if clases_objetivo is None:
            print("\n❌ Configuración cancelada")
            input("\nPresiona Enter para continuar...")
            return
        
        # PASO 2: Solicitar ruta del video
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 20 + "📁 SELECCIÓN DE VIDEO")
        print("=" * 70)
        print()
        if clases_objetivo:
            print(f"🎯 Detectando: {', '.join(clases_objetivo[:5])}{'...' if len(clases_objetivo) > 5 else ''}")
        else:
            print("🎯 Detectando: TODAS las clases")
        print()
        print("Ingresa la ruta del video a procesar:")
        print("(Puedes arrastrar el archivo aquí)")
        print()
        video_path = input("Ruta del video: ").strip().strip('"')
        
        if not Path(video_path).exists():
            print(f"\n❌ Error: No se encuentra el archivo {video_path}")
            input("\nPresiona Enter para continuar...")
            return
        
        print()
        print("-" * 70)
        print("⚙️  OPCIONES DE PROCESAMIENTO")
        print("-" * 70)
        
        print("\n¿Guardar video procesado? (s/n): ", end="")
        guardar_video = input().lower().strip() == 's'
        
        print("¿Mostrar video durante procesamiento? (s/n): ", end="")
        mostrar_video = input().lower().strip() == 's'
        
        print("Umbral de confianza (0.1-1.0, recomendado 0.25-0.35): ", end="")
        try:
            conf_threshold = float(input())
            if conf_threshold < 0.1 or conf_threshold > 1.0:
                conf_threshold = 0.25
        except:
            conf_threshold = 0.25
        
        print()
        print("-" * 70)
        print("🔄 Iniciando procesamiento...")
        print("-" * 70)
        print()
        
        # PASO 3: Procesar video con funcionalidad dual
        self._procesar_video_configurable(
            video_path=video_path,
            clases_objetivo=clases_objetivo,
            conf_threshold=conf_threshold,
            guardar_video=guardar_video,
            mostrar_video=mostrar_video
        )
        
        input("\nPresiona Enter para continuar...")
    
    def _deteccion_basica_video(self, video_path, guardar_video, mostrar_video, skip_frames):
        """Detección básica de video - SIMPLIFICADO como main.py"""
        print("\n🔄 Cargando modelo...")
        model = YOLO(self.model_path)
        print("✅ Modelo cargado\n")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print("❌ Error al abrir el video")
            return
        
        # Información del video
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📊 FPS: {fps} | Resolución: {width}x{height} | Frames: {total_frames}")
        print(f"⚙️  Procesando cada {skip_frames} frame(s)")
        print()
        
        # Video de salida
        out = None
        if guardar_video:
            output_path = Path("detections") / f"output_{Path(video_path).stem}.mp4"
            output_path.parent.mkdir(exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            print(f"💾 Guardando en: {output_path}")
        
        print("🎬 Procesando video...")
        if mostrar_video:
            print("   Presiona 'Q' para detener")
        print()
        
        frame_number = 0
        processed = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_number += 1
            
            # Saltar frames si es necesario
            if skip_frames > 1 and frame_number % skip_frames != 0:
                if out:
                    out.write(frame)
                continue
            
            # Realizar inferencia de YOLO (IGUAL que main.py)
            results = model(frame)
            
            # Extraer resultados anotados (IGUAL que main.py)
            annotated_frame = results[0].plot()
            
            processed += 1
            
            if out:
                out.write(annotated_frame)
            
            if mostrar_video:
                cv2.imshow('Procesando Video', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            if processed % 30 == 0 and processed > 0:
                progress = (frame_number / total_frames) * 100
                print(f"  Progreso: {progress:.1f}% ({frame_number}/{total_frames}) - Procesados: {processed}")
        
        cap.release()
        if out:
            out.release()
            print(f"\n✅ Video guardado: {output_path}")
        if mostrar_video:
            cv2.destroyAllWindows()
        
        print(f"✅ Procesamiento completado: {processed} frames procesados")
    
    def optimizar_modelo(self):
        """Optimiza el modelo para Jetson Nano"""
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 18 + "⚙️  OPTIMIZACIÓN DE MODELO")
        print("=" * 70)
        print()
        
        if not self.model_path:
            print("❌ Error: No hay modelo disponible")
            input("\nPresiona Enter para continuar...")
            return
        
        print(f"📦 Modelo a optimizar: {self.model_path}")
        print()
        print("-" * 70)
        print("Este proceso exportará el modelo a:")
        print("  • ONNX (Compatible, recomendado)")
        print("  • TensorRT (Máximo rendimiento en Jetson)")
        print()
        print("⚠️  NOTA: La conversión a TensorRT solo funciona")
        print("   correctamente en la Jetson Nano")
        print("-" * 70)
        print()
        
        confirmacion = input("¿Continuar con la optimización? (s/n): ")
        
        if confirmacion.lower().strip() != 's':
            print("\n❌ Optimización cancelada")
            input("\nPresiona Enter para continuar...")
            return
        
        print()
        print("🔄 Iniciando optimización...")
        print()
        
        try:
            from Optimized_model import optimize_model_for_jetson
            
            optimize_model_for_jetson(self.model_path, "yolo11s_jetson")
            
            print("\n✅ Optimización completada")
            
        except Exception as e:
            print(f"\n❌ Error durante la optimización: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def _configurar_clases_interactivo(self):
        """Configuración interactiva de clases para detección"""
        # Clases disponibles
        CLASES_DISPONIBLES = {
            'EPP': ['Gloves', 'Goggles', 'Hardhat', 'Mask', 'Safety Vest'],
            'NO_EPP': ['NO-Gloves', 'NO-Goggles', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest'],
            'OTROS': ['Person', 'Fall-Detected', 'Ladder', 'Safety Cone']
        }
        
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 15 + "🎯 CONFIGURACIÓN DE CLASES A DETECTAR")
        print("=" * 70)
        print()
        
        # Mostrar todas las clases
        todas_clases = []
        idx = 1
        
        print("🟢 EPP (Equipo de Protección Personal):")
        for clase in CLASES_DISPONIBLES['EPP']:
            print(f"   [{idx:2d}] {clase}")
            todas_clases.append(clase)
            idx += 1
        
        print()
        print("🔴 NO-EPP (Sin Equipo):")
        for clase in CLASES_DISPONIBLES['NO_EPP']:
            print(f"   [{idx:2d}] {clase}")
            todas_clases.append(clase)
            idx += 1
        
        print()
        print("🟡 Otros:")
        for clase in CLASES_DISPONIBLES['OTROS']:
            print(f"   [{idx:2d}] {clase}")
            todas_clases.append(clase)
            idx += 1
        
        print()
        print("=" * 70)
        print("💡 COMANDOS DISPONIBLES:")
        print("=" * 70)
        print("  • Número (1-14)  → Agregar/Remover esa clase")
        print("  • 'todo'         → Agregar todas las clases")
        print("  • 'ver'          → Ver tu lista actual")
        print("  • 'limpiar'      → Vaciar la lista")
        print("  • 'iniciar'      → Comenzar detección")
        print("  • 'cancelar'     → Volver al menú")
        print("=" * 70)
        print()
        
        clases_seleccionadas = []
        
        while True:
            # Mostrar estado actual
            if clases_seleccionadas:
                print(f"\n📋 Clases seleccionadas ({len(clases_seleccionadas)}):")
                print(f"   {', '.join(clases_seleccionadas)}")
            else:
                print(f"\n📋 Lista vacía (0 clases seleccionadas)")
            
            comando = input("\n➤ Comando: ").strip().lower()
            
            if comando == 'iniciar':
                if not clases_seleccionadas:
                    print("\n⚠️  No has seleccionado ninguna clase.")
                    print("¿Detectar TODAS las clases? (s/n): ", end="")
                    if input().lower().strip() == 's':
                        return None  # None = detectar todo
                    else:
                        continue
                return clases_seleccionadas
            
            elif comando == 'cancelar':
                return None
            
            elif comando == 'todo':
                clases_seleccionadas = todas_clases.copy()
                print(f"✅ Se agregaron TODAS las clases ({len(clases_seleccionadas)})")
            
            elif comando == 'ver':
                if clases_seleccionadas:
                    print("\n" + "="*50)
                    print("📋 TU LISTA ACTUAL:")
                    print("="*50)
                    for i, clase in enumerate(clases_seleccionadas, 1):
                        print(f"   {i:2d}. {clase}")
                    print("="*50)
                else:
                    print("\n❌ La lista está vacía")
            
            elif comando == 'limpiar':
                clases_seleccionadas.clear()
                print("✅ Lista limpiada")
            
            else:
                try:
                    num = int(comando)
                    if 1 <= num <= len(todas_clases):
                        clase = todas_clases[num - 1]
                        if clase in clases_seleccionadas:
                            clases_seleccionadas.remove(clase)
                            print(f"➖ Removido: {clase}")
                        else:
                            clases_seleccionadas.append(clase)
                            print(f"✅ Agregado: {clase}")
                    else:
                        print(f"❌ Número fuera de rango (1-{len(todas_clases)})")
                except ValueError:
                    print("❌ Comando no reconocido")
                    print("   Usa: número, 'todo', 'ver', 'limpiar', 'iniciar' o 'cancelar'")
    
    def cambiar_modelo(self):
        """Permite cambiar el modelo a utilizar"""
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 22 + "📊 CAMBIAR MODELO")
        print("=" * 70)
        print()
        
        print("Ingresa la ruta del modelo (.pt, .onnx, .engine):")
        print("(Puedes arrastrar el archivo aquí)")
        print()
        nuevo_modelo = input("Ruta del modelo: ").strip().strip('"')
        
        if not Path(nuevo_modelo).exists():
            print(f"\n❌ Error: No se encuentra el archivo {nuevo_modelo}")
            input("\nPresiona Enter para continuar...")
            return
        
        # Verificar que sea un modelo válido
        extensiones_validas = ['.pt', '.onnx', '.engine']
        if not any(nuevo_modelo.endswith(ext) for ext in extensiones_validas):
            print(f"\n⚠️  Advertencia: El archivo no tiene una extensión reconocida")
            print(f"   Extensiones válidas: {', '.join(extensiones_validas)}")
            confirmacion = input("\n¿Continuar de todas formas? (s/n): ")
            if confirmacion.lower().strip() != 's':
                print("\n❌ Cambio cancelado")
                input("\nPresiona Enter para continuar...")
                return
        
        self.model_path = nuevo_modelo
        print(f"\n✅ Modelo cambiado correctamente")
        print(f"📦 Nuevo modelo: {self.model_path}")
        
        input("\nPresiona Enter para continuar...")
    
    def alerta_epp_faltante(self):
        """Sistema de alerta de EPP faltante"""
        self.limpiar_pantalla()
        print("=" * 70)
        print(" " * 18 + "🚨 ALERTA DE EPP FALTANTE")
        print("=" * 70)
        print()
        
        if not self.model_path:
            print("❌ Error: No hay modelo disponible")
            input("\nPresiona Enter para continuar...")
            return
        
        print("📹 Selecciona la fuente:")
        print("  [1] Cámara en tiempo real")
        print("  [2] Archivo de video")
        print()
        
        opcion = input("Opción (1-2): ").strip()
        
        if opcion == '1':
            source = 0
        elif opcion == '2':
            print()
            print("📁 Ingresa la ruta del video:")
            source = input("Ruta: ").strip().strip('"')
            if not Path(source).exists():
                print(f"\n❌ Error: No se encuentra el archivo {source}")
                input("\nPresiona Enter para continuar...")
                return
        else:
            print("\n❌ Opción no válida")
            input("\nPresiona Enter para continuar...")
            return
        
        try:
            from alerta_epp_faltante import main_video_alertas
            main_video_alertas(self.model_path, source)
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar(self):
        """Bucle principal del menú"""
        while self.running:
            self.mostrar_menu()
            
            try:
                opcion = input("Selecciona una opción (1-6): ").strip()
                
                if opcion == '1':
                    self.deteccion_tiempo_real()
                elif opcion == '2':
                    self.deteccion_por_video()
                elif opcion == '3':
                    self.alerta_epp_faltante()
                elif opcion == '4':
                    self.optimizar_modelo()
                elif opcion == '5':
                    self.cambiar_modelo()
                elif opcion == '6':
                    self.limpiar_pantalla()
                    print("\n👋 ¡Hasta pronto!")
                    print()
                    self.running = False
                else:
                    print("\n⚠️  Opción no válida. Intenta de nuevo.")
                    input("\nPresiona Enter para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupción detectada")
                print("¿Deseas salir? (s/n): ", end="")
                if input().lower().strip() == 's':
                    self.running = False
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                input("\nPresiona Enter para continuar...")


def main():
    """Función principal"""
    try:
        menu = MenuPrincipal()
        menu.ejecutar()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
