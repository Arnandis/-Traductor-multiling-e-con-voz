import streamlit as st

class AudioInput:
    @staticmethod
    def obtener_audio():
        """Obtiene audio mediante subida o grabación directa"""
        metodo = st.radio(
            "Selecciona método:",
            ["📤 Subir archivo", "🎙️ Grabar audio"],
            horizontal=True
        )

        audio_bytes = None
        audio_nombre = "audio_procesado.wav"

        if metodo == "📤 Subir archivo":
            audio_bytes, audio_nombre = AudioInput._subir_archivo()
        else:
            audio_bytes, audio_nombre = AudioInput._grabar_audio()

        return audio_bytes, audio_nombre

    @staticmethod
    def _subir_archivo():
        """Maneja la subida de archivos de audio"""
        with st.expander("ℹ️ Formatos soportados"):
            st.write("""
            **WAV** (recomendado), **WEBM**, **MP3**
            - Frecuencia: 16kHz
            - Canales: Mono
            - Duración: < 60 segundos
            """)

        archivo = st.file_uploader(
            "Selecciona archivo de audio", 
            type=['wav', 'webm', 'mp3'],
            help="Formatos: WAV, WEBM, MP3"
        )

        if archivo is not None:
            audio_bytes = archivo.read()
            st.audio(audio_bytes, format=f"audio/{archivo.name.split('.')[-1]}")
            st.write(f"**Archivo:** {archivo.name} ({len(audio_bytes) / 1024:.1f} KB)")
            return audio_bytes, archivo.name

        return None, "audio_procesado.wav"

    @staticmethod
    def _grabar_audio():
        """Maneja la grabación directa de audio"""
        st.write("**Presiona para grabar (máximo 60 segundos):**")

        try:
            grabacion = st.audio_input("Grabar audio")
            if grabacion is not None:
                audio_bytes = grabacion.read()
                st.audio(audio_bytes, format="audio/wav")
                st.success("✅ Audio grabado correctamente")
                st.write(f"**Tamaño:** {len(audio_bytes) / 1024:.1f} KB")
                return audio_bytes, "audio_grabado.wav"
        except Exception as e:
            st.warning("⚠️ Grabación no disponible")
            st.info("Usa la opción 'Subir archivo'")

        return None, "audio_grabado.wav"