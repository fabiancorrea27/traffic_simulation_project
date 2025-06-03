# Simulación de Flujo Vehicular en una Intersección

## 📋 Descripción

Este proyecto simula el flujo de vehículos en una intersección controlada por semáforos. Permite observar, de forma visual e interactiva, cómo los tiempos semafóricos afectan el tráfico vehicular. La herramienta está orientada al análisis y optimización de sistemas viales urbanos mediante algoritmos de inteligencia artificial.

## 🛠️ Requisitos

- Python 3.13.0 o superior
- Sistemas operativos: Windows 7 o superior (recomendado: Windows 11)
- Librerías necesarias:

  - `pygame`
  - `pygame_gui`
  - `networkx`
  - `matplotlib`

> Puedes instalar las dependencias ejecutando:

```bash
pip install pygame pygame_gui networkx matplotlib

```

## ▶️ Instrucciones de Uso

1.  Abre una consola y navega hasta la carpeta del proyecto.
2.  Ejecuta el programa con el siguiente comando:

    ```bash
    python main.py

    ```

3.  Controles disponibles en la interfaz:

    - **Iniciar**: Comienza la simulación.
    - **Detener**: Pausa la simulación y reinicia vehículos y semáforos.
    - **Optimización**: Ejecuta el algoritmo genético para ajustar automáticamente los tiempos semafóricos.
    - **x5 Velocidad**: Aumenta la velocidad de simulación.

      - Presiona nuevamente para restaurar la velocidad normal.

## ℹ️ Información Adicional

- La simulación se detiene automáticamente tras cinco minutos de ejecución.
- Al detenerse, los vehículos regresan a su posición inicial y los semáforos reinician su ciclo.
- Resultados detallados de la optimización se muestran en la consola.

### ⚙️ Personalización en el archivo `config`

Puedes modificar parámetros en el archivo `config` para ajustar el comportamiento del sistema:

#### GUI

- Espaciado entre elementos
- Títulos de las calles
- Ruta de los assets de los vehículos

#### Vehículos

- Ancho
- Velocidad de giro
- Velocidad de desplazamiento
- Espacio entre vehículos

#### Semáforos

- Radio del círculo indicador
- Distancia mínima de detención en rojo
- Tiempo por defecto en verde y amarillo
- Orden de cambio de luces

## 👥 Autores

- **Fabián Leonardo Correa Rojas**
- **Yeimmy Natalia Bernal Pulido**
- **Karen Yulieth Castro Chivatá**
