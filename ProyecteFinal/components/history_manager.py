import streamlit as st
import pandas as pd
from datetime import datetime

class HistoryManager:
    def __init__(self):
        if 'historial_traducciones' not in st.session_state:
            st.session_state.historial_traducciones = []

    def guardar_traduccion(self, audio_nombre, texto_original, texto_traducido,
                         config_origen, config_destino):
        """Guarda una traducción en el historial (AMPLIACIÓN)"""
        traduccion_info = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'audio_original': audio_nombre,
            'idioma_origen': config_origen.get('idioma_detectado', config_origen['idioma_stt']),
            'texto_original': texto_original,
            'idioma_destino': config_destino['idioma'],
            'texto_traducido': texto_traducido,
            'voz_destino': config_destino['voz']
        }
        
        st.session_state.historial_traducciones.append(traduccion_info)

    def mostrar_historial(self):
        """Muestra el historial y opción de descarga CSV (AMPLIACIÓN)"""
        if st.session_state.historial_traducciones:
            st.markdown("---")
            st.subheader("📊 Historial de Traducciones")
            
            # Mostrar tabla resumida
            historial_df = pd.DataFrame(st.session_state.historial_traducciones[::-1])
            st.dataframe(
                historial_df[['timestamp', 'idioma_origen', 'idioma_destino', 'texto_original']],
                use_container_width=True
            )
            
            # Botón descarga CSV
            csv = historial_df.to_csv(index=False)
            st.download_button(
                "📥 Descargar Historial (CSV)",
                csv,
                f"historial_traducciones_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True
            )