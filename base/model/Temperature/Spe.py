# -*- coding: utf-8 -*-
# T-Rax - GUI program for analysis of spectroscopy data during
# diamond anvil cell experiments
# Copyright (C) 2016 Clemens Prescher (clemens.prescher@gmail.com)
# Institute for Geology and Mineralogy, University of Cologne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Implements the SPE_File class for loading princeton instrument binary SPE files into Python
works for version 2 and version 3 files.

Usage:
mydata = SPE_File('data.spe')

most important properties:

num_frames - number of frames collected
exposure_time

img - 2d data if num_frames==1
      list of 2d data if num_frames>1  

x_calibration - wavelength information of x-axis



the data will be automatically loaded and all important parameters and the data 
can be requested from the object.
"""

import os
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET

from dateutil import parser
import datetime
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import polyval
import pandas as pd

class SpeFile(object):
    def __init__(self, *, filepath):
        """Opens the PI SPE file and loads its content

        :param filename: filename of the PI SPE to open
        :param debug: if set to true, will automatically save <filename>.xml files for version 3 spe files in the spe
        directory
        """
        """"""
        self.filename = filepath
        print(f"ファイル: {self.filename}")
        self.debug = False
        self._fid = open(self.filename, 'rb')
        self._read_parameter()
        self._read_img()
        self.img = np.array(self.img) # list of 2d-ndarray -> 3d-ndarrayへの変換
        self.xml_parser(print_flag=False)
        self._fid.close()

    def _read_parameter(self):
        """Reads in size and datatype. Decides whether it should check in the binary
        header (version 2) or in the xml-footer for the experimental parameters"""
        self._read_size()
        self._read_datatype()
        self.xml_offset = self._read_at(678, 1, np.int_)[0]
        if self.xml_offset <= 0:  # means that there is no XML present, hence it is a pre 3.0 version of the SPE
            # file
            self._read_parameter_from_header()
        else:
            try:
                self._read_parameter_from_dom()
            except: # if fails for any reason, try reading from the header
                self._read_parameter_from_header()

    def _read_size(self):
        """reads the dimensions of the Model from the header into the object
        resulting object parameters are _xdim and _ydim"""
        self._xdim = np.int64(self._read_at(42, 1, np.int16)[0])
        self._ydim = np.int64(self._read_at(656, 1, np.int16)[0])

    def _read_parameter_from_header(self):
        """High level function which calls all the read_"parameter" function
        that are reading information from the binary header.
        """
        self._read_date_time_from_header()
        self._read_calibration_from_header()
        self._read_exposure_from_header()
        self._read_detector_from_header()
        self._read_grating_from_header()
        self._read_center_wavelength_from_header()
        self._read_roi_from_header()
        self._read_num_frames_from_header()
        self._read_num_combined_frames_from_header()

    def _read_parameter_from_dom(self):
        """High level function which calls all the read_"parameter" function
        that are reading information from the xml footer.
        """
        self._get_xml_string()
        self._create_dom_from_xml()
        self._read_date_time_from_dom()
        self._read_calibration_from_dom()
        self._read_detector_from_dom()
        self._read_exposure_from_dom()
        self._read_grating_from_dom()
        self._read_center_wavelength_from_dom()
        self._read_roi_from_dom()
        self._select_wavelength_from_roi()
        self._read_num_frames_from_header()
        self._read_num_combined_frames_from_dom()

    def _read_date_time_from_header(self):
        """Reads the collection time from the header into the date_time field"""
        rawdate = self._read_at(20, 9, np.int8)
        rawtime = self._read_at(172, 6, np.int8)
        strdate = ''.join([chr(i) for i in rawdate])
        strdate += ''.join([chr(i) for i in rawtime])
        import locale
        locale.setlocale(locale.LC_TIME, 'en_US.utf8')
        try:
            self.date_time = datetime.datetime.strptime(str(strdate), "%d%b%Y%H%M%S")
        except:
            print('WARNING: could note read datetime from SPE_FILE')
            self.date_time = datetime.datetime.now()


    def _read_calibration_from_header(self):
        """Reads the calibration from the header into the x_calibration field"""
        x_polynocoeff = self._read_at(3263, 6, np.double)
        x_val = np.arange(self._xdim) + 1
        self.x_calibration = np.array(polyval(x_val, x_polynocoeff))

    def _read_exposure_from_header(self):
        """Reads the exposure time from the header into the exposure_time field"""
        self.exposure_time = self._read_at(10, 1, np.float32)
        self.exposure_time = self.exposure_time[0]

    def _read_detector_from_header(self):
        """Sets the detector value to unspecified, because the detector is not
        specified in the binary header. Only in the xml footer of version 3 SPE
        files """
        self.detector = 'unspecified'

    def _read_grating_from_header(self):
        """Reads grating position from the header into the grating field"""
        self.grating = str(self._read_at(650, 1, np.float32)[0])

    def _read_center_wavelength_from_header(self):
        """Reads center wavelength position from the header into the center_wavelength field"""
        self.center_wavelength = float(self._read_at(72, 1, np.float32)[0])

    def _read_roi_from_header(self):
        return

    def _read_num_frames_from_header(self):
        self.num_frames = self._read_at(1446, 1, np.int32)[0]

    def _read_num_combined_frames_from_header(self):
        self._num_combined_frames = 1

    def _create_dom_from_xml(self):
        """Creates a DOM representation of the xml footer and saves it in the
        dom field"""
        self.dom = parseString(self.xml_string)

    def _get_xml_string(self):
        """Reads out the xml string from the file end"""
        self._fid.seek(int(self.xml_offset))
        self.xml_string = self._fid.read()

        if self.debug:
            fid = open(self.filename+'.xml', 'w')
            for line in self.xml_string:
                fid.write(line)
            fid.close()

    def _read_date_time_from_dom(self):
        """Reads the time of collection and saves it date_time field"""
        date_time_str = self.dom.getElementsByTagName('Origin')[0].getAttribute('created')
        self.date_time = parser.parse(date_time_str)

    def _read_calibration_from_dom(self):
        """Reads the x calibration of the image from the xml footer and saves 
        it in the x_calibration field"""
        spe_format = self.dom.childNodes[0]
        calibrations = spe_format.getElementsByTagName('Calibrations')[0]
        wavelengthmapping = calibrations.getElementsByTagName('WavelengthMapping')[0]
        wavelengths = wavelengthmapping.getElementsByTagName('Wavelength')[0]
        wavelength_values = wavelengths.childNodes[0]
        self.x_calibration = np.array([float(i) for i in wavelength_values.toxml().split(',')])

    def _read_exposure_from_dom(self):
        """Reads th exposure time of the experiment into the exposure_time field"""
        if len(self.dom.getElementsByTagName('Experiment')) != 1:  # check if it is a real v3.0 file
            if len(self.dom.getElementsByTagName('ShutterTiming')) == 1:  #check if it is a pixis detector
                self._exposure_time = self.dom.getElementsByTagName('ExposureTime')[0].childNodes[0]
                self.exposure_time = float(self._exposure_time.toxml()) / 1000.0
            else:
                self._exposure_time = self.dom.getElementsByTagName('ReadoutControl')[0]. \
                    getElementsByTagName('Time')[0].childNodes[0].nodeValue
                self._exposure_time = float(self._exposure_time)/1000000000
                self._exposure_time = self.dom.getElementsByTagName('Gating')[0]. \
                    getElementsByTagName('RepetitiveGate')[0].getElementsByTagName('Pulse')[0].getAttribute('width')
                self._exposure_time = float(self._exposure_time)/1000000000
                self._accumulations = self.dom.getElementsByTagName('Accumulations')[0].childNodes[0].nodeValue
                self.exposure_time = float(self._exposure_time) * float(self._accumulations)
        else:  # this is searching for legacy experiment:
            self._exposure_time = self.dom.getElementsByTagName('LegacyExperiment')[0]. \
                getElementsByTagName('Experiment')[0]. \
                getElementsByTagName('CollectionParameters')[0]. \
                getElementsByTagName('Exposure')[0].attributes["value"].value
            self.exposure_time = float(self._exposure_time.split()[0])

    def _read_detector_from_dom(self):
        """Reads the detector information from the dom object"""
        self._camera = self.dom.getElementsByTagName('Camera')
        if len(self._camera) >= 1:
            self.detector = self._camera[0].getAttribute('model')
        else:
            self.detector = 'unspecified'

    def _read_grating_from_dom(self):
        """Reads the type of grating from the dom Model"""
        try:
            self._grating = self.dom.getElementsByTagName('Devices')[0]. \
                getElementsByTagName('Spectrometer')[0]. \
                getElementsByTagName('Grating')[0]. \
                getElementsByTagName('Selected')[0].childNodes[0].toxml()
            self.grating = self._grating.split('[')[1].split(']')[0].replace(',', ' ')
        except IndexError:
            self._read_grating_from_header()

    def _read_center_wavelength_from_dom(self):
        """Reads the center wavelength from the dom Model and saves it center_wavelength field"""
        try:
            self._center_wavelength = self.dom.getElementsByTagName('Devices')[0]. \
                getElementsByTagName('Spectrometer')[0]. \
                getElementsByTagName('Grating')[0]. \
                getElementsByTagName('CenterWavelength')[0]. \
                childNodes[0].toxml()
            self.center_wavelength = float(self._center_wavelength)
        except IndexError:
            self._read_center_wavelength_from_header()

    def _read_roi_from_dom(self):
        """Reads the ROIs information defined in the SPE file.
        Depending on the modus it will read out:
        For CustomRegions
        roi_x, roi_y, roi_width, roi_height, roi_x_binning, roi_y_binning
        For FullSensor
        roi_x,roi_y, roi_width, roi_height"""
        try:
            self.roi_modus = str(self.dom.getElementsByTagName('ReadoutControl')[0]. \
                                 getElementsByTagName('RegionsOfInterest')[0]. \
                                 getElementsByTagName('Selection')[0]. \
                                 childNodes[0].toxml())
            if self.roi_modus == 'CustomRegions':
                self.roi_dom = self.dom.getElementsByTagName('ReadoutControl')[0]. \
                    getElementsByTagName('RegionsOfInterest')[0]. \
                    getElementsByTagName('CustomRegions')[0]. \
                    getElementsByTagName('RegionOfInterest')[0]
                self.roi_dom_width = self.dom.getElementsByTagName('DataFormat')[0]. \
                    getElementsByTagName('DataBlock')[0]. \
                    getElementsByTagName('DataBlock')[0]
                self.roi_x = int(self.roi_dom.attributes['x'].value)
                self.roi_y = int(self.roi_dom.attributes['y'].value)
                self.roi_width = int(self.roi_dom_width.attributes['width'].value)
                self.roi_height = int(self.roi_dom.attributes['height'].value)
                self.roi_x_binning = int(self.roi_dom.attributes['xBinning'].value)
                self.roi_y_binning = int(self.roi_dom.attributes['yBinning'].value)
            elif self.roi_modus == 'FullSensor':
                self.roi_x = 0
                self.roi_y = 0
                self.roi_width = self._xdim
                self.roi_height = self._ydim
            elif self.roi_modus == 'LineSensor':
                self.roi_dom_width = self.dom.getElementsByTagName('DataFormat')[0]. \
                                        getElementsByTagName('DataBlock')[0].\
                                        getElementsByTagName('DataBlock')[0]
                self.roi_width = int(self.roi_dom_width.attributes['width'].value)
                self.roi_height = 1
                self.roi_x = 0
                self.roi_y = 0
                self._xdim = self.roi_width
                self._ydim = 1

        except IndexError:
            self.roi_x = 0
            self.roi_y = 0
            self.roi_width = self._xdim
            self.roi_height = self._ydim

    def _read_num_combined_frames_from_dom(self):
        try:
            self.frame_combination = self.dom.getElementsByTagName('Experiment')[0]. \
                getElementsByTagName('Devices')[0]. \
                getElementsByTagName('Cameras')[0]. \
                getElementsByTagName('FrameCombination')[0]
            self.num_frames_combined = int(self.frame_combination.getElementsByTagName('FramesCombined')[0]. \
                                           childNodes[0].toxml())
        except IndexError:
            self._read_num_combined_frames_from_header()

    def _select_wavelength_from_roi(self):
        try:
            self.x_calibration = self.x_calibration[self.roi_x: self.roi_x + self.roi_width]
        except AttributeError:
            print("SPE File bad!")

    def _read_datatype(self):
        self._data_type = self._read_at(108, 1, np.uint16)[0]

    def _read_at(self, pos, size, ntype):
        pos = int(pos)
        size = int(size)
        self._fid.seek(pos)
        return np.fromfile(self._fid, ntype, size)

    def _read_img(self):
        self.img = self._read_frame(4100)
        if self.num_frames > 1:
            img_temp = []
            img_temp.append(self.img)
            for n in range(self.num_frames - 1):
                img_temp.append(self._read_frame())
            self.img = img_temp

    def _read_frame(self, pos=None):
        """Reads in a frame at a specific binary position. The following parameters have to
        be predefined before calling this function:
        datatype - either 0,1,2,3,8 for float32, int32, int16, uint16 or uint32 (datatypes can be found on page 10 in
        the SPE 3.0 File format manual)
        _xdim, _ydim - being the dimensions.
        """
        if pos == None:
            pos = self._fid.tell()
        if self._data_type == 0:
            img = self._read_at(pos, self._xdim * self._ydim, np.float32)
        elif self._data_type == 1:
            img = self._read_at(pos, self._xdim * self._ydim, np.int32)
        elif self._data_type == 2:
            img = self._read_at(pos, self._xdim * self._ydim, np.int16)
        elif self._data_type == 3:
            img = self._read_at(pos, self._xdim * self._ydim, np.uint16)
        elif self._data_type == 8:
            img = self._read_at(pos, self._xdim * self._ydim, np.uint32)
        return img.reshape((self._ydim, self._xdim))

    def get_index_from(self, wavelength):
        """
        calculating image index for a given index
        :param wavelength: wavelength in nm
        :return: index
        """
        result = []
        xdata = self.x_calibration
        try:
            for w in wavelength:
                try:
                    base_ind = max(max(np.where(xdata <= w)))
                    if base_ind < len(xdata) - 1:
                        result.append(int(np.round((w - xdata[base_ind]) / \
                                                   (xdata[base_ind + 1] - xdata[base_ind]) \
                                                   + base_ind)))
                    else:
                        result.append(base_ind)
                except:
                    result.append(0)
            return np.array(result)
        except TypeError:
            base_ind = max(max(np.where(xdata <= wavelength)))
            return int(np.round((wavelength - xdata[base_ind]) / \
                                (xdata[base_ind + 1] - xdata[base_ind]) \
                                + base_ind))

    def get_wavelength_from(self, index):
        if isinstance(index, list):
            result = []
            for c in index:
                result.append(self.x_calibration[c])
            return np.array(result)
        else:
            return self.x_calibration[index]


    def get_dimension(self):
        """Returns (xdim, ydim)"""
        return (self._xdim, self._ydim)

    def get_roi(self):
        """Returns the ROI which was defined by WinSpec or Lightfield for datacollection"""
        return [self.roi_x, self.roi_x + self.roi_width - 1,
                self.roi_y, self.roi_y + self.roi_height - 1]

    def get_file_size(self):
        self._fid.seek(0, 2)
        self.file_size = self._fid.tell()
        return self.file_size

    def xml_parser(self, print_flag=False):
        xml = self.xml_string
        str_xml = str(xml)
        list_xml = str_xml.split("<")

        # 特定の文字列が入っているものから情報を抜き出す
        for i, ele in enumerate(list_xml):
            if ('FrameRate r:readOnly' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }") # デバッグ用
                self.framerate = float(ele.split('>')[-1])
            if ('BaseFileName' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.basename = ele.split('>')[-1]
            if ('IncrementNumber' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.filenum = int(ele.split('>')[-1])
            if ('ReferenceFileDate r:readOnly' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.date = ele.split('>')[-1]
            if ('Date r:readOnly' in ele) and ('Reference' not in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.calibration_date = ele.split('>')[-1]
            if ('Name type' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.OD = ele.split('>')[-1]
        if print_flag:
            print(f"\n{self.framerate = }")
            print(f"{self.basename = }")
            print(f"{self.filenum = }")
            print(f"{self.date = }")
            print(f"{self.calibration_date = }")
            print(f"{self.OD = }")

    # TODO ここから下のメソッドはクラスに入れる必要ないので後から消す
    def set_intensity_array(self):
        frame_num = self.num_frames
        intensity_array_total = np.zeros(frame_num)
        intensity_array_up = np.zeros(frame_num)
        intensity_array_down = np.zeros(frame_num)
        for i in range(frame_num):
            df_img = pd.DataFrame(self.img[i])
            intensity_array_total[i] = df_img.sum().sum()
            intensity_array_up[i] = df_img.iloc[0:255, :].sum().sum()
            intensity_array_down[i] = df_img.iloc[256:511, :].sum().sum()
        self.img_intensity_total = intensity_array_total
        self.img_intensity_up = intensity_array_up
        self.img_intensity_down = intensity_array_down

    def get_plot_values(self):
        self.time_series = np.arange(self.num_frames) / self.framerate

    def plot_intensity_total(self, *,
                             overlap=False,
                             threshold=1.2,
                             close_to_threshold=False):
        figsize = (4, 4)
        dpi = 200
        facecolor = 'white'

        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor)
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(self.time_series, self.img_intensity_total, label='Total emission')

        ax.set_title('Optical emission intensity')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Intensity (a.u.)')
        ax.grid()
        ax.legend()

        unit_frame = 40 # とりあえず加熱直前を基準にしてる
        unit_intensity = self.img_intensity_total[unit_frame]

        if close_to_threshold:
            ax.set_ylim(0, unit_intensity * (threshold * 1.5))
        if overlap:
            return fig, ax
        else:
            ax.axhline(unit_intensity, color='black')
            ax.axhline(unit_intensity * threshold, color='orange')
            return None

    def plot_intensity_separate(self, *, overlap=False):
        figsize = (4, 4)
        dpi = 200
        facecolor = 'white'

        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor)
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(self.time_series, self.img_intensity_up,
                color='green',
                label='Up')
        ax.plot(self.time_series, self.img_intensity_down,
                color='orange',
                label='Down')

        ax.set_title('Optical emission intensity')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Intensity (a.u.)')
        ax.grid()
        ax.legend()
        if overlap:
            return fig, ax
        else:
            return None

def load(filepaths=None):
    """
    Allows user to load multiple files at once. Each file is stored as an SpeFile object in the list batch.
    """
    if filepaths is None:
        filepaths = get_files(mult=True)
    elif isinstance(filepaths, str):
        filepaths = [filepaths]
    batch = [[] for _ in range(0, len(filepaths))]
    for file in range(0, len(filepaths)):
        batch[file] = SpeFile(filepaths[file])
    return_type = "list of SpeFile objects"
    if len(batch) == 1:
        batch = batch[0]
        return_type = "SpeFile object"
    print('Successfully loaded %i file(s) in a %s' % (len(filepaths), return_type))
    return batch

def read_at(file, pos, size, ntype):
    """
    Reads SPE source file at specific byte position.
    Adapted from https://scipy.github.io/old-wiki/pages/Cookbook/Reading_SPE_files.html
    """
    file.seek(pos)
    return np.fromfile(file, ntype, size)


def imgobject(speobject, frame=0, roi=0):
    """
    Unbound function for imaging loaded data
    """
    img = plt.imshow(getattr(speobject, 'data')[frame][roi], cmap=cm.get_cmap('hot'))
    return img

def spe_info(spe:SpeFile) -> dict:
    filepath = spe.filename
    filename = os.path.splitext(os.path.basename(filepath))[0]

    spe_info = {
            'filepath': filepath,
            'filename': filename,
            'date_time': spe.date_time,
            'x_calibration': f"{spe.x_calibration[0]} nm to {spe.x_calibration[-1]} nm",
            'center_wavelength': spe.center_wavelength,
            #'debug': spe.debug,
            'detector': spe.detector,
            #'dom': spe.dom,
            #'frame_combination': spe.frame_combination,
            #'get_dimension': spe.get_dimension,
            #'get_file_size': spe.get_file_size,
            #'get_index_from': spe.get_index_from,
            #'get_roi': spe.get_roi,
            #'get_wavelength_from': spe.get_wavelength_from,
            'grating': spe.grating,
            'frame': len(spe.img),
            'shape': spe.img[0].shape,
            'num_frames': spe.num_frames,
            #'num_frames_combined': spe.num_frames_combined,
            #'roi_height': spe.roi_height,
            #'roi_modus': spe.roi_modus,
            #'roi_width': spe.roi_width,
            #'roi_x': spe.roi_x,
            #'roi_y': spe.roi_y,
            #'xml_offset': spe.xml_offset
            }

    """
    #spe_infoのdict要素を出力する(一応残してる)
    for i, attr in enumerate(dir(spe)):
        print(f"            '{attr}': spe.{attr},")
    """
    return spe_info


if __name__ == "__main__":
    spe = load()
else:
    print(f"{__name__: <30} is imported")
