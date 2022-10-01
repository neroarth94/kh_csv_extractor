#
# CSV aggregator script
# Consolidates the CSV files generated by Penlite+ software in to a single CSV file
#
# -> python csv_extractor.py -f <csv file folder> -o <output folder>
#

import shutil
import sys
from optparse import OptionParser
from pathlib import Path
import csv
import os
import glob

csv_file_dict = {}
output_dir = "output"
output_csv_name = "output"
test_configs = [ 
                # Test Name
                'INTERCON',
                'PULL_DOWN',
                'LEAKAGE',
                'TSR',
                'UID_CRC_CHECK',
                'ID_BITS_DECODE',
                'PEN_CRC_VERIFY',
                'MROM_CHECK',
                'ID_BITS_READ',
                'RSCAN',
                'RSCANSTATISTICS',
                'RSCANSTATISTICS_LIMIT'
               ]



def process_files(csv_folder):
    print(f"output folder: {output_dir}")

    # Get list of CSV files to process
    csv_folder_path = Path(csv_folder)
    if not csv_folder_path.is_dir():
        print(f"EXITING !!! {csv_folder} doesn't exists")
        return

    os.chdir(csv_folder)
    files = glob.glob("*.csv")

    # Check if the output file exists
    '''
    file_path = Path(output_csv_file)
    if file_path.is_file():
        print("Exiting !!! Output file alreday exists")
        return
    '''

    # Iterate through all the CSV files and search for test results
    for file in files:
        print(f"[INFO] Processing file : {file}")
        penid = get_penid(file)

        for test_name in test_configs:
            test_data, row_name = parse_test_results(file, test_name, penid)

            if not row_name:
                continue

            file_name = csv_file_dict[row_name]
            write_file = open(os.path.join(output_dir, file_name), 'a+', newline='')
            csv_writter = csv.writer(write_file, delimiter=',')

            for row in test_data:
                csv_writter.writerow([penid, test_name] + row)
                


def get_penid(file):
    ''' Returns the Pen ID from the given CSV file. Returns None if not found '''
    # Open the CSV file
    with open (file, newline='') as csvfile:
        # Get Pen ID
        for line in csvfile:
            if line.startswith("Pen ID:"):
                tmp = line.split()
                print(f"[INFO] Pen Id = {tmp[2]}")
                return tmp[2]
    
    return None

def parse_test_results(file, test_name, penid):
    ''' Returns test data '''
    rows = []
    test_result = "NA"
    row_name = ""
    has_reached_header_row = False
    has_found_testname = False

    with open(file, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        for row in csv_reader:
            if len(row) > 0 and row[0].startswith(test_name+":"):
                has_found_testname = True
                test_result = row[0].split(':')[1]
                print(f"[INFO] Found test data for {test_name} result {test_result}")
                # Skip the rows that are not relevant

            if (not has_reached_header_row and has_found_testname and "Name" in row):
                joined_row = ",".join(row)
                if joined_row not in csv_file_dict:
                    file_name = f"{output_csv_name}_{len(csv_file_dict) + 1}.csv"
                    csv_file_dict[joined_row] = file_name

                    write_file = open(os.path.join(output_dir, file_name), 'a+', newline='')
                    csv_writter = csv.writer(write_file, delimiter=',')
                    csv_writter.writerow(["Pen ID", "Test"] + row)
                row_name = joined_row
                has_reached_header_row = True
                continue
                
            if not has_reached_header_row:
                continue

            if len(row) == 0:
                return rows, row_name
            rows.append(row)
    return rows, row_name


if __name__ == "__main__":
    # Command line options parser
    usage_str = "usage: %prog [options]"
    parser = OptionParser(usage=usage_str)
    parser.add_option("-f", "--folder", dest="csv_folder", metavar="FILE", help="Specifies input CSV folder")
    parser.add_option("-o", "--output", dest="output_folder", metavar="FILE", help="Output CSV file")
    (options, args) = parser.parse_args(sys.argv)

    print(f"Starting CSV aggregator. CSV folder = {options.csv_folder}, Output file = {options.output_folder}")
    output_dir = os.path.join(os.getcwd(), options.output_folder)
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    print(f"output directory: {output_dir}")
    process_files(options.csv_folder)
    


