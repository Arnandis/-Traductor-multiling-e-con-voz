import streamlit as st
from utils.http_client import HTTPClient  #Importar HTTPClient
import os

class TranslationService:
    def __init__(self):
        self.translator_key = os.environ.get("AZURE_TRANSLATOR_KEY") or st.secrets.get("AZURE_TRANSLATOR_KEY")
        self.region = os.environ.get("AZURE_REGION") or st.secrets.get("AZURE_REGION")
        self.http_client = HTTPClient(max_retries=3, base_backoff=1.5)  #Usar HTTPClient
        
        # Mapeo de idiomas
        self.mapeo_idiomas_stt = {
            'es': 'es-ES', 'en': 'en-US', 'fr': 'fr-FR', 
            'de': 'de-DE', 'it': 'it-IT', 'pt': 'pt-BR', 'ja': 'ja-JP'
        }
        
        self.voces_por_idioma = {
            "es": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural", "es-MX-DaliaNeural"],
            "en": ["en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural"],
            "fr": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
            "de": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
            "it": ["it-IT-ElsaNeural", "it-IT-DiegoNeural"],
            "pt": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"],
            "ja": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"]
        }

    def configurar_idioma_origen(self):
        """Configuración del idioma de origen con detección automática"""
        st.subheader("🎤 Configuración Entrada")
        
        deteccion_automatica = st.checkbox(
            "🔍 Detectar idioma automáticamente", 
            value=True,
            help="El sistema detectará automáticamente el idioma del audio"
        )
        
        if deteccion_automatica:
            st.info("🌐 El idioma se detectará automáticamente")
            idioma_stt = "es-ES"  # Idioma por defecto para transcripción inicial
            idioma_traduccion = "es"  # Idioma por defecto para traducción
        else:
            idioma_stt = st.selectbox(
                "Idioma del audio original:",
                ["es-ES", "en-US", "fr-FR", "de-DE", "it-IT", "pt-BR", "ja-JP"]
            )
            # Extraer código simple para traducción (es-ES → es)
            idioma_traduccion = idioma_stt.split('-')[0]
        
        return {
            'deteccion_automatica': deteccion_automatica,
            'idioma_stt': idioma_stt,
            'idioma_traduccion': idioma_traduccion,
            'idioma_detectado': None
        }

    def configurar_idioma_destino(self):
        """Configuración del idioma de destino"""
        st.subheader("🌍 Configuración Salida")
        
        idioma_destino = st.selectbox(
            "Idioma de destino:",
            ["es", "en", "fr", "de", "it", "pt", "ja"]
        )
        
        voz = st.selectbox(
            "Voz para audio:",
            self.voces_por_idioma.get(idioma_destino, ["es-ES-ElviraNeural"])
        )
        
        return {
            'idioma': idioma_destino,
            'voz': voz
        }

    # st.cache_data maneja todo automáticamente
    @st.cache_data(ttl=3600)
    def detectar_idioma(_self, texto):
        """Detección automática de idioma (AMPLIACIÓN)"""
        url = "https://api.cognitive.microsofttranslator.com/detect"
        params = {"api-version": "3.0"}
        headers = {
            "Ocp-Apim-Subscription-Key": _self.translator_key,
            "Ocp-Apim-Subscription-Region": _self.region,
            "Content-Type": "application/json"
        }
        body = [{"text": texto}]

        #USAR HTTPClient CON REINTENTOS
        response = _self.http_client.post_with_retry(
            url, 
            params=params, 
            headers=headers, 
            json=body
        )
        
        if response and response.status_code == 200:
            resultado = response.json()
            idioma = resultado[0]['language']
            confianza = resultado[0].get('score', 0)
            return idioma, confianza
        return None, 0

    def detectar_y_mejorar_idioma(self, audio_bytes, texto_original, config_origen):
        """Mejora la transcripción detectando el idioma automáticamente"""
        from services.speech_service import SpeechService
        
        st.write("**🔍 Detectando idioma...**")
        idioma_detectado, confianza = self.detectar_idioma(texto_original)
        
        if idioma_detectado and confianza > 0.7:
            st.success(f"🌐 Idioma detectado: **{idioma_detectado}** ({confianza:.1%})")
            
            # Re-transcribir con el idioma correcto si es diferente
            idioma_stt_correcto = self.mapeo_idiomas_stt.get(idioma_detectado, "es-ES")
            if idioma_stt_correcto != config_origen['idioma_stt']:
                st.write("**🔄 Mejorando transcripción...**")
                speech_service = SpeechService()
                texto_mejorado = speech_service.transcribir_audio(audio_bytes, idioma_stt_correcto)
                if texto_mejorado and not texto_mejorado.startswith("Error"):
                    # Actualizar config_origen con el idioma detectado
                    config_origen['idioma_detectado'] = idioma_detectado
                    config_origen['idioma_traduccion'] = idioma_detectado  # Usar idioma detectado para traducción
                    return texto_mejorado, config_origen
        
        # Si no se detecta o no mejora, mantener configuración original
        config_origen['idioma_detectado'] = idioma_detectado
        return texto_original, config_origen

    # st.cache_data maneja todo automáticamente
    @st.cache_data(ttl=3600, show_spinner="Traduciendo texto...")
    def traducir_texto(_self, texto, idioma_origen, idioma_destino):
        """Traduce texto entre idiomas"""
        url = "https://api.cognitive.microsofttranslator.com/translate"
        params = {
            "api-version": "3.0",
            "from": idioma_origen,
            "to": idioma_destino
        }
        headers = {
            "Ocp-Apim-Subscription-Key": _self.translator_key,
            "Ocp-Apim-Subscription-Region": _self.region,
            "Content-Type": "application/json"
        }
        body = [{"text": texto}]

        #USAR HTTPClient CON REINTENTOS
        response = _self.http_client.post_with_retry(
            url, 
            params=params, 
            headers=headers, 
            json=body
        )
        
        if response and response.status_code == 200:
            resultado = response.json()
            return resultado[0]['translations'][0]['text']
        elif response:
            return f"Error: {response.status_code} - {response.text}"
        else:
            return "Error: No se pudo conectar con el servicio de traducción"