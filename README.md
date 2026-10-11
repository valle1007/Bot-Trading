# 🤖 Personal Algorithmic Trading Bot

Un corredor personal automatizado diseñado bajo principios de ingeniería de software de misión crítica. Este sistema ejecuta estrategias cuantitativas, gestiona riesgos en tiempo real y opera de forma desatendida en entornos de pruebas (*Paper Trading*).

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.10+
* **Librerías:** Pandas, Requests, TA (Análisis Técnico)
* **Broker / API:** Alpaca Markets REST & WebSockets
* **Infraestructura:** Docker / VPS (Preparado para despliegue 24/7)

## 🛡️ Características de Seguridad y Gestión de Riesgo
* **Position Sizing Automatizado:** Cálculo dinámico para limitar la exposición por operación.
* **Stop Loss Dinámico:** Protección obligatoria integrada por cada orden ejecutada.
* **Kill-Switch de Emergencia:** Apagado automático, cancelación de órdenes pendientes y liquidación de posiciones ante umbrales de pérdida diaria críticos.

## 📁 Estructura del Proyecto
```text
personal-trading-bot/
├── venv/                  # Entorno virtual aislado (ignorado en git)
├── .env                   # Credenciales privadas de API (ignorado en git)
├── .gitignore             # Archivos excluidos del control de versiones
├── main.py                # Script principal de conexión y ejecución
└── README.md              # Documentación del proyecto