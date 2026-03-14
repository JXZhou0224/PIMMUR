import json
import argparse
import os

# arg input file name
def parse_args():
    parser = argparse.ArgumentParser(description="Process file and save results.")
    parser.add_argument("input_file", type=str, help="Path to the input file")
    return parser.parse_args()

def main():
    args = parse_args()
    input_file = args.input_file

    with open("data/paper_order","r") as f:
        paper_order = f.readlines()
    paper_order = [line.strip() for line in paper_order]
    output_list = []
    ref_dict = {}
    with open(input_file, "r") as file:
        lines = file.readlines()
        for line in lines:
            key, entry = line.split(" ")
            key = key.strip()
            entry = entry.strip()
            ref_dict[key] = entry
    cnt = 0
    for paper in paper_order:
        if(ref_dict[paper] == "yes"):
            output_list.append(f"\\cmark")
            print("yes")
            cnt+=1
        elif (ref_dict[paper] == "no"):
            output_list.append(f"\\xmark")
            print("no")
        else:
            raise ValueError(f"Unexpected value for {paper}: {ref_dict[paper]}")
    output_str = " & ".join(output_list)
    print(output_str)
    print(f"Total unaware: {cnt}")


if __name__ == "__main__":
    main()