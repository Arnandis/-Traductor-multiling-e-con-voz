import streamlit as st
from utils.http_client import HTTPClient  
import os


class SpeechService:
    def __init__(self):
        self.speech_key = os.environ.get("AZURE_SPEECH_KEY") or st.secrets.get("AZURE_SPEECH_KEY")
        self.region = os.environ.get("AZURE_REGION") or st.secrets.get("AZURE_REGION")
        self.http_client = HTTPClient(max_retries=3, base_backoff=1.5)  #Usar HTTPClient
    
    # st.cache_data maneja todo automáticamente
    @st.cache_data(ttl=3600, show_spinner="Transcribiendo audio...")
    def transcribir_audio(_self, audio_bytes, idioma):
        url = f"https://{_self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": _self.speech_key,
            "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000"
        }
        
        #USAR HTTPClient CON REINTENTOS
        response = _self.http_client.post_with_retry(
            url, 
            params={"language": idioma}, 
            headers=headers, 
            data=audio_bytes
        )
        
        if response and response.status_code == 200:
            data = response.json()
            return data.get("DisplayText") or data.get("Text")
        elif response:
            return f"Error: {response.status_code} - {response.text}"
        else:
            return "Error: No se pudo conectar con el servicio de voz"
    
    # utilitzem el cache de streamlit
    @st.cache_data(ttl=3600, show_spinner="Generando audio...")
    def sintetizar_voz(_self, texto, voz):
        url = f"https://{_self.region}.tts.speech.microsoft.com/cognitiveservices/v1"
        idioma_voz = "-".join(voz.split('-')[:2])
        
        ssml = f"""<speak version='1.0' xml:lang='{idioma_voz}'>
            <voice name='{voz}'>{texto}</voice>
        </speak>"""
        
        headers = {
            "Ocp-Apim-Subscription-Key": _self.speech_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
        }
        
        #USAR HTTPClient CON REINTENTOS
        response = _self.http_client.post_with_retry(
            url, 
            headers=headers, 
            data=ssml.encode("utf-8")
        )
        
        if response and response.status_code == 200:
            return response.content
        else:
            error_msg = f"Error en síntesis de voz: {response.status_code if response else 'Sin respuesta'}"
            print(error_msg)
            return None