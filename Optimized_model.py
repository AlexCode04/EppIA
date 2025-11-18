"""
Script para optimizar YOLO11s a TensorRT para Jetson Nano
Asegúrate de tener instalado: ultralytics, torch
"""

from ultralytics import YOLO
import torch

def optimize_model_for_jetson(model_path, output_name="yolo11s_optimized"):
    """
    Convierte el modelo YOLO11s a diferentes formatos optimizados
    
    Args:
        model_path: Ruta al modelo .pt original
        output_name: Nombre base para los archivos de salida
    """
    
    print("=" * 60)
    print("OPTIMIZACIÓN DE YOLO11s PARA JETSON NANO")
    print("=" * 60)
    
    # Cargar el modelo
    print(f"\n1. Cargando modelo desde: {model_path}")
    model = YOLO(model_path)
    
    # Opción 1: Exportar a ONNX (Intermedio, recomendado primero)
    print("\n2. Exportando a ONNX...")
    try:
        onnx_path = model.export(
            format="onnx",
            dynamic=False,  # False para mejor optimización en Jetson
            simplify=True,  # Simplificar el grafo
            opset=12  # Versión compatible
        )
        print(f"   ✓ Modelo ONNX guardado: {onnx_path}")
    except Exception as e:
        print(f"   ✗ Error exportando ONNX: {e}")
    
    # Opción 2: Exportar a TensorRT (Mejor rendimiento en Jetson)
    # NOTA: Esto debe ejecutarse EN LA JETSON NANO para mejor compatibilidad
    print("\n3. Exportando a TensorRT...")
    print("   IMPORTANTE: Para mejores resultados, ejecuta esto en la Jetson Nano")
    try:
        engine_path = model.export(
            format="engine",  # TensorRT
            half=True,  # FP16 para mejor velocidad en Jetson
            workspace=4,  # GB de memoria de trabajo
            verbose=False,
            simplify=True
        )
        print(f"   ✓ Motor TensorRT guardado: {engine_path}")
    except Exception as e:
        print(f"   ✗ Error exportando TensorRT: {e}")
        print(f"   → Esto es normal si no estás en Jetson Nano")
        print(f"   → Usa el archivo ONNX y conviértelo en la Jetson")
    
    # Información del modelo
    print("\n4. Información del modelo:")
    print(f"   - Clases: {len(model.names)}")
    print(f"   - Nombres de clases: {model.names}")
    
    # Guardar información de las clases
    class_info = {
        'names': model.names,
        'epp_classes': ['Gloves', 'Goggles', 'Hardhat', 'Mask', 'Safety Vest'],
        'no_epp_classes': ['NO-Gloves', 'NO-Goggles', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest']
    }
    
    import json
    with open(f"{output_name}_classes.json", 'w') as f:
        json.dump(class_info, f, indent=2)
    print(f"   ✓ Información de clases guardada: {output_name}_classes.json")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE ARCHIVOS GENERADOS:")
    print("=" * 60)
    print(f"1. {output_name}.onnx - Modelo ONNX (usa este si TensorRT falla)")
    print(f"2. {output_name}.engine - Motor TensorRT (mejor rendimiento)")
    print(f"3. {output_name}_classes.json - Información de clases")
    
    print("\n" + "=" * 60)
    print("SIGUIENTE PASO:")
    print("=" * 60)
    print("Si estás en tu PC:")
    print("  1. Transfiere los archivos .onnx y .json a la Jetson Nano")
    print("  2. En la Jetson, ejecuta la conversión a TensorRT (opcional pero recomendado)")
    print("\nSi estás en la Jetson Nano:")
    print("  ¡Listo! Usa el archivo .engine para máximo rendimiento")
    print("=" * 60)


def convert_onnx_to_tensorrt_on_jetson(onnx_path):
    """
    Ejecutar SOLO en Jetson Nano para convertir ONNX a TensorRT
    """
    print("\n🚀 Conversión ONNX → TensorRT en Jetson Nano")
    
    try:
        model = YOLO(onnx_path)
        engine_path = model.export(
            format="engine",
            half=True,  # FP16
            workspace=2,  # Reducido para Jetson Nano
            verbose=True
        )
        print(f"✓ Motor TensorRT creado: {engine_path}")
        return engine_path
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


if __name__ == "__main__":
    import sys
    
    # Configuración
    MODEL_PATH = "yolo11s.pt"  # Cambia esto a la ruta de tu modelo
    
    if len(sys.argv) > 1:
        MODEL_PATH = sys.argv[1]
    
    print(f"\n📦 Modelo a optimizar: {MODEL_PATH}")
    print(f"💻 Plataforma actual: {'Jetson' if torch.cuda.is_available() else 'PC'}")
    
    # Ejecutar optimización
    optimize_model_for_jetson(MODEL_PATH, "yolo11s_jetson")
    
    print("\n✅ Proceso completado!")
    print("\nPara ejecutar la conversión en Jetson Nano desde ONNX:")
    print("  python optimize_yolo_jetson.py --convert-onnx yolo11s_jetson.onnx")