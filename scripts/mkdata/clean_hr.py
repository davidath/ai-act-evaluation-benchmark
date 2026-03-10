import sys
import json


def delete_after_semicolon(text):
    semicolon_index = text.find(';')
    if semicolon_index != -1:
        return text[:semicolon_index].strip()
    return text.strip()


try:
    with open(sys.argv[1], 'r', encoding='utf-8') as file:
        data = json.load(file)
    assert_str = "Loaded data must be a dictionary or list"
    assert isinstance(data, (dict, list)), assert_str
except FileNotFoundError:
    print(f"Error: The file '{sys.argv[1]}' does not exist.")
except json.JSONDecodeError:
    print(f"Error: The file '{sys.argv[1]}' does not contain valid JSON.")
except IOError:
    print(f"Error: Could not read the file '{sys.argv[1]}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

gather = []
for record in data:
    record['intended_use'] = delete_after_semicolon(record['intended_use'])
    gather.append(record)

try:
    with open(sys.argv[2], 'w', encoding='utf-8') as file:
        json.dump(gather, file, ensure_ascii=False, indent=4)
except IOError as e:
    print(f"Error writing to file: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
