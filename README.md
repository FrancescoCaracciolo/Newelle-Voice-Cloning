# Newelle Voice Cloning

<p align="left">
  <a href="https://github.com/topics/newelle-extension">
    <img width="200" alt="Download on Flathub" src="https://raw.githubusercontent.com/qwersyk/Assets/main/newelle-extension.svg"/>
  </a>
  <br/>
</p>

<br/><br/>

This plugins adds a TTS Handler to do one shot voice cloning using GPT-SoVITS-v2 with a single audio file of ~10s.

To adjust the settings and set the audio file, go into Newelle's settings, under the Voice settings, expand TTS and select "So-VITS 2". There you can set multiple settings.

## Selfhosting
By default, this plugin runs on [this Huggingface space](https://huggingface.co/spaces/lj1995/GPT-SoVITS-v2).
You can selfhost it by running it with docker locally:
```bash
docker run -it -p 7860:7860 --platform=linux/amd64 --gpus all \
	registry.hf.space/lj1995-gpt-sovits-v2:latest python inference_webui.py
```
## Installation
- Download and Install [Newelle](https://flathub.org/apps/io.github.qwersyk.Newelle)
- Download the [python file](https://github.com/FrancescoCaracciolo/Newelle-Voice-Cloning/blob/main/cloning.py) in the repository
- Load the extension
![screenshot](https://raw.githubusercontent.com/qwersyk/Mathematical-graph/main/Screenshot.png)
