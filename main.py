            # PARA BINARIAS 5m
            hora_ec = datetime.now(pytz.timezone('America/Guayaquil')).strftime("%H:%M:%S")
            accion_binaria = "CALL 📈" if buy_ok else "PUT 📉"
            direccion = "COMPRAR 🟢" if buy_ok else "VENDER 🔴"
            
            mensaje = f"""🔥 BINARIAS 85%+ PREMIUM {hora_ec} EC

{direccion} {par} {INTERVAL}
Señal: {accion_binaria}
💰 Precio: {precio:.5f}
📊 Estoc 13,3,3 K:{k:.1f} D:{d:.1f}
📈 RSI {rsi:.1f}
🎯 Confianza {conf}%

⏰ ENTRADA: Siguiente vela 5m
⏳ EXPIRACIÓN: 5 minutos
🛡️ Martingala: 1 nivel max

✅ ENTRAR AHORA"""
