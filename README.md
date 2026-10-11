# Bot de Trading Algorítmico con Alpaca Markets

Sistema modular desarrollado en Python para la ejecución automatizada de estrategias de trading en el entorno de pruebas (*Paper Trading*) de Alpaca Markets, utilizando dinero virtual ($100,000 USD simulados) y mecanismos integrados de gestión de riesgo.

---

## 🚀 Características Principales

1. **Autenticación y Seguridad:** Conexión cifrada y segura con la API de Alpaca utilizando variables de entorno (`.env`) excluidas del control de versiones.
2. **Monitoreo de Cuenta:** Consulta automatizada del saldo disponible (*Cash*), estado de la cuenta y valor total del portafolio.
3. **Datos de Mercado en Tiempo Real:** Extracción de cotizaciones precisas de activos (ej. AAPL) mediante endpoints oficiales de Alpaca Data.
4. **Gestión de Riesgo Avanzada (Bracket Orders):** Envío de órdenes al mercado vinculadas nativamente a límites automáticos de **Stop-Loss** (protección ante caídas) y **Take-Profit** (aseguramiento de ganancias).
5. **Control de Posiciones:** Monitoreo activo de la cartera y cálculo de ganancias/pérdidas no realizadas (*P&L*).

---

## 🛠️ Tecnologías y Requisitos

* **Python 3.10+**
* **Librerías principales:** 
  * `requests` (para peticiones HTTP a la API REST)
  * `python-dotenv` (para manejo seguro de credenciales)
* **Broker:** Alpaca Markets (API Paper Trading)

---

## ⚙️ Configuración e Instalación

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/valle1007/Bot-Trading.git](https://github.com/valle1007/Bot-Trading.git)
   cd Bot-Trading