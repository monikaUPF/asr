import os
import glob
import argparse
import tempfile
import subprocess

from sox import file_info


class Transcriber:

    list_file_format = "{id}\t{path}\t{duration}\t{transcript}\n"

    def __init__(self, base_cfg_path):

        with open(base_cfg_path) as base_cfg:
            self.cfg_base = ''
            self.sampling_rate = 16000
            for line in base_cfg.readlines():
                if line.startswith('--test') or line.startswith('--sclite'):
                    pass
                else:
                    if line.startswith('--samplerate'):
                        self.sampling_rate = line.strip().split('=')[1]
                    self.cfg_base += line

    def _call_process(self, lst_path, outdir_path):

        with tempfile.NamedTemporaryFile(mode='w+') as cfg_fd:

            cfg_fd.write(self.cfg_base)
            cfg_fd.write('--test={0}\n'.format(lst_path))
            cfg_fd.write('--sclite={0}\n'.format(outdir_path))
            cfg_fd.flush()

            arg_list = ['/root/flashlight/build/bin/asr/fl_asr_decode', '--flagsfile', cfg_fd.name]
            subprocess.run(args=arg_list)

    def resample_audio(self, source_path, target_path, sampling_rate):
        os.system(f"sox {source_path} -r {sampling_rate} -c 1 -b 16 {target_path}")

    def predict(self, audio_path):
        audio_id = 0
        with tempfile.NamedTemporaryFile(mode='w+') as lst_fd, \
                tempfile.NamedTemporaryFile(mode='w+', suffix='.wav') as audio_fd:
                            
            resampled_audio_path = audio_fd.name
            self.resample_audio(audio_path, resampled_audio_path, sampling_rate=self.sampling_rate)
            duration = file_info.duration(resampled_audio_path)

            audio_id_str = '%09d' % audio_id
            list_dict = {
                'id': audio_id_str,
                'path': resampled_audio_path,
                'duration': str(duration),
                'transcript': '<no_transcript>'
            }
            list_data = self.list_file_format.format(**list_dict)

            lst_fd.write(list_data)
            lst_fd.flush()

            results = self.predict_data(lst_fd.name)

            return results[audio_id_str]

    def predict_batch(self, audio_path_list):

        with tempfile.NamedTemporaryFile(mode='w+') as lst_fd:
            audio_id = 0
            audio_mapping = {}
            for audio_path in audio_path_list:
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.wav', delete=False) as audio_fd:

                    resampled_audio_path = audio_fd.name
                    self.resample_audio(audio_path, resampled_audio_path, sampling_rate=self.sampling_rate)
                    duration = file_info.duration(resampled_audio_path)

                    audio_id_str = '%09d' % audio_id
                    list_dict = {
                        'id': audio_id_str,
                        'path': resampled_audio_path,
                        'duration': str(duration),
                        'transcript': '<no_transcript>'
                    }
                    list_data = self.list_file_format.format(**list_dict)

                    lst_fd.write(list_data)
                    lst_fd.flush()

                    audio_mapping[audio_id_str] = audio_path
                    audio_id += 1

            with open(lst_fd.name) as temp:
                print("lst file contents:")
                print(temp.read())

            results = self.predict_data(lst_fd.name)
            mapped = {v: results[k] for k, v in audio_mapping.items()}
            return mapped


    def predict_data(self, data_path):

        with tempfile.TemporaryDirectory() as outdir_path:

            self._call_process(data_path, outdir_path)

            lst_name = data_path.replace('/', '#')
            output_hyp_filename = '{0}.hyp'.format(lst_name)
            output_hyp_path = os.path.join(outdir_path, output_hyp_filename)

            results = {}
            with open(output_hyp_path) as fd_output:
                for line in fd_output:
                    try:
                        hypothesis, audio_id = line.split('(', 1)
                        audio_id, _ = audio_id.split(')', 1)
                        results[audio_id] = hypothesis
                        
                    except Exception as exc:
                        raise Exception("Error found! Output transcription not generated or malformed.") from exc

            with open(output_hyp_path) as fd_output:
                print(fd_output.read())

            return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcriber options')
    parser.add_argument('--cfg', help='configuration file path', required=True)
    parser.add_argument('--wav', help='wav file path', required=True)
    args = parser.parse_args()

    transcriber = Transcriber(args.cfg)
    if os.path.isdir(args.wav):
        files = glob.glob("/data/**/*.wav", recursive=True)
    else:
        files = [args.wav]

    print(files)
    results = transcriber.predict_batch(files)
    with open("/data/audio/all.txt", "w") as out_txt:
        for path, result in results.items():
            out_txt.write(f"'{path}', {result}\n")
