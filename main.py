import os
import requests
import pandas as pd
from dotenv import load_dotenv

# ==========================================
# CONFIGURACIÓN INICIAL Y SEGURIDAD
# ==========================================
load_dotenv()

API_KEY = os.getenv("APALPACA_API_KEY")
SECRET_KEY = os.getenv("APALACA_SECRET_KEY")
BASE_URL = os.getenv("APALACA_BASE_URL", "https://paper-api.alpaca.markets")
DATA_URL = "https://data.alpaca.markets"

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

# ==========================================
# MÓDULO 1: GESTIÓN DE CUENTA Y BALANCE
# ==========================================
def obtener_estado_cuenta():
    """Consulta el saldo y estado actual de la cuenta en Alpaca."""
    url = f"{BASE_URL}/v2/account"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        cuenta = response.json()
        print("--- ESTADO DE LA CUENTA ---")
        print(f"Estado: {cuenta.get('status')}")
        print(f"Efectivo disponible: ${float(cuenta.get('cash')):.2f}")
        print(f"Valor total del portafolio: ${float(cuenta.get('portfolio_value')):.2f}\n")
    else:
        print(f"Error al consultar la cuenta: {response.status_code} - {response.text}")

# ==========================================
# MÓDULO 2: DATOS HISTÓRICOS Y MERCADO
# ==========================================
def obtener_historico_velas(simbolo: str, timeframe: str = "1Hour", limit: int = 100):
    """
    Descarga el historial de precios por hora de un activo desde Alpaca.
    Incluye 'feed=iex' obligatorio para cuentas de Paper Trading gratuitas.
    """
    url = f"{DATA_URL}/v2/stocks/{simbolo}/bars"
    params = {
        "timeframe": timeframe,
        "limit": limit,
        "feed": "iex"  # Canal de datos gratuito para cuentas Paper
    }
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Protegemos contra valores nulos (None) usando 'or []'
        bars = data.get("bars") or []
        print(f"[DEBUG] Barras horarias obtenidas exitosamente: {len(bars)}")
        
        if not bars:
            print(f"[ADVERTENCIA] No se recibieron datos de barras para {simbolo}. Respuesta: {data}")
            return None
        
        # Convertimos los datos a un DataFrame de Pandas
        df = pd.DataFrame(bars)
        df = df.rename(columns={"c": "close", "o": "open", "h": "high", "l": "low", "v": "volume"})
        return df
    else:
        print(f"Error al obtener histórico de {simbolo}: {response.status_code} - {response.text}")
        return None

# ==========================================
# MÓDULO 3: ESTRATEGIA ALGORÍTMICA (CRUCE DE MEDIAS)
# ==========================================
def evaluar_estrategia_cruce_medias(simbolo: str):
    """
    Estrategia de Cruce de Medias Móviles Simples (SMA 10 y SMA 30) en velas horarias.
    """
    print(f"Analizando mercado para {simbolo}...")
    df = obtener_historico_velas(simbolo, timeframe="1Hour", limit=100)
    
    if df is None or len(df) < 30:
        print("Datos insuficientes para calcular las medias móviles.")
        return "hold"

    # Cálculo de Medias Móviles Simples (SMA)
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_30'] = df['close'].rolling(window=30).mean()

    # Tomar valores actuales y anteriores
    precio_actual = df['close'].iloc[-1]
    sma_10_actual = df['sma_10'].iloc[-1]
    sma_30_actual = df['sma_30'].iloc[-1]
    
    sma_10_anterior = df['sma_10'].iloc[-2]
    sma_30_anterior = df['sma_30'].iloc[-2]

    print(f"Precio actual: ${precio_actual:.2f} | SMA 10: ${sma_10_actual:.2f} | SMA 30: ${sma_30_actual:.2f}")

    # Señal de Compra / Venta
    if sma_10_anterior <= sma_30_anterior and sma_10_actual > sma_30_actual:
        print("--> ¡Señal detectada: COMPRA (Cruce alcista)!")
        return "buy"
    elif sma_10_anterior >= sma_30_anterior and sma_10_actual < sma_30_actual:
        print("--> ¡Señal detectada: VENTA (Cruce bajista)!")
        return "sell"
    else:
        print("--> Sin cruce de tendencia. Manteniendo posición (HOLD).")
        return "hold"

# ==========================================
# MÓDULO 4: EJECUCIÓN DE ÓRDENES
# ==========================================
def enviar_orden(simbolo: str, cantidad: int, lado: str):
    """Envía una orden al mercado de pruebas de Alpaca."""
    url = f"{BASE_URL}/v2/orders"
    payload = {
        "symbol": simbolo,
        "qty": str(cantidad),
        "side": lado,
        "type": "market",
        "time_in_force": "gtc"
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        orden = response.json()
        print(f"\n[ÉXITO] Orden de {lado.upper()} enviada correctamente.")
        print(f"ID de Orden: {orden.get('id')}")
        print(f"Estado: {orden.get('status')}\n")
    else:
        print(f"Error al enviar la orden: {response.status_code} - {response.text}")

# ==========================================
# FLUJO PRINCIPAL DE EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    print("Iniciando bot de trading con estrategia algorítmica...\n")
    
    obtener_estado_cuenta()
    activo = "AAPL"
    
    senal = evaluar_estrategia_cruce_medias(activo)
    
    if senal == "buy":
        print(f"Ejecutando orden de compra autónoma para {activo}...")
        enviar_orden(activo, cantidad=1, lado="buy")
    elif senal == "sell":
        print(f"Ejecutando orden de venta autónoma para {activo}...")
        enviar_orden(activo, cantidad=1, lado="sell")
    else:
        print("El bot determinó que no hay condiciones óptimas para operar en este momento.")