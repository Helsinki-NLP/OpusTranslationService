import os
import yaml
import subprocess
import pycountry
import argparse
import json
import glob
import shutil
from fix_vocab import fix_vocab


def write_metadata(output_dir, lang1_short, lang2_short):
    lang1_name = pycountry.languages.get(alpha_2=lang1_short).name
    lang2_name = pycountry.languages.get(alpha_2=lang2_short).name
   
    metadata = {
        "package_version": "1.5",
        "argos_version": "1.5",
        "from_code": lang1_short,
        "from_name": lang1_name,
        "to_code": lang2_short,
        "to_name": lang2_name
    }
   
    with open(os.path.join(output_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=4)

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def check_ct2(yaml_content):
    return yaml_content.get('model-tags') and 'ct2' in yaml_content['model-tags']


def convert_three_letter_to_two_letter(three_letter_code):
    """Convert a three-letter language code to its corresponding two-letter code using pycountry."""
    try:
        lang = pycountry.languages.get(alpha_3=three_letter_code)
        return lang.alpha_2
    except AttributeError:
        # Return None or raise an exception if the three-letter code is not found
        return None


def process_models(input_models_dir, output_models_dir):
    for sub_dir in os.listdir(input_models_dir):
        # Ensure it's a directory and contains a hyphen
        if '-' in sub_dir:
            lang1, lang2 = sub_dir.split('-')

            for deeper_sub_dir in os.listdir(os.path.join(input_models_dir, sub_dir)):
                yaml_file = os.path.join(input_models_dir, sub_dir, deeper_sub_dir, 'modelconfig.yml')

                if os.path.exists(yaml_file):
                    yaml_content = load_yaml(yaml_file)

                    if check_ct2(yaml_content):
                        # Convert 3-letter language codes to 2-letter language codes
                        lang1_short = convert_three_letter_to_two_letter(lang1)
                        lang2_short = convert_three_letter_to_two_letter(lang2)
                       
                        # Create language pair output directory
                        lang_pair_output_dir = os.path.join(output_models_dir, f"{lang1_short}_{lang2_short}")
                        os.makedirs(lang_pair_output_dir, exist_ok=True)

                        # Write metadata.json for the language pair
                        write_metadata(lang_pair_output_dir, lang1_short, lang2_short)
                        
                        # Copy the spm model to the output dir
                        shutil.copy(
                            os.path.join(input_models_dir, sub_dir, deeper_sub_dir,"source.spm"),
                            os.path.join(lang_pair_output_dir,"sentencepiece.model")
                        )
                        
                        # Adjust the output directory to include a "model" subdirectory
                        model_output_sub_dir = os.path.join(lang_pair_output_dir, "model")

                        # Some opus models have buggy vocabs, fix them
                        vocab_file = glob.glob(os.path.join(input_models_dir, sub_dir, deeper_sub_dir,"*.vocab.yml"))[0]
                        fix_vocab(vocab_file)

                        # Execute the ct2-opus-mt-converter command
                        try:
                            subprocess.run([
                                'ct2-opus-mt-converter',
                                '--model_dir', os.path.join(input_models_dir, sub_dir, deeper_sub_dir),
                                '--output_dir', model_output_sub_dir
                            ])
                        except FileNotFoundError:
                            print("ct2-opus-mt-converter not found, install it by running pip install ctranslate2.")


def main():
    parser = argparse.ArgumentParser(description='Process models based on given directories.')
    parser.add_argument('input_models_dir', type=str, help='The directory of input models.')
    parser.add_argument('output_models_dir', type=str, help='The directory for output models.')

    args = parser.parse_args()

    process_models(args.input_models_dir, args.output_models_dir)

if __name__ == "__main__":
    main()