import csv
import subprocess
import datetime


def main():
    init_time = datetime.datetime.now().replace(microsecond=0).isoformat() 

    file_name = f'./data/LTE_logs/LTE_Log_{init_time}'

    # we do these writes with multiple file operations so that they are resilient to power outages
    # as if we do everything in one file operation the data can be more easily lost
    initial_write(file_name)
    
    while True:
        samples = get_sample('1.9925e9')
        write_samples(file_name, samples)
        now = datetime.datetime.now().replace(microsecond=0).isoformat() 
        print(now)

def initial_write(file_name):
    csvfile = open(file_name,'w', newline='\n')
    lte_writer = csv.writer(csvfile)
    columns = ['DPX', 'CID', 'A', 'fc', 'freq-offset', 'RXPWR', 'C', 'nRB', 'P', 'PR', 'CrystalCorrectionFactor', 'time']
    lte_writer.writerow(columns)
    csvfile.close()


def write_samples(file_name, samples):
    csvfile = open(file_name,'a', newline='\n')
    lte_writer = csv.writer(csvfile)
    for row in samples:
        lte_writer.writerow(row)


def get_sample(freq):
    hackrf_open = False

    while hackrf_open != True:
        try:
            now = datetime.datetime.now().replace(microsecond=0).isoformat() 
            lte_output = subprocess.run(
                ['CellSearch', '--freq-start', freq, '-n', '5'], check=True, capture_output=True, text=True)
            hackrf_open = lte_output.returncode == 0
            # we also need to get GPS location here, but unsure exactly how that call will look
            # will probably use gpsd solution
        except subprocess.CalledProcessError:
            # HackRF usually takes a couple attempts to successfully open
            print('Could not open HackRF, trying again')


    for index, line in enumerate(lte_output.stdout.splitlines()):
        if "DPX CID" in line:
            output_index = index
   
    # this checks to make sure that we did find output lines, if we didn't thne output_index if falsey
    if output_index:
        output_rows = lte_output.stdout.splitlines()[output_index+1:]
        output_rows = list(map(lambda str: list(
            filter(None, str.split(' '))), output_rows))

    # there are not correct spaces when the antenna ID is 3 digits or longer, so we fix that here
    for row in output_rows:
        if len(row[1]) > 3:
            length = len(row[1])
            antenna = row[1][length-3:]
            cid = row[1][:-3]
            row[1] = cid
            print(f'cid: {cid}, ant:{antenna}')
            row.insert(2, antenna)

        row.append(now)
    
    return output_rows

if __name__ == '__main__':
    main()