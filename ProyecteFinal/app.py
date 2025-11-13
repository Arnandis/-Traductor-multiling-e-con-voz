import streamlit as st
from services.speech_service import SpeechService
from services.translation_service import TranslationService
from components.audio_input import AudioInput
from components.history_manager import HistoryManager

# Configuración de la página
st.set_page_config(
    page_title="Traductor Multilingüe con Voz",
    page_icon="🎙️", 
    layout="wide"
)

def main():
    st.title("🎙️ Traductor Multilingüe con Voz")
    st.markdown("**Voz → Texto → Traducción → Voz**")
    st.markdown("---")
    
    # Inicializar servicios
    speech_service = SpeechService()
    translation_service = TranslationService()
    history_manager = HistoryManager()
    
    # Configuración de idiomas
    col1, col2 = st.columns(2)
    with col1:
        config_origen = translation_service.configurar_idioma_origen()
    with col2:
        config_destino = translation_service.configurar_idioma_destino()
    
    # Entrada de audio
    st.subheader("🎤 Entrada de Audio")
    audio_bytes, audio_nombre = AudioInput.obtener_audio()
    
    # Procesamiento principal
    if audio_bytes:
        procesar_traduccion(
            audio_bytes, audio_nombre,
            config_origen, config_destino,
            speech_service, translation_service,
            history_manager
        )
    
    # Mostrar historial
    history_manager.mostrar_historial()

def procesar_traduccion(audio_bytes, audio_nombre, config_origen, 
                       config_destino, speech_service, 
                       translation_service, history_manager):
    
    if st.button("🚀 Ejecutar Traducción Completa", type="primary", use_container_width=True):
        with st.spinner("Procesando flujo completo..."):
            
            # PASO 1: Transcripción
            texto_original = speech_service.transcribir_audio(
                audio_bytes, config_origen['idioma_stt']
            )
            
            if texto_original and not texto_original.startswith("Error"):
                st.success(f"✅ **Texto transcrito:** {texto_original}")
                
                # Detección automática de idioma (ampliación)
                if config_origen['deteccion_automatica']:
                    texto_original, config_origen = translation_service.detectar_y_mejorar_idioma(
                        audio_bytes, texto_original, config_origen
                    )
                
                # PASO 2: Traducción
                texto_traducido = translation_service.traducir_texto(
                    texto_original, 
                    config_origen['idioma_traduccion'], 
                    config_destino['idioma']
                )
                
                if texto_traducido and not texto_traducido.startswith("Error"):
                    st.success(f"✅ **Texto traducido:** {texto_traducido}")
                    
                    # PASO 3: Síntesis de voz
                    audio_resultado = speech_service.sintetizar_voz(
                        texto_traducido, config_destino['voz']
                    )
                    
                    if audio_resultado:
                        st.success("🎉 **Traducción completada!**")
                        
                        # Mostrar resultados
                        mostrar_resultados_finales(
                            audio_nombre, texto_original, texto_traducido,
                            config_origen, config_destino, audio_resultado
                        )
                        
                        # Guardar en historial (ampliación)
                        history_manager.guardar_traduccion(
                            audio_nombre, texto_original, texto_traducido,
                            config_origen, config_destino
                        )
                    else:
                        st.error("❌ Error generando audio")
                else:
                    st.error("❌ Error en traducción")
            else:
                st.error("❌ Error en transcripción")

def mostrar_resultados_finales(audio_nombre, texto_original, texto_traducido,
                             config_origen, config_destino, audio_resultado):
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**📋 Resumen:**")
        st.write(f"🎤 **Audio:** {audio_nombre}")
        if config_origen.get('idioma_detectado'):
            st.write(f"🌐 **Idioma detectado:** {config_origen['idioma_detectado']}")
        else:
            st.write(f"🗣️ **Idioma origen:** {config_origen['idioma_stt']}")
        st.write(f"📝 **Texto original:** {texto_original}")
        st.write(f"🌍 **Texto traducido:** {texto_traducido}")
        st.write(f"🔊 **Voz:** {config_destino['voz']}")
    
    with col2:
        st.write("**🔊 Audio Resultante:**")
        st.audio(audio_resultado, format="audio/mp3")
        st.download_button(
            "📥 Descargar Audio",
            audio_resultado,
            f"traduccion_{config_destino['idioma']}.mp3",
            "audio/mp3",
            use_container_width=True
        )

if __name__ == "__main__":
    main()