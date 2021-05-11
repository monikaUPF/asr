## ASR

This repository contains the Wav2Letter++ ASR Docker architecture, originally deployed by Guillermo Cambara and Roberto Carlini (members of TALN-UPF).

In order to use the provided images, you'll have to download and extract the model/s that you want to use. You'll find models for English [here]().

Once you have downloaded and extracted the model/s, modify the docker-compose.dev.yml to mount the location of the model as an internal image directory. The docker-compose file is already prepared, showing the placeholder ```[REPLACE BY PATH TO RESOURCES DIR]``` indicating where you have to set your local resource directory containing the extracted data.

Finally, assuming you have docker-compose already installed, execute:  
```docker-compose -f docker-compose.dev.yml up integration speech2text```

This command will start speech2text service (at localhost:4200) and the demo interface (at localhost:4100).

If you want just to process a batch of wav files, run this command instead:  
```docker run -v [BATCH_PATH]:/data/audio -v [PATH TO CHOSEN ASR]:/ASR speech2text:flashlight python3 transcriber.py --cfg /ASR/conf/decode.cfg --wav /data```
