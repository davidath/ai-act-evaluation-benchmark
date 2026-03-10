from llm_inference.lmcpp_oss import LlammaCppGPTOSSTextGenerator
import utils
import sys
import json


def replace_prompt(config, json_string):
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string provided: {e}")

    formatted_json_string = json.dumps(json_object,
                                       ensure_ascii=False, indent=4)

    if '$!PLACEHOLDER!$' in config['prompt']:
        config['prompt'] = config['prompt'].replace('$!PLACEHOLDER!$',
                                                    formatted_json_string)
    else:
        raise ValueError("'$!PLACEHOLDER!$' is not found in prompt.")


def main():
    config = utils.load_config(sys.argv[1])
    llm_client = LlammaCppGPTOSSTextGenerator(config)
    print(sys.argv[2])
    replace_prompt(config, sys.argv[2])
    print(llm_client.generate(config['prompt']))


if __name__ == "__main__":
    main()
