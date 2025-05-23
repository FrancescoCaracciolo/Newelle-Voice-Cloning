from .utility.pip import find_module, install_module
from .handlers.tts import TTSHandler
from .handlers import ExtraSettings
from .extensions import NewelleExtension
import shutil
import os


class VoiceCloning(NewelleExtension):

    name = "Voice Cloning"
    id = "voicecloning"

    def __init__(self, pip_path : str, extension_path: str, settings):
        super().__init__(pip_path, extension_path, settings)

    def get_tts_handlers(self) -> list[dict]:
        return [
            {
                "key": "so-vits2",
                "title": "So-VITS 2",
                "description": "Self-hostable, So-VITS 2 One shot voice cloning. Easily clone voices with only one audio file",
                "website": "https://huggingface.co/spaces/lj1995/GPT-SoVITS-v2",
                "class": SoVits2
            },
            {
                "key": "fishtts",
                "title": "FishTTS",
                "description": "Self-hostable, FishTTS One shot voice cloning. Easily clone voices with only one audio file",
                "website": "https://huggingface.co/spaces/fishtts/fishtts",
                "class": FishTTS
            },
            {
                "key": "indextts",
                "title": "IndexTTS",
                "description": "Self-hostable, IndexTTS One shot voice cloning. Easily clone voices with only one audio file",
                "website": "https://huggingface.co/spaces/indextts/indextts",
                "class": IndexTTS
            }
        ]

class SoVits2(TTSHandler):
    key = "so-vits2"
    def __init__(self, settings, path):
        super().__init__(settings, path)
        self.ref_audio_path = os.path.join(os.path.abspath(os.path.join(self.path, os.pardir)), "audio_files")
        if not os.path.isdir(self.ref_audio_path):
            os.makedirs(self.ref_audio_path)

    def is_installed(self) -> bool:
        return bool(find_module("gradio_client"))

    def install(self):
        install_module("gradio_client", self.pip_path)

    def get_audio_files(self):
        audio_files = os.listdir(self.ref_audio_path)
        res = tuple()
        for file in audio_files:
            if file.endswith(".wav"):
                relative_path = os.path.join(self.ref_audio_path, file)
                res += ((file, relative_path), )
        return res 

    def get_extra_settings(self) -> list:
        return [
            ExtraSettings.EntrySetting("api", "HuggingFace API Token", "Not mandatory, HF API token", ""),
            {
                "key": "url",
                "title": "Endpoint",
                "description": "URL of the endpoint",
                "type": "entry",
                "default": "lj1995/GPT-SoVITS-v2",
            },
            {
                "key": "audio",
                "title": "Reference Audio",
                "description": "Open the folder and add a wav file to use as reference audio",
                "type": "combo",
                "values": self.get_audio_files(),
                "default": "",
                "folder": self.ref_audio_path,
                "refresh": lambda x : self.settings_update(),
            },
            {
                "key": "ref-language",
                "title": "Reference Language",
                "description": "Language of the reference audio",
                "type": "combo",
                # prompt_language Literal['Chinese', 'English', 'Japanese', 'Yue', 'Korean', 'Chinese-English Mixed', 'Japanese-English Mixed', 'Yue-English Mixed', 'Korean-English Mixed', 'Multilingual Mixed', 'Multilingual Mixed(Yue)'] Default: "Chinese"
                "values": (("Chinese", "Chinese"), ("English", "English"), ("Japanese", "Japanese"), ("Yue", "Yue"), ("Korean", "Korean"), ("Chinese-English Mixed", "Chinese-English Mixed"), ("Yue-English Mixed", "Yue-English Mixed"), ("Korean-English Mixed", "Korean-English Mixed"),  ("Multilingual Mixed", "Multilingual Mixed"), ("Multilingual Mixed(Yue)")),
                "default": "Chinese",
            },
            {
                "key": "ref-prompt",
                "title": "Reference Prompt",
                "description": "Reference prompt",
                "type": "entry",
                "default": "",
            },
            {
                "key": "lang",
                "title": "Language",
                "description": "Language of the generated audio",
                "type": "combo",
                "values": (('Chinese', 'Chinese'), ('English', 'English'), ('Japanese', 'Japanese'), ('Yue', 'Yue'), ('Korean', 'Korean'), ('Chinese-English Mixed', 'Chinese-English Mixed'), ('Japanese-English Mixed', 'Japanese-English Mixed'), ('Yue-English Mixed', 'Yue-English Mixed'), ('Korean-English Mixed', 'Korean-English Mixed'), ('Multilingual Mixed', 'Multilingual Mixed'), ('Multilingual Mixed(Yue)', 'Multilingual Mixed(Yue)')),
                "default": "Chinese",
            },
            {
                "key": "how_to_cut",
                "title": "How to cut",
                "description": "How to cut the text for elaboration",
                "type": "combo",
                "values": (('No slice', 'No slice'), ('Slice once every 4 sentences', 'Slice once every 4 sentences'), ('Slice per 50 characters', 'Slice per 50 characters'), ('Slice by Chinese punct', 'Slice by Chinese punct'), ('Slice by English punct', 'Slice by English punct'), ('Slice by every punct', 'Slice by every punct')),
                "default": "Slice once every 4 sentences",
                
            },
            {
                "key": "top_k",
                "title": "Top K",
                "description": "Top K",
                "type": "range",
                "min": 1,
                "max": 50,
                "round-digits": 0,
                "default": 15,
            },
            {
                "key": "top_p",
                "title": "Top P",
                "description": "Top P",
                "type": "range",
                "min": 0.0,
                "max": 1.0,
                "round-digits": 2,
                "default": 1.0
            },
            {
                "key": "temperature",
                "title": "Temperature",
                "description": "Temperature",
                "type": "range",
                "min": 0.0,
                "max": 1.0,
                "round-digits": 2,
                "default": 1.0
            },
        ]

    def save_audio(self, message, file): 
        from gradio_client import Client, handle_file
        if self.get_setting("api") == "":
            client = Client(self.get_setting("url"))
        else:
            client = Client(self.get_setting("url"), hf_token=self.get_setting("api"))
        result = client.predict(
                ref_wav_path=handle_file(self.get_setting("audio")),
                prompt_text=self.get_setting("ref-prompt"),
                prompt_language=self.get_setting("ref-language"),
                text=message,
                text_language=self.get_setting("lang"),
                how_to_cut=self.get_setting("how_to_cut"),
                top_k=int(self.get_setting("top_k")),
                top_p=self.get_setting("top_p"),
                temperature=self.get_setting("temperature"),
                ref_free=False,
                speed=1,
                if_freeze=False,
                inp_refs=[],
                api_name="/get_tts_wav"
        ) 
        shutil.copy(result, file)
        client.close()



class FishTTS(TTSHandler):
    key = "fishtts"
    def __init__(self, settings, path):
        super().__init__(settings, path)
        self.ref_audio_path = os.path.join(os.path.abspath(os.path.join(self.path, os.pardir)), "audio_files")
        if not os.path.isdir(self.ref_audio_path):
            os.makedirs(self.ref_audio_path)

    def is_installed(self) -> bool:
        return bool(find_module("gradio_client"))

    def install(self):
        install_module("gradio_client", self.pip_path)

    def get_audio_files(self):
        audio_files = os.listdir(self.ref_audio_path)
        res = tuple()
        for file in audio_files:
            if file.endswith(".wav"):
                relative_path = os.path.join(self.ref_audio_path, file)
                res += ((file, relative_path), )
        return res 

    def get_extra_settings(self) -> list:
        return [
            ExtraSettings.EntrySetting("api", "HuggingFace API Token", "Not mandatory, HF API token", ""),
            {
                "key": "url",
                "title": "Endpoint",
                "description": "URL of the endpoint",
                "type": "entry",
                "default": "fishaudio/fish-speech-1",
            },
            {
                "key": "audio",
                "title": "Reference Audio",
                "description": "Open the folder and add a wav file to use as reference audio",
                "type": "combo",
                "values": self.get_audio_files(),
                "default": "",
                "folder": self.ref_audio_path,
                "refresh": lambda x : self.settings_update(),
            },
            {
                "key": "ref-prompt",
                "title": "Reference Prompt",
                "description": "Reference prompt",
                "type": "entry",
                "default": "",
            }, 
            {
                "key": "top_p",
                "title": "Top P",
                "description": "Top P",
                "type": "range",
                "min": 0.0,
                "max": 1.0,
                "round-digits": 2,
                "default": 0.7
            },
            {
                "key": "temperature",
                "title": "Temperature",
                "description": "Temperature",
                "type": "range",
                "min": 0.0,
                "max": 1.0,
                "round-digits": 2,
                "default": 0.8
            },
        ]

    def save_audio(self, message, file): 
        from gradio_client import Client, handle_file
        if self.get_setting("api") == "":
            client = Client(self.get_setting("url"))
        else:
            client = Client(self.get_setting("url"), hf_token=self.get_setting("api"))
        result = client.predict(
              text=message,
              normalize=True,
              reference_audio=handle_file(self.get_setting("audio")),
              reference_text=self.get_setting("ref-prompt"),
              max_new_tokens=1024,
              chunk_length=200,
              top_p=self.get_setting("top_p"),
              repetition_penalty=1.2,
              temperature=self.get_setting("temperature"),
              seed=0,
              use_memory_cache="never",
              api_name="/inference_wrapper"
        ) 
        result = result[0]
        shutil.copy(result, file)
        client.close()


class IndexTTS(TTSHandler):
    key = "indextts"
    def __init__(self, settings, path):
        super().__init__(settings, path)
        self.ref_audio_path = os.path.join(os.path.abspath(os.path.join(self.path, os.pardir)), "audio_files")
        if not os.path.isdir(self.ref_audio_path):
            os.makedirs(self.ref_audio_path)

    def is_installed(self) -> bool:
        return bool(find_module("gradio_client"))

    def install(self):
        install_module("gradio_client", self.pip_path)

    def get_audio_files(self):
        audio_files = os.listdir(self.ref_audio_path)
        res = tuple()
        for file in audio_files:
            # Assuming audio files can be wav, mp3, etc. Adjust if needed.
            if file.lower().endswith((".wav", ".mp3", ".ogg", ".flac")):
                relative_path = os.path.join(self.ref_audio_path, file)
                res += ((file, relative_path), )
        return res

    def get_extra_settings(self) -> list:
        return [
            ExtraSettings.EntrySetting("api", "HuggingFace API Token", "Not mandatory, HF API token", ""), 
            {
                "key": "url",
                "title": "Endpoint",
                "description": "URL of the Gradio endpoint",
                "type": "entry",
                "default": "IndexTeam/IndexTTS",
            },
            {
                "key": "audio",
                "title": "Reference Audio Prompt",
                "description": "Open the folder and add a wav file to use as reference audio",
                "type": "combo",
                "values": self.get_audio_files(),
                "default": "",
                "folder": self.ref_audio_path,
                "refresh": lambda x : self.settings_update(),
            },
        ]

    def save_audio(self, message, file):
        from gradio_client import Client, handle_file
        if self.get_setting("api") == "":
            client = Client(self.get_setting("url"))
        else:
            client = Client(self.get_setting("url"), hf_token=self.get_setting("api"))
        reference_audio_path = self.get_setting("audio")

        if not reference_audio_path or not os.path.exists(reference_audio_path):
             # Handle error: Reference audio not selected or not found
             print(f"Error: Reference audio file not found or not selected: {reference_audio_path}")
             # Maybe raise an exception or return an error indicator
             return False # Indicate failure

        try:
            result = client.predict(
                    prompt=handle_file(reference_audio_path),
                    text=message,
                    api_name="/gen_single"
            )
            # Assuming 'result' is the path to the generated audio file
            result = result["value"]
            if result and os.path.exists(result):
                 shutil.copy(result, file)
                 # Clean up temporary file created by gradio_client if necessary
                 # os.remove(result) # Be careful with this if result is not always a temp file
                 return True # Indicate success
            else:
                 print(f"Error: Prediction failed or returned invalid path: {result}")
                 return False # Indicate failure

        except Exception as e:
            print(f"Error during TTS prediction: {e}")
            return False # Indicate failure
        finally:
            # Ensure client connection is closed, though gradio_client might handle this implicitly
            # Check gradio_client documentation if explicit closing is needed or possible
            pass
