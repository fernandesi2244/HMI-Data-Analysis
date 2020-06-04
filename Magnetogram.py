import sunpy.map
import astropy.units as u
import matplotlib.pyplot as plt

#TODO: Associate HARP# with AR. Make HARP # dictionary with all files related to that HARP number

class Magnetogram(object):
    def __init__(self, file_name, harp_num, SHARPS_parameters):
        self.file_name = file_name
        self.harp_num = harp_num
        self.SHARPS_parameters = SHARPS_parameters
    
    def generate_info(self):
        print(f'HMI Active Region Patch #{self.harp_num}')

        for parameter_name in self.SHARPS_parameters:
            print(f'{parameter_name}: {self.SHARPS_parameters[parameter_name]:,f}')
    
    def plot(self, clip = None):
        magnetogram = sunpy.map.Map(self.file_name)
        magnetogram.plot_settings['title'] = 'Magnetogram for HARP #'+str(self.harp_num)
        
        if clip is None:
            magnetogram.peek()
        else:
            fig = plt.figure(figsize=(12,4))
            ax1 = fig.add_subplot(1,2,1, projection = magnetogram)
            magnetogram.plot(title='Without Clipping')

            ax2 = fig.add_subplot(1,2,2, projection = magnetogram)
            magnetogram.plot(clip_interval=clip, title='With Clipping')

            plt.colorbar(extend='both')
            plt.show()
    
    def __str__(self):
        return 'HARP Number: '+str(self.harp_num)