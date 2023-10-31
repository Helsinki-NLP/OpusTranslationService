import yaml
import sys
import string

def extract_tokens_from_sentences(sentences_file,token_counts):
    with open(sentences_file, 'r') as file:
        for line in file:
            for token in line.split():
                if token in token_counts:
                    token_counts[token] += 1
                else:
                    token_counts[token] = 1

    return token_counts

def check_tokens_in_yaml(yaml_file, tokens):
    with open(yaml_file, 'r') as file:
        yaml_content = yaml.safe_load(file)
        if not isinstance(yaml_content, dict):
            raise ValueError("Expected a dictionary structure in the YAML file.")

        missing_tokens = {token[0]: token[1] for token in tokens.items() if token[0] not in yaml_content.keys()}
        return missing_tokens

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <yaml_file> <src_sentences_file> <trg_sentences_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    src_sentences_file = sys.argv[2]
    trg_sentences_file = sys.argv[3]

    token_counts = dict()
    src_tokens = extract_tokens_from_sentences(src_sentences_file, token_counts)
    trg_tokens = extract_tokens_from_sentences(trg_sentences_file, token_counts)
    
    missing_tokens = check_tokens_in_yaml(yaml_file, token_counts)

    if missing_tokens:
        print("Tokens not found in the YAML file:", "\n".join([str((x[0],x[1],[hex(ord(y)) for y in x[0]])) for x in missing_tokens.items()]))
    else:
        print("All tokens were found in the YAML file!")

    missing_token_set = {token[0] for token in missing_tokens.items()}
    with \
        open(src_sentences_file, 'r') as src_file,\
        open(trg_sentences_file, 'r') as trg_file,\
        open(src_sentences_file+".nounk", 'w') as src_file_out,\
        open(trg_sentences_file+".nounk", 'w') as trg_file_out:
        for src_line in src_file:
            trg_line = trg_file.readline()
            src_sentence_token_set = set(src_line.split())
            trg_sentence_token_set = set(trg_line.split())
            valid_sentence_pair = True 
            if missing_token_set.intersection(src_sentence_token_set):
                print("src contains unk: " + src_line)
                valid_sentence_pair = False
            if missing_token_set.intersection(trg_sentence_token_set):
                print("trg contains unk: " + trg_line)
                valid_sentence_pair = False
            if valid_sentence_pair:
                src_file_out.write(src_line)
                trg_file_out.write(trg_line)
    

