import json
import os
import sys


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        assert isinstance(data, (dict, list)
                          ), "Loaded data must be a dictionary or list"
        return data
    except FileNotFoundError:
        print(f"Error: The file '{path}' does not exist.")
    except json.JSONDecodeError:
        print(f"Error: The file '{path}' does not contain valid JSON.")
    except IOError:
        print(f"Error: Could not read the file '{path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def reparse_json_string(input_str):
    start = input_str.find('{')
    end = input_str.rfind('}') + 1
    return input_str[start:end]


def load_json_from_txt(file_path):
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            try:
                json_obj = json.loads(first_line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Error decoding JSON from the first line: {e}")

            second_line = file.readline().strip()
            second_line = reparse_json_string(second_line)
            try:
                obligations = json.loads(second_line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Error decoding JSON from the first line: {e}")

        return json_obj, obligations['obligations']

    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} was not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


def extract_name_before_json(file_path):
    root, ext = os.path.splitext(file_path)

    if ext.lower() == '.json':
        return root
    else:
        raise ValueError(
            f"The file {file_path} does not have a .json extension.")


def main():
    main_json_obj = load_json(sys.argv[1])
    name_before_json = extract_name_before_json(sys.argv[1])

    for txt_file_name in os.listdir(sys.argv[2]):
        if txt_file_name.endswith('.txt'):
            obj_id = int(txt_file_name.split('_')[1])
            txt_file_path = os.path.join(sys.argv[2], txt_file_name)
            txt_json_obj, obligations = load_json_from_txt(txt_file_path)
            if txt_json_obj == main_json_obj[obj_id]:
                main_json_obj[obj_id]['obligations'] = obligations

    with open(name_before_json+'_updated_obligations.json', 'w') as file:
        json.dump(main_json_obj, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
