import os
import pandas as pd
import paths

def txt_to_csv(txt_file_path):
    try:
        # Read the text file and split it into columns
        data = []
        with open(txt_file_path, "r") as f:
            for line in f:
                parts = line.strip().split(maxsplit=1)  # Split at the first space
                if len(parts) == 2:
                    file_name, file_context = parts
                    data.append([file_name, file_context])

        # Get the current working directory
        current_dir = os.getcwd()
        
        csv_file_path = os.path.join(current_dir, "output_data.csv")
        
        df = pd.DataFrame(data, columns=["file_name", "file_context"])
        df.to_csv(csv_file_path, index=False)

        print(f"CSV file created successfully at: {csv_file_path}")
    
    except FileNotFoundError as e:
        print(f"Error: The file {txt_file_path} was not found.")
        print(e)
    except PermissionError as e:
        print(f"Error: Permission denied while trying to write to {csv_file_path}.")
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    txt_file_path = paths.TXT_PATH
    txt_to_csv(txt_file_path)
