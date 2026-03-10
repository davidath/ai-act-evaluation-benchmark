from llm_inference.lmcpp_oss import LlammaCppGPTOSSTextGenerator
import utils
import sys
import json
import pickle


def replace_context(config, json_string, pkl_string):
    try:
        # Load JSON string
        json_object = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string provided: {e}")

    try:
        # Load pickle file
        with open(pkl_string, 'rb') as file:
            pickle_object = pickle.load(file)
    except (FileNotFoundError, IOError) as e:
        raise FileNotFoundError(f"Error loading pickle file: {e}")
    except pickle.UnpicklingError as e:
        raise ValueError(f"Error unpickling the file: {e}")

    rnge = json_object['related_articles']
    rnge = [int(i) - 1 for i in rnge]
    article_str = [pickle_object[i] for i in rnge]
    config['prompt'] = config['prompt'].replace(
        '$!CONTEXT_PLACEHOLDER!$', ' '.join(article_str))


def replace_scenario(config, json_string):
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string provided: {e}")

    formatted_json_string = json.dumps(json_object,
                                       ensure_ascii=False, indent=4)

    if '$!SCENARIO_PLACEHOLDER!$' in config['prompt']:
        config['prompt'] = config['prompt'].replace('$!SCENARIO_PLACEHOLDER!$',
                                                    formatted_json_string)
    else:
        raise ValueError("'$!SCENARIO_PLACEHOLDER!$' is not found in prompt.")


def main():
    config = utils.load_config(sys.argv[1])
    llm_client = LlammaCppGPTOSSTextGenerator(config)
    print(sys.argv[2])
    replace_scenario(config, sys.argv[2])
    replace_context(config, sys.argv[2], sys.argv[3])
    print(llm_client.generate(config['prompt']))


if __name__ == "__main__":
    main()
