import os
import requests
from dotenv import load_dotenv

# ==========================================
# CONFIGURACIÓN INICIAL Y SEGURIDAD
# ==========================================
# Carga las variables de entorno desde el archivo .env de forma segura.
# Esto evita exponer credenciales (API Keys) directamente en el código fuente.
load_dotenv()

API_KEY = os.getenv("APALPACA_API_KEY")
SECRET_KEY = os.getenv("APALACA_SECRET_KEY")
# URL base para Paper Trading (entorno de pruebas gratuito con $100k virtuales)
BASE_URL = os.getenv("APALACA_BASE_URL", "https://paper-api.alpaca.markets")
# URL base para el servicio de datos en tiempo real de Alpaca
DATA_URL = "https://data.alpaca.markets"

# Cabeceras de autenticación obligatorias requeridas por la API de Alpaca en cada petición HTTP
HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

# ==========================================
# MÓDULO 1: GESTIÓN DE CUENTA Y BALANCE
# ==========================================
def obtener_estado_cuenta():
    """
    Consulta el saldo actual, efectivo disponible (cash) y el valor total
    del portafolio en la cuenta de pruebas de Alpaca.
    """
    url = f"{BASE_URL}/v2/account"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        cuenta = response.json()
        print("--- ESTADO DE LA CUENTA ---")
        print(f"Estado de la cuenta: {cuenta.get('status')}")
        print(f"Efectivo disponible (Cash): ${float(cuenta.get('cash')):.2f}")
        print(f"Valor total del portafolio: ${float(cuenta.get('portfolio_value')):.2f}\n")
    else:
        print(f"Error al consultar la cuenta ({response.status_code}): {response.text}")

# ==========================================
# MÓDULO 2: DATOS DE MERCADO (PRECIOS)
# ==========================================
def obtener_precio_actual(simbolo: str):
    """
    Consulta el último precio operado en tiempo real para un activo específico (ej. 'AAPL').
    Retorna el precio como un número decimal (float) o None si ocurre un fallo.
    """
    url = f"{DATA_URL}/v2/stocks/{simbolo}/trades/latest"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        datos = response.json()
        precio = datos.get("trade", {}).get("p")
        return float(precio) if precio else None
    else:
        print(f"Error al obtener cotización para {simbolo}: {response.status_code} - {response.text}")
        return None

# ==========================================
# MÓDULO 3: GESTIÓN DE ORDEN Y CONTROL DE RIESGO
# ==========================================
def enviar_orden_con_riesgo(simbolo: str, cantidad: int, lado: str, porcentaje_stop_loss: float = 0.02, porcentaje_take_profit: float = 0.04):
    """
    Envía una orden al mercado incorporando gestión de riesgo automatizada (Stop-Loss y Take-Profit).
    Utiliza 'bracket orders' para proteger el capital de forma nativa a nivel del broker.
    
    Parámetros:
    - simbolo: Ticker del activo (ej. 'AAPL')
    - cantidad: Número de acciones a operar
    - lado: 'buy' para compra o 'sell' para venta
    - porcentaje_stop_loss: Margen de pérdida tolerado (ej. 0.02 = 2% de caída máxima)
    - porcentaje_take_profit: Margen de ganancia objetivo (ej. 0.04 = 4% de ganancia esperada)
    """
    # 1. Consultamos el precio actual del activo para calcular los límites matemáticos de riesgo
    precio_actual = obtener_precio_actual(simbolo)
    if not precio_actual:
        print("No se pudo obtener el precio para calcular los límites de riesgo. Operación cancelada.")
        return

    # 2. Calculamos los precios objetivo basándonos en la dirección de la operación (compra)
    if lado == "buy":
        precio_sl = round(precio_actual * (1 - porcentaje_stop_loss), 2)  # Precio por debajo de entrada (Stop-Loss)
        precio_tp = round(precio_actual * (1 + porcentaje_take_profit), 2) # Precio por encima de entrada (Take-Profit)
    else:
        # Lógica inversa en caso de posiciones cortas (short selling)
        precio_sl = round(precio_actual * (1 + porcentaje_stop_loss), 2)
        precio_tp = round(precio_actual * (1 - porcentaje_take_profit), 2)

    url = f"{BASE_URL}/v2/orders"
    
    # 3. Estructura de la orden avanzada ('order_class': 'bracket') que adjunta las protecciones
    payload = {
        "symbol": simbolo,
        "qty": str(cantidad),
        "side": lado,
        "type": "market",
        "time_in_force": "gtc",         # Good 'Til Canceled (la orden permanece vigente hasta ejecutarse o cancelarse)
        "order_class": "bracket",       # Permite vincular la orden principal con el Stop-Loss y Take-Profit
        "stop_loss": {
            "stop_price": str(precio_sl)
        },
        "take_profit": {
            "limit_price": str(precio_tp)
        }
    }
    
    print(f"Enviando orden protegida para {simbolo} a un precio base aprox. de ${precio_actual:.2f}...")
    print(f"--> [Riesgo] Stop-Loss fijado en: ${precio_sl} (-{porcentaje_stop_loss*100}%)")
    print(f"--> [Objetivo] Take-Profit fijado en: ${precio_tp} (+{porcentaje_take_profit*100}%)")

    response = requests.post(url, json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        orden = response.json()
        print(f"\n[ÉXITO] Orden protegida enviada correctamente al broker.")
        print(f"ID de Orden Principal: {orden.get('id')}")
        print(f"Estado de la orden: {orden.get('status')}\n")
    else:
        print(f"Error al enviar la orden protegida: {response.status_code} - {response.text}")

# ==========================================
# MÓDULO 4: MONITOREO DE POSICIONES
# ==========================================
def consultar_posiciones():
    """
    Consulta y lista todas las posiciones activas actualmente en la cartera,
    mostrando las ganancias o pérdidas no realizadas en tiempo real (P&L).
    """
    url = f"{BASE_URL}/v2/positions"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        posiciones = response.json()
        print("--- POSICIONES ABIERTAS EN CARTERA ---")
        if not posiciones:
            print("No hay posiciones abiertas en este momento.\n")
        else:
            for p in posiciones:
                print(f"Activo: {p.get('symbol')} | Cantidad: {p.get('qty')} | P&L no realizado: ${float(p.get('unrealized_pl')):.2f}")
            print()
    else:
        print(f"Error al consultar posiciones: {response.status_code} - {response.text}")

# ==========================================
# FLUJO DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("Iniciando ejecución del script de trading...\n")
    
    # 1. Validar fondos disponibles en la cuenta virtual
    obtener_estado_cuenta()
    
    # 2. Definir el activo de prueba y consultar su cotización
    simbolo_objetivo = "AAPL"
    precio = obtener_precio_actual(simbolo_objetivo)
    
    if precio:
        print(f"Cotización actual detectada de {simbolo_objetivo}: ${precio:.2f}\n")
    
    # 3. Enviar orden de compra simulada con un 2% de Stop-Loss y 4% de Take-Profit automático
    enviar_orden_con_riesgo(
        simbolo=simbolo_objetivo, 
        cantidad=1, 
        lado="buy", 
        porcentaje_stop_loss=0.02, 
        porcentaje_take_profit=0.04
    )
    
    # 4. Consultar el estado de la cartera tras aplicar la orden y sus protecciones
    consultar_posiciones()