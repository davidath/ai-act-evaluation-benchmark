from llm_inference.lmcpp_oss import LlammaCppGPTOSSTextGenerator
import utils
import sys


def main():
    config = utils.load_config(sys.argv[1])
    llm_client = LlammaCppGPTOSSTextGenerator(config)
    print(llm_client.generate(config['prompt']))


if __name__ == "__main__":
    main()
