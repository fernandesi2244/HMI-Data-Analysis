import sunpy.map
import astropy.units as u
import matplotlib.pyplot as plt
from sunpy.net import Fido, attrs as a
from Magnetogram import Magnetogram
import os
import pickle

# Specifications for HMI data download
start_time = '2012-03-06T14:20:00'
end_time = '2012-03-07T14:20:00'
series_name = 'hmi.sharp_cea_720s'
segs = ('magnetogram', 'Br', 'Bp', 'Bt', 'bitmap')
email_for_notification = 'fernandesi2244@gmail.com'
interval = 6*u.hour
download_path = 'HMI Downloaded Files'

corrupted_files = []
magnetograms = []

def download_files(start_time, end_time, series_name, segs, email_for_notification, interval, download_path):
    segVal=a.jsoc.Segment(segs[0])
    for i in range(1, len(segs)):
        segVal&=a.jsoc.Segment(segs[i])

    result = Fido.search(
        a.Time(start_time, end_time),
        a.jsoc.Series(series_name),
        a.jsoc.Notify(email_for_notification),
        a.Sample(interval),
        segVal)

    downloaded_files=Fido.fetch(result, path=os.path.join(download_path, '{file}'))

    print('Files downloaded.')

def register_magnetogram(file_name):
    magnetogram = sunpy.map.Map(file_name)
    harp_num = magnetogram.meta['HARPNUM']
    tot_flux = magnetogram.meta['USFLUX']
    tot_vertical_current = magnetogram.meta['TOTUSJZ']
    twist_param = magnetogram.meta['MEANALP']

    SHARPS_params = {}
    SHARPS_params['Total Unsigned Magnetic Flux'] = tot_flux
    SHARPS_params['Total Unsigned Vertical Current'] = tot_vertical_current
    SHARPS_params['Total Twist Parameter'] = twist_param

    magnetograms.append(Magnetogram(file_name, harp_num, SHARPS_params))

def get_num_files_downloaded():
    return len(os.listdir('HMI Downloaded Files'))

if __name__ == "__main__":
    
    download = input('Do you want to download the HMI Files given by the query specified in the code? Y/N ').lower() == 'y'
    
    if(download):
        download_files(start_time, end_time, series_name, segs, email_for_notification, interval, download_path)
    
    # Parse through magnetogram files
    print('\nParsing files for magnetograms...')
    for fits_file in os.listdir('HMI Downloaded Files'):
        if 'magnetogram.fits' in fits_file:
            try:
                register_magnetogram(os.path.join('HMI Downloaded Files', fits_file))
            except:
                print('There is a problem with the following file:', fits_file)
                corrupted_files.append(fits_file)
    
    print('\nPrinting all magnetograms registered from files...')
    for magnetogram in magnetograms:
        print(magnetogram)

    print('\nNumber of corrupted files:', len(corrupted_files))
    print('Total Number of files:', get_num_files_downloaded())

    with open(os.path.join('Program Saved Files', 'magnetograms.list'), 'wb') as magnetograms_file:
        pickle.dump(magnetograms, magnetograms_file)