__author__ = 'Brian Mark Anderson'
import os
import shutil
import pydicom
from threading import Thread
from queue import *


def worker_def(q):
    while True:
        item = q.get()
        if item is None:
            break
        else:
            shuttle_files(item)
            q.task_done()


def shuttle_files(data):
    path, file = data
    if os.path.exists(os.path.join(path,'query_file')):
        for file_del in os.listdir(os.path.join(path,'query_file')):
            os.remove(os.path.join(path,'query_file', file_del))
    else:
        os.mkdir(os.path.join(path,'query_file'))
    try:
        shutil.copy(os.path.join(path,file),os.path.join(path,'query_file',file))
    except:
        print('Had a copy issue here...')
    return None


class get_directories:
    def __init__(self,path = 'C:\\',out_path = 'C:\\'):
        self.path = path
        self.CT_Folder = []
        self.RT_Folder = []
        self.Dose_Folder = []
        self.out_path = out_path
        self.file_shutil_info = {}
        self.down_folder(path)
        thread_count = 12
        q = Queue(maxsize=thread_count)
        threads = []
        for worker in range(thread_count):
            t = Thread(target=worker_def, args=(q,))
            t.start()
            threads.append(t)
        for key in self.file_shutil_info.keys():
            # self.file_shutil_info[key]
            q.put(self.file_shutil_info[key])
        q.join()
        for worker in range(thread_count):
            q.put(None)
        for t in threads:
            t.join()
        self.print_vals()
    def print_vals(self):
        fid = open(os.path.join(self.out_path,'RayStation_Paths.txt'),'w+')
        print(str(len(self.CT_Folder) + len(self.RT_Folder) + len(self.Dose_Folder)) + ' patients to do...')
        for out_path in self.CT_Folder:
            fid.write(out_path + ',')
        fid.write('\n')
        for path in self.RT_Folder:
            fid.write(path + ',')
        for path in self.Dose_Folder:
            fid.write(path + ',')
        fid.close()
        print('File paths are located at: ' + self.out_path)
        return None
    def down_folder(self,path):
        files = []
        dirs = []
        file = []
        ds = []
        root = ''
        for root, dirs, files in os.walk(path):
            break
        if path.find('query_file') == -1:
            if (('done.txt' not in files and 'prepped.txt' in files) or 'Completed.txt' in files) and \
                    'imported.txt' not in files and 'Imported.txt' not in files:
                print(path)
                for val in files:
                    if val.find('.dcm') != -1 or val.find('IM') != -1 or val.find('CT') == 0:
                        file = val
                        ds = pydicom.read_file(os.path.join(path,file))
                        break
                if not ds:
                    for file in files:
                        try:
                            ds = pydicom.read_file(os.path.join(path,file))
                            break
                        except:
                            continue
                if ds:
                    try:
                        if str(ds.SOPClassUID).find('Secondary') == 0:
                            go = False
                        else:
                            go = True
                    except:
                        go = True
                    if go:
                        if (ds.Modality == 'CT' or ds.Modality == "MR") and ds.Modality != 'RTPLAN' and ds.Modality != 'RTDOSE' \
                                and str(ds.SOPClassUID).find('Secondary') == -1:
                            if len(os.listdir(path)) >= 1:
                                if ds.Modality == "MR":
                                    if ds.ImageType[0] != 'DERIVED':
                                        self.file_shutil_info[path + file] = [path, file]
                                        self.CT_Folder.append(path)
                                else:
                                    self.file_shutil_info[path + file] = [path, file]
                                    self.CT_Folder.append(path)
                        elif ds.Modality == 'RTSTRUCT':
                            self.RT_Folder.append(path)
                        else:
                            self.Dose_Folder.append(path)
        for dir in dirs:
            self.down_folder(os.path.join(root,dir))
if __name__ == '__main__':
    #path = 'C:\\Users\\BMAnderson\\Fuller_Patients\\'
    #path = 'R:\\Carlos Cardenas\\GTVp-GTVn Project\\'
    path = 'L:\\Morfeus\\BMAnderson\\MRI_Cervix_Patients\\'
    path = 'L:\\Morfeus\\BMAnderson\\New_Liver_Koay\\'
    path = 'C:\\Liver_Ablation_Patients\\For_Import\\'
    path = 'L:\\Morfeus\\BMAnderson\\New_Liver_Koay\\3.16.18\\'
    path = 'L:\\Morfeus\\BMAnderson\\MRI_Cervix_Patients\\Velocity\\'
    path = 'L:\\Morfeus\\bmanderson\\MRI_Cervix_Patients\\Velocity\\'
    path = 'L:\\Morfeus\\bmanderson\\CNN\\Data\\Data_Chung_Brain\\Kantor_patients_Transfer_Inst\\'
    path = 'L:\\Morfeus\\ZYang\\Liver\\'
    path = 'K:\\Morfeus\\BMAnderson\\pacs_copy_3\\'
    # paths = get_directories(path=path,out_path=path)
    xxx = 1