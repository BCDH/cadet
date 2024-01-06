import os
import sys


def fix_conllu_file(conllu_file_path):
    with open(conllu_file_path) as f:
        lines = f.readlines()
    fixed_lines = []
    index = 0
    for line in lines:
        if len(fixed_lines) == 0 and line == "\n":
            continue
        if line == "\n":
            fixed_lines.append("\n")
            index = 0
            continue
        tokens = line.split("\t")
        tokens[0] = str(index + 1)
        fixed_tokens = [tokens[0]]
        for token in tokens[1:]:
            if token != "":
                fixed_tokens.append(token)
            else:
                fixed_tokens.append("_")
        index += 1
        fixed_lines.append("\t".join(fixed_tokens))
    with open(conllu_file_path, "wt") as f:
        f.writelines(fixed_lines)


def fix_conllu_folder(conllu_folder_path):
    files = os.listdir(conllu_folder_path)
    for file in files:
        if file.endswith(".conllu"):
            fix_conllu_file(conllu_folder_path + "/" + file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SYNTAX: fix_conllu_files <full_conllu_export_folder_path>")
        sys.exit(1)
    fix_conllu_folder(sys.argv[1])
