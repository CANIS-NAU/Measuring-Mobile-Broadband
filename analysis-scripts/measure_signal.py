import csv
import subprocess
import datetime


def main():
    now = datetime.datetime.now().replace(microsecond=0).isoformat() 

    with open(f'./data/LTE_logs/LTE_Log_{now}','w', newline='\n') as csvfile:
        lte_writer = csv.writer(csvfile)

        columns = ['DPX', 'CID', 'A', 'fc', 'freq-offset', 'RXPWR', 'C', 'nRB', 'P', 'PR', 'CrystalCorrectionFactor', 'time']

        lte_writer.writerow(columns)

        while True:
            samples = get_sample('1.9925e9')
            for row in samples:
                lte_writer.writerow(row)
        
            now = datetime.datetime.now().replace(microsecond=0).isoformat() 
            print(now)


def get_sample(freq):
    hackrf_open = False

    while hackrf_open != True:
        try:
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

      

    now = datetime.datetime.now().replace(microsecond=0).isoformat() 

    # there are not correct spaces when the antenna ID is 3 digits or longer, so we fix that here
    for row in output_rows:
        if len(row[1]) > 3:
            length = len(row[1])
            cid = row[1][:length]
            antenna = row[1][:-3]
            row[1] = cid
            row.insert(1, antenna)
        row.append(now)
    
    return output_rows

if __name__ == '__main__':
    main()