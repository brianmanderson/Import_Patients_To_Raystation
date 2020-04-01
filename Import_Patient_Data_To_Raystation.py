import os
from connect import *
import time
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import OpenFileDialog, DialogResult


class import_dicom_class_8B:
    def __init__(self,round = 1):
        self.round = round
        self.rois_in_case = []
        self.exams = []
        try:
            self.patient = get_current('Patient')
            self.patient_id = self.patient.PatientID
            self.case = get_current('Case')
            for roi in self.case.PatientModel.RegionsOfInterest:
                self.rois_in_case.append(roi.Name)
            for exam in self.case.Examinations:
                self.exams.append(exam.Name)
        except:
            self.patient_id = '0'
        self.patient_db = get_current("PatientDB")
        self.imported_uids = []
        self.output = {}

    def import_dicoms_new(self,file_path):
        if os.path.exists(os.path.join(file_path,'imported.txt')):
            print('previously imported ' + str(self.round))
            return None
        print('going for ' + file_path)
        fid = open(os.path.join(file_path,'running.txt'),'w+')
        fid.close()
        fid = open(os.path.join(file_path,'UID_val.txt'))
        uid = fid.readline()
        fid.close()
        fid = open(os.path.join(file_path,'MRN_val.txt'))
        MRN = fid.readline()
        print(MRN)
        fid.close()
        if MRN not in self.output:
            self.output[MRN] = []
        if not uid:
            return None
        print('importing dicom')
        info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN})
        # If it isn't, see if it's in the secondary database
        if not info_all:
            info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN}, UseIndexService=True)
        info = []
        for info_temp in info_all:
            if info_temp['PatientID'] == MRN:
                info = info_temp
                break
        file = None
        check_path = file_path
        if os.path.exists(os.path.join(file_path, 'query_file')) and len(
                os.listdir(os.path.join(file_path, 'query_file'))) > 0:
            file = os.listdir(os.path.join(file_path, 'query_file'))
            check_path = os.path.join(file_path, 'query_file')
        pi = self.patient_db.QueryPatientsFromPath(Path=check_path, SearchCriterias={'PatientID':MRN})[0]
        studies = self.patient_db.QueryStudiesFromPath(Path=check_path,
                                                       SearchCriterias=pi)
        series = []
        for study in studies:
            series += self.patient_db.QuerySeriesFromPath(Path=check_path,
                                                          SearchCriterias=study)
        if file:
            os.remove(os.path.join(file_path, 'query_file', file[0]))
            os.rmdir(os.path.join(file_path, 'query_file'))
        if not info:
            self.patient_db.ImportPatientFromPath(Path=file_path, SeriesOrInstances=series)
            self.patient = get_current("Patient")
            self.patient_id = MRN
            self.patient_db = get_current("PatientDB") #Got a new patient, update the patient db
            self.case = get_current("Case")
        else:
            print('info found')
            if self.patient_id != MRN:
                print('patient id does not match MRN')
                if self.patient_id != '0':
                    self.patient.Save()
                print(info)
                try:
                    self.patient = self.patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)
                except:
                    self.patient_id = '0'
                    return None
                self.patient_id = self.patient.PatientID
                for case in self.patient.Cases:
                    self.case = case

            self.imported_uids = [e.Series[0].ImportedDicomUID for e in self.case.Examinations]
            self.exams = []
            for exam in self.case.Examinations:
                self.exams.append(exam.Name)
            if self.round == 1:
                if uid not in self.imported_uids and uid: #
                    try:
                        self.patient.ImportDataFromPath(Path=file_path, CaseName=self.case.CaseName,
                                                             SeriesOrInstances=series,AllowMismatchingPatientID=True)
                        fid = open(os.path.join(file_path, 'imported.txt'), 'w+')
                        fid.close()
                    except:
                        print('some kind of error')
                else:
                    print('already imported')
                    self.output[MRN].append(self.exams[self.imported_uids.index(uid)])
                    fid = open(os.path.join(file_path,'imported.txt'), 'w+')
                    fid.close()
            elif self.round == 2:
                self.patient.ImportDataFromPath(Path=file_path, CaseName=self.case.CaseName,
                                                SeriesOrInstances=series, AllowMismatchingPatientID=True)
                self.patient.Save()
                fid = open(os.path.join(file_path,'imported.txt'),'w+')
                fid.close()
        os.remove(os.path.join(file_path,'running.txt'))
        return None

class import_dicom_class:
    def __init__(self,round = 1):
        self.round = round
        self.rois_in_case = []
        self.exams = []
        try:
            self.patient = get_current('Patient')
            self.patient_id = self.patient.PatientID
            self.case = get_current('Case')
            for roi in self.case.PatientModel.RegionsOfInterest:
                self.rois_in_case.append(roi.Name)
            for exam in self.case.Examinations:
                self.exams.append(exam.Name)
        except:
            self.patient_id = '0'
        self.patient_db = get_current("PatientDB")
        self.imported_uids = []
        self.output = {}

    def import_dicoms_new(self,file_path):
        if os.path.exists(os.path.join(file_path,'imported.txt')):
            print('previously imported ' + str(self.round))
            return None
        print('going for ' + file_path)
        fid = open(os.path.join(file_path,'running.txt'),'w+')
        fid.close()
        fid = open(os.path.join(file_path,'UID_val.txt'))
        uid = fid.readline()
        fid.close()
        fid = open(os.path.join(file_path,'MRN_val.txt'))
        MRN = fid.readline()
        print(MRN)
        fid.close()
        if MRN not in self.output:
            self.output[MRN] = []
        if not uid:
            return None
        print('importing dicom')
        info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN})
        # If it isn't, see if it's in the secondary database
        if not info_all:
            info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN}, UseIndexService=True)
        info = []
        for info_temp in info_all:
            if info_temp['PatientID'] == MRN:
                info = info_temp
                break
        if not info:
            print('info not found')
            if os.path.exists(os.path.join(file_path,'query_file')) and len(os.listdir(os.path.join(file_path,'query_file'))) > 0:
                #Rather than query all 300+ CT slices, just query the one I put aside
                pi = self.patient_db.QueryPatientsFromPath(Path=os.path.join(file_path,'query_file'), Filter={})[0]
                file = os.listdir(os.path.join(file_path,'query_file'))
                #But Raystation can't have that.. so we need to delete the file
                if file:
                    os.remove(os.path.join(file_path,'query_file',file[0]))
                # Remove the directory for good measure
                os.rmdir(os.path.join(file_path,'query_file'))
            else:
                pi = self.patient_db.QueryPatientsFromPath(Path=file_path, Filter={})[0]
            self.patient_db.ImportPatientFromPath(Path=file_path, Patient=pi, SeriesFilter={}, ImportFilters=[])
            self.patient_db = get_current("PatientDB") #Got a new patient, update the patient db
            self.patient_id = MRN
            self.patient = get_current("Patient")
            self.case = get_current("Case")
        else:
            print('info found')
            if os.path.exists(os.path.join(file_path,'query_file')):
                file = os.listdir(os.path.join(file_path,'query_file'))
                # But Raystation can't have that.. so we need to delete the file
                if file:
                    os.remove(os.path.join(file_path,'query_file',file[0]))
                # Remove the directory for good measure
                os.rmdir(os.path.join(file_path,'query_file'))
            if self.patient_id != MRN:
                print('patient id does not match MRN')
                if self.patient_id != '0':
                    self.patient.Save()
                print(info)
                try:
                    self.patient = self.patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)
                except:
                    self.patient_id = '0'
                    return None
                self.patient_id = self.patient.PatientID
                for case in self.patient.Cases:
                    self.case = case
                # self.case.SetCurrent()
                self.rois_in_case = []
                for roi in self.case.PatientModel.RegionsOfInterest:
                    self.rois_in_case.append(roi.Name)
                # self.case.SetCurrent()

            self.imported_uids = [e.Series[0].ImportedDicomUID for e in self.case.Examinations]
            self.exams = []
            for exam in self.case.Examinations:
                self.exams.append(exam.Name)
            delete_non_contour_exams = False
            if self.round == 1:
                if uid in self.imported_uids and uid and delete_non_contour_exams:
                    exam_name = self.exams[self.exams.index(uid)]
                    rois_in_exam = 0
                    for roi in self.rois_in_case:
                        if self.case.PatientModel.StructureSets[exam_name].RoiGeometries[roi].HasContours():
                            rois_in_exam += 1
                            break
                    if rois_in_exam == 0:
                        self.case.DeleteExamination(ExaminationName=exam_name)
                        self.patient.Save()
                        self.imported_uids = [e.Series[0].ImportedDicomUID for e in self.case.Examinations]
                if uid not in self.imported_uids and uid: #
                    try:
                        self.patient.ImportDicomDataFromPath(Path=file_path, CaseName=self.case.CaseName, SeriesFilter={},
                                                             ImportFilters=[])
                    except:
                        try:
                            self.patient.ImportDataFromPath(Path=file_path, CaseName=self.case.CaseName,
                                                                 SeriesFilter={},
                                                                 ImportFilters=[],AllowMismatchingPatientID=True)
                        except:
                            print('some kind of error')
                else:
                    print('already imported')
                    self.output[MRN].append(self.exams[self.imported_uids.index(uid)])
                fid = open(os.path.join(file_path,'imported.txt'), 'w+')
                fid.close()
            elif self.round == 2:
                try:
                    self.patient.ImportDicomDataFromPath(Path=file_path, CaseName=self.case.CaseName, SeriesFilter={},
                                                         ImportFilters=[])
                except:
                    self.patient.ImportDataFromPath(Path=file_path, CaseName=self.case.CaseName, AllowMismatchingPatientID=True)
                self.patient.Save()
                fid = open(os.path.join(file_path,'imported.txt'),'w+')
                fid.close()
        os.remove(os.path.join(file_path,'running.txt'))
        return None
def main():
    xxx = 1
if __name__ == "__main__":
    dialog = OpenFileDialog()
    dialog.Filter = "All Files|*.*"
    CT_Path_File = []
    RT_Path_File = []
    result = dialog.ShowDialog()
    Path_File = ''
    if result == DialogResult.OK:
        Path_File = dialog.FileName
    import_class = import_dicom_class()
    try:
        import numpy as np
    except:
        print('Running in 8')
        import_class = import_dicom_class_8B()
    if Path_File:
        fid = open(Path_File)
        CT_file_paths = fid.readline()
        RT_file_paths = fid.readline()
        fid.close()
        CT_file_paths = CT_file_paths.split(',')[:-1]
        RT_file_paths = RT_file_paths.split(',')[:-1]
        print('running')
        error_log = []
        import_class.round = 1
        for i in range(len(CT_file_paths)):
            path = CT_file_paths[i]
            path_CT = path
#             path_CT = os.path.join('\\\\Client\\', path[0] + '$')
#             path_temp = path[2:].split('/')
#             if len(path_temp) == 1:
#                 path_temp = path[2:].split('\\')
#             path = path_temp
#             for section in path[1:]:
#                 path_CT = os.path.join(path_CT,section)
            print(path_CT)
            try:
                import_class.import_dicoms_new(path_CT)
            except:
                continue
        import_class.round = 2
        for i in range(len(RT_file_paths)):
            path = RT_file_paths[i]
            path_RT = path
#             path_RT = os.path.join('\\\\Client\\', path[0] + '$')
#             path_temp = path[2:].split('/')
#             if len(path_temp) == 1:
#                 path_temp = path[2:].split('\\')
#             path = path_temp
#             for section in path[1:]:
#                 path_RT = os.path.join(path_RT,section)
            # path_RT = 'r' + path
            try:
                import_class.import_dicoms_new(path_RT)
                time.sleep(1)
            except:
                error_log.append(path_RT)
        fid = open(Path_File.replace('RayStation_Paths','Upload_Error_Log'),'w+')
        for log in error_log:
            fid.write(log + '\n')
        fid.close()
