from llm_inference.lmcpp_oss import LlammaCppGPTOSSTextGenerator
import utils
import sys

SUPPORTED_LEVELS = ['prohibited', 'high-risk', 'limited', 'minimal']


def get_levels():
    if len(sys.argv) < 3 or sys.argv[2].lower() == "all":
        selected_levels = SUPPORTED_LEVELS
    else:
        selected_levels = sys.argv[2:]
        # lowercase
        selected_levels = [s.lower() for s in selected_levels]
        # sanity check
        selected_levels = list(set(selected_levels) & set(SUPPORTED_LEVELS))
    return selected_levels


def main():
    config = utils.load_config(sys.argv[1])
    llm_client = LlammaCppGPTOSSTextGenerator(config)
    selected_levels = get_levels()
    for level in selected_levels:
        print('---------------------- '+level+' ---------------------------')
        print('------------------------------------------------------------')
        print(llm_client.generate(config[level]))
        print('------------------------------------------------------------')


if __name__ == "__main__":
    main()
