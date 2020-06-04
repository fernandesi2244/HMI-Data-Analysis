from Magnetogram import Magnetogram
import pickle
import os
import astropy.units as u

def analyze(magnetogram):
    magnetogram.generate_info()
    print()
    clip = (1,95)*u.percent
    magnetogram.plot(clip)
    print("--------------------"*3)

def sorting_key(value):
    return value.harp_num

def binary_search(magnetograms, harp_num):
    left, right = 0, len(magnetograms)-1
    while(left<=right):
        mid = (left+right)//2
        if(magnetograms[mid].harp_num == harp_num):
            return magnetograms[mid]
        if(magnetograms[mid].harp_num < harp_num):
            left = mid+1
        if(magnetograms[mid].harp_num > harp_num):
            right = mid-1

if __name__ == '__main__':
    with open(os.path.join('Program Saved Files', 'magnetograms.list'), 'rb') as magnetograms_file:
        magnetograms = pickle.load(magnetograms_file)
    
    magnetograms.sort(key = sorting_key)
    
    harp_num = input("Enter the HARP number of the magnetogram of interest OR enter 'all' to analyze all magnetograms: ").lower()
    if harp_num == 'all':
        for magnetogram in magnetograms:
            print()
            analyze(magnetogram)
    else:
        try:
            harp_num = int(harp_num)
        except:
            print('Operation failed: please enter a valid HARP number.')
            exit()
        magnetogram = binary_search(magnetograms, harp_num)
        if magnetogram is None:
            print('Operation failed: HARP number does not exist within dataset.')
            exit()
        print()
        analyze(magnetogram)
