__author__ = 'Brian Mark Anderson'
import os
import pydicom, copy
from threading import Thread
from multiprocessing import cpu_count
from queue import *


def worker_def(A):
    q, overlapping_images, overlapping_liver, min_size = A
    make_uid = make_uid_class(overlapping_images, overlapping_liver, min_size)
    while True:
        item = q.get()
        if item is None:
            break
        else:
            try:
                make_uid.make_uid(item)
            except:
                print('failed? ' + item)
            q.task_done()

def load_and_add_to_dict(A):
    dictionary_dicom = A[0]
    dicom_path = A[1]
    file = A[2]
    try:
        ds = pydicom.read_file(os.path.join(dicom_path,file))
        try:
            Acquistion_time = str(ds.AcquisitionTime)
        except:
            Acquistion_time = ds.StudyTime
            print('had an issue ?')
            Acquistion_time = Acquistion_time.replace('.', '')
        dictionary_dicom[file] = [file,Acquistion_time]
    except:
        print('double issue..')
        return None
    return None

class make_uid_class:
    def __init__(self, overlapping_images, overlapping_liver, min_size):
        self.paths_to_run = []
        self.overlapping_images = overlapping_images
        self.overlapping_liver = overlapping_liver
        self.min_size = min_size
        self.CT_Paths = []
        self.RT_Paths = []
    def make_uid_and_del_dic(self, dicom_path,files_all, data_keys):
        data_all = {}
        files = [i for i in files_all if i.find('.dcm') != -1] #If none of the files have a .dcm tag, we might have to go through them all
        if not files:
            files = files_all
        RT_val = 1
        for file in files:
            try:
                ds = pydicom.read_file(os.path.join(dicom_path, file))
            except:
                continue
            for split in [True, False]:
                for parameter in data_keys: #
                    if parameter in ds:
                        Acquistion_time = str(ds[parameter].value)
                        key_name = ds[parameter].name
                        if split:
                            key_name += '_Split'
                    else:
                        continue
                    if key_name not in data_all.keys():
                        data_all[key_name] = {}
                        del_dict = {}
                        uid_dic = {}
                    else:
                        del_dict, uid_dic = copy.deepcopy(data_all[key_name])
                    if split:
                        Acquistion_time = Acquistion_time.split('.')[0]
                    else:
                        Acquistion_time = Acquistion_time.replace('.', '')
                    if ds.Modality.find('RTSTRUCT') == 0 or ds.Modality.find('RTPLAN') == 0 or ds.Modality.find('RTDOSE') == 0:
                        Acquistion_time += str(RT_val)
                        RT_val += 1
                        if Acquistion_time not in uid_dic.keys():
                            uid_dic['RT_'+Acquistion_time] = [file]
                    elif ds.Modality == 'US':
                        continue
                    elif len(files) > self.min_size:
                        if Acquistion_time not in uid_dic.keys():
                            uid_dic[Acquistion_time] = [file]
                        else:
                            uid_dic[Acquistion_time].append(file)
                        try:
                            image_orientation = ''.join([str(i) for i in ds.ImageOrientationPatient])
                            if image_orientation not in del_dict.keys():
                                del_dict[image_orientation] = [file]
                            else:
                                del_dict[image_orientation].append(file)
                        except:
                            xxx = 1
                    data_all[key_name] = del_dict, uid_dic
        return data_all, ds
    def make_uid(self,dicom_path):
        print(dicom_path)
        if os.path.exists(os.path.join(dicom_path,'UID_val.txt')):
            os.remove(os.path.join(dicom_path,'UID_val.txt'))
        if os.path.exists(os.path.join(dicom_path,'MRN_val.txt')):
            os.remove(os.path.join(dicom_path,'MRN_val.txt'))
            #)
        file_list = []
        dirs = []
        for root, dirs, file_list in os.walk(dicom_path):
            break
        files = [file for file in file_list if file.find('.dcm') != -1]
        if not files:
            files = file_list
        uid_dic = {}
        if not self.overlapping_images:  # If we know there aren't overlapping image sets, move on
            for file in files:
                if file.find('{') != -1 or file.find('}') != -1:
                    os.remove(os.path.join(dicom_path,file))
                    continue
                try:
                    ds = pydicom.read_file(os.path.join(dicom_path,file))
                    try:
                        Acquistion_time = str(ds.SeriesTime)
                    except:
                        Acquistion_time = ds.StudyTime
                        Acquistion_time = Acquistion_time.replace('.', '')
                    keys = uid_dic.keys()
                    if ds.Modality.find('RTSTRUCT') == 0:
                        RT_val = 1
                        Acquistion_time += str(RT_val)
                        if Acquistion_time not in keys:
                            uid_dic[Acquistion_time] = [file]
                    elif len(files) > self.min_size:
                        if Acquistion_time not in keys:
                            uid_dic[Acquistion_time] = [file]
                    break
                except:
                    continue
        else:
            if self.overlapping_liver:
                data_keys = [(0x08,0x033), (0x08,0x032), (0x08,0x031), (0x08,0x030), (0x008,0x021), (0x008,0x022),(0x008,0x02a),(0x020,0x012)]
            else:
                data_keys = [(0x08,0x031),(0x020,0x012)]
            data_keys = [(0x08, 0x031), (0x020, 0x012)]
            try:
                data_all, ds = self.make_uid_and_del_dic(dicom_path,files, data_keys) # Acquisition Time
            except:
                return None
            go_on = False
            output = 2
            while not go_on:
                output -= 1
                if output < 0:
                    break
                min_images = 51
                while min_images > 0:
                    for key in data_all.keys():
                        if len(list(data_all[key][1].keys())) > output and \
                                len(files)/len(list(data_all[key][1].keys())) >= min_images: #len(list(data_all[key][1].keys())) <= 7 and
                            output = len(list(data_all[key][1].keys()))
                            del_dict, uid_dic = data_all[key]
                            go_on = True
                    if go_on:
                        break
                    min_images -= 10
            for key in del_dict.keys():
                if len(del_dict[key]) == 1: # If we have one image that wrong orientation, delete it
                    os.remove(os.path.join(dicom_path,del_dict[key][0]))
        if (len(uid_dic.keys()) > 1) or (len(dirs) > 0 and 'query_file' not in dirs): # We have multiple scans.. need to make new folders for each and change the uids
            i = -1
            for key in uid_dic.keys():
                i += 1
                files_total = uid_dic[key]
                for file_name in files_total:
                    if os.path.exists(os.path.join(dicom_path,key,file_name)):
                        os.remove(os.path.join(dicom_path,file_name)) # If it already exists, just move on
                        continue
                    if self.overlapping_liver and key.find('RT') != 0 and len(files_total) > self.min_size:
                        ds = pydicom.read_file(os.path.join(dicom_path,file_name))
                        ds.SeriesInstanceUID += '.' + str(i)
                        pydicom.write_file(os.path.join(dicom_path,file_name),ds)
                    if ds.Modality != 'US': #Raystation can't handle ultrasound
                        if len(files_total) > self.min_size or key.find('RT') == 0:
                            if not os.path.exists(os.path.join(dicom_path,key)):
                                os.mkdir(os.path.join(dicom_path ,key))
                            os.rename(os.path.join(dicom_path,file_name),os.path.join(dicom_path,key,file_name))
                    else:
                        os.remove(os.path.join(dicom_path,file_name))
                if ds.Modality != 'US' and (len(files_total) > self.min_size or key.find('RT') == 0):
                    fid = open(os.path.join(dicom_path,key,'UID_val.txt'), 'w+')
                    if ds.Modality != 'RTSTRUCT':
                        fid.write(ds.SeriesInstanceUID)
                    else:
                        fid.write(ds.StudyInstanceUID)
                    fid.close()
                    fid = open(os.path.join(dicom_path,key,'MRN_val.txt'), 'w+')
                    fid.write(ds.PatientID)
                    fid.close()
                    fid = open(os.path.join(dicom_path,key,'prepped.txt'), 'w+')
                    fid.close()
        elif len(uid_dic.keys()) > 0:

            fid = open(os.path.join(dicom_path ,'UID_val.txt'), 'w+')
            if ds.Modality != 'RTSTRUCT' and ds.Modality != 'RTPLAN' and ds.Modality != 'RTDOSE':
                fid.write(ds.SeriesInstanceUID)
            else:
                fid.write(ds.StudyInstanceUID)
            fid.close()

            try:
                MRN_val = ds.PatientID
            except:
                MRN_val = 0

            fid = open(os.path.join(dicom_path, 'MRN_val.txt'), 'w+')
            fid.write(MRN_val)
            fid.close()
            fid = open(os.path.join(dicom_path, 'prepped.txt'), 'w+')
            fid.close()
        return None

class prep_dicom:
    def __init__(self):
        xxx = 1
        # self.make_pool()

    def build(self, overlapping_images, overlapping_liver, min_size):
        self.paths_to_run = []
        self.overlapping_images = overlapping_images
        self.overlapping_liver = overlapping_liver
        self.min_size = min_size
        self.CT_Paths = []
        self.RT_Paths = []
        self.uid_class = make_uid_class(overlapping_liver=overlapping_liver,
                                        overlapping_images=overlapping_images,min_size=min_size)

    def get_input_paths(self, input_path='C:\\Liver_Ablation_Patients\\For Import\\'):
        self.path = input_path
        self.pat_id = 0
        files = []
        dirs = []
        root = []
        for root, dirs, files in os.walk(input_path):
            break
        go = False
        if files and input_path.find('query_file') == -1 and 'imported.txt' not in files and 'prepped.txt' not in files:
            for file in files:
                if file[-4:].lower() == '.dcm' or file.find('CT') == 0 or file.find('IM') == 0:
                    go = True
                    break
            if go:
                self.paths_to_run.append(input_path)
        if 'prepped.txt' in files:
            self.pat_id += 1

        for dir in dirs:
            self.get_input_paths(os.path.join(root,dir))
        return None

    def make_uids(self):
        thread_count = cpu_count() - 1 # Leaves you one thread for doing things with
        # thread_count = 1
        print('This is running on ' + str(thread_count) + ' threads')
        q = Queue(maxsize=thread_count)
        A = [q,self.overlapping_images, self.overlapping_liver, self.min_size]
        threads = []
        for worker in range(thread_count):
            t = Thread(target=worker_def, args=(A,))
            t.start()
            threads.append(t)
        for input_path in self.paths_to_run:
            # self.make_uid(input_path)
            q.put(input_path)
        for i in range(thread_count):
            q.put(None)
        for t in threads:
            t.join()

    def make_uid_and_del_dic(self, dicom_path,files_all, data_keys):
        data_all = {}
        files = [i for i in files_all if i.find('.dcm') != -1] #If none of the files have a .dcm tag, we might have to go through them all
        if not files:
            files = files_all
        RT_val = 1
        for file in files:
            try:
                ds = pydicom.read_file(os.path.join(dicom_path, file))
            except:
                continue
            for split in [True, False]:
                for parameter in data_keys: #
                    if parameter in ds:
                        Acquistion_time = str(ds[parameter].value)
                        key_name = ds[parameter].name
                        if split:
                            key_name += '_Split'
                    else:
                        continue
                    if key_name not in data_all.keys():
                        data_all[key_name] = {}
                        del_dict = {}
                        uid_dic = {}
                    else:
                        del_dict, uid_dic = copy.deepcopy(data_all[key_name])
                    if split:
                        Acquistion_time = Acquistion_time.split('.')[0]
                    else:
                        Acquistion_time = Acquistion_time.replace('.', '')
                    if ds.Modality.find('RTSTRUCT') == 0 or ds.Modality.find('RTPLAN') == 0 or ds.Modality.find('RTDOSE') == 0:
                        Acquistion_time += str(RT_val)
                        RT_val += 1
                        if Acquistion_time not in uid_dic.keys():
                            uid_dic['RT_'+Acquistion_time] = [file]
                    elif ds.Modality == 'US':
                        continue
                    elif len(files) > self.min_size:
                        if Acquistion_time not in uid_dic.keys():
                            uid_dic[Acquistion_time] = [file]
                        else:
                            uid_dic[Acquistion_time].append(file)
                        try:
                            image_orientation = ''.join([str(i) for i in ds.ImageOrientationPatient])
                            if image_orientation not in del_dict.keys():
                                del_dict[image_orientation] = [file]
                            else:
                                del_dict[image_orientation].append(file)
                        except:
                            xxx = 1
                    data_all[key_name] = del_dict, uid_dic
        return data_all, ds
    def make_uid(self,dicom_path):
        print(dicom_path)
        if os.path.exists(os.path.join(dicom_path,'UID_val.txt')):
            os.remove(os.path.join(dicom_path,'UID_val.txt'))
        if os.path.exists(os.path.join(dicom_path,'MRN_val.txt')):
            os.remove(os.path.join(dicom_path,'MRN_val.txt'))
            #)
        file_list = []
        dirs = []
        for root, dirs, file_list in os.walk(dicom_path):
            break
        files = [file for file in file_list if file.find('.dcm') != -1]
        if not files:
            files = file_list
        uid_dic = {}
        if not self.overlapping_images:  # If we know there aren't overlapping image sets, move on
            for file in files:
                if file.find('{') != -1 or file.find('}') != -1:
                    os.remove(os.path.join(dicom_path,file))
                    continue
                try:
                    ds = pydicom.read_file(os.path.join(dicom_path,file))
                    try:
                        Acquistion_time = str(ds.SeriesTime)
                    except:
                        Acquistion_time = ds.StudyTime
                        Acquistion_time = Acquistion_time.replace('.', '')
                    keys = uid_dic.keys()
                    if ds.Modality.find('RTSTRUCT') == 0:
                        RT_val = 1
                        Acquistion_time += str(RT_val)
                        if Acquistion_time not in keys:
                            uid_dic[Acquistion_time] = [file]
                    elif len(files) > self.min_size:
                        if Acquistion_time not in keys:
                            uid_dic[Acquistion_time] = [file]
                    break
                except:
                    continue
        else:
            if self.overlapping_liver:
                data_keys = [(0x08,0x033), (0x08,0x032), (0x08,0x031), (0x08,0x030), (0x008,0x021), (0x008,0x022),(0x008,0x02a),(0x020,0x012)]
            else:
                data_keys = [(0x08,0x031),(0x020,0x012)]
            data_keys = [(0x08, 0x031), (0x020, 0x012)]
            try:
                data_all, ds = self.make_uid_and_del_dic(dicom_path,files, data_keys) # Acquisition Time
            except:
                return None
            go_on = False
            output = 2
            while not go_on:
                output -= 1
                min_images = 51
                while min_images > 0:
                    for key in data_all.keys():
                        if len(list(data_all[key][1].keys())) > output and \
                                len(files)/len(list(data_all[key][1].keys())) >= min_images: #len(list(data_all[key][1].keys())) <= 7 and
                            output = len(list(data_all[key][1].keys()))
                            del_dict, uid_dic = data_all[key]
                            go_on = True
                    if go_on:
                        break
                    min_images -= 10
            for key in del_dict.keys():
                if len(del_dict[key]) == 1: # If we have one image that wrong orientation, delete it
                    os.remove(os.path.join(dicom_path,del_dict[key][0]))
        if (len(uid_dic.keys()) > 1) or (len(dirs) > 0 and 'query_file' not in dirs): # We have multiple scans.. need to make new folders for each and change the uids
            i = -1
            for key in uid_dic.keys():
                i += 1
                files_total = uid_dic[key]
                for file_name in files_total:
                    if os.path.exists(os.path.join(dicom_path,key,file_name)):
                        os.remove(os.path.join(dicom_path,file_name)) # If it already exists, just move on
                        continue
                    if self.overlapping_liver and key.find('RT') != 0 and len(files_total) > self.min_size:
                        ds = pydicom.read_file(os.path.join(dicom_path,file_name))
                        ds.SeriesInstanceUID += '.' + str(i)
                        pydicom.write_file(os.path.join(dicom_path,file_name),ds)
                    if ds.Modality != 'US': #Raystation can't handle ultrasound
                        if len(files_total) > self.min_size or key.find('RT') == 0:
                            if not os.path.exists(os.path.join(dicom_path,key)):
                                os.mkdir(os.path.join(dicom_path ,key))
                            os.rename(os.path.join(dicom_path,file_name),os.path.join(dicom_path,key,file_name))
                    else:
                        os.remove(os.path.join(dicom_path,file_name))
                if ds.Modality != 'US' and (len(files_total) > self.min_size or key.find('RT') == 0):
                    fid = open(os.path.join(dicom_path,key,'UID_val.txt'), 'w+')
                    if ds.Modality != 'RTSTRUCT':
                        fid.write(ds.SeriesInstanceUID)
                    else:
                        fid.write(ds.StudyInstanceUID)
                    fid.close()
                    fid = open(os.path.join(dicom_path,key,'MRN_val.txt'), 'w+')
                    fid.write(ds.PatientID)
                    fid.close()
                    fid = open(os.path.join(dicom_path,key,'prepped.txt'), 'w+')
                    fid.close()
        elif len(uid_dic.keys()) > 0:

            fid = open(os.path.join(dicom_path ,'UID_val.txt'), 'w+')
            if ds.Modality != 'RTSTRUCT' and ds.Modality != 'RTPLAN' and ds.Modality != 'RTDOSE':
                fid.write(ds.SeriesInstanceUID)
            else:
                fid.write(ds.StudyInstanceUID)
            fid.close()

            try:
                MRN_val = ds.PatientID
            except:
                MRN_val = 0

            fid = open(os.path.join(dicom_path, 'MRN_val.txt'), 'w+')
            fid.write(MRN_val)
            fid.close()
            fid = open(os.path.join(dicom_path, 'prepped.txt'), 'w+')
            fid.close()
        return None
if __name__ ==  '__main__':
    xxx = 1