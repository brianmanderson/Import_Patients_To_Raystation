__author__ = 'Brian Mark Anderson'
from tkinter import *
from tkinter.filedialog import askdirectory
from Prep_dicom_UID import prep_dicom
import Dir_Listing_CT_RT_Files

class Application(Frame):
    def find_folder(self):
        print('Locate the address folder')
        try:
            self.path = askdirectory()
            self.out_path = self.path
            self.Go['state'] = 'normal'
            self.Go['text'] = 'Prep!'
            self.Go['fg'] = 'green'
            self.Go.config(font=('Courier', 15))
            self.Go['width'] = 10

            self.list_button['state'] = 'normal'

            self.path_text['text'] = 'path = ' + self.path

            self.out_path_text['text'] = 'out_path = ' + self.out_path
        except:
            xxx = 1
    def output_folder(self):
        self.out_path = askdirectory()
        self.out_path_text['text'] = 'out_path = ' + self.out_path
        if self.path:
            self.list_button['state'] = 'normal'
    def go_button(self):
        self.Go['state'] = DISABLED
        self.list_button['state'] = DISABLED
        self.Go['text'] = 'Running...'
        self.Go.update_idletasks()
        try:
            min_images = 15
            self.uid_pred.build(overlapping_images=not self.check_box_val_2.get(),overlapping_liver=self.check_box_val.get(), min_size=min_images)
            self.uid_pred.get_input_paths(input_path=self.path)
            self.uid_pred.make_uids()
            Dir_Listing_CT_RT_Files.get_directories(path=self.path, out_path=self.out_path)
            self.Go['text'] = 'Finished!'
        except:
            self.Go['text'] = 'Had an error..sorry'
            self.Go['width'] = 20
            self.Go['fg'] = 'red'
            self.Go.config(font=('Courier', 10))
        self.list_button['state'] = 'normal'
        self.list_button.update_idletasks()
        self.Go.update_idletasks()
    def list_button_fun(self):
        self.list_button['state'] = DISABLED
        self.list_button['text'] = 'Running...'
        self.list_button.update_idletasks()
        try:
            Dir_Listing_CT_RT_Files.get_directories(path=self.path, out_path=self.out_path)
            self.list_button['text'] = 'Finished!'
        except:
            self.list_button['text'] = 'Error =('
        self.list_button['state'] = 'normal'
        self.list_button.update_idletasks()
    def createWidget(self):
        self.out_path = []
        self.path = []
        self.winfo_toplevel().title('Prep dicom for Raystation')
        self.find_folder_button = Button(self)
        self.find_folder_button['text'] = 'Select dicom parent folder'
        self.find_folder_button['width'] = 30
        self.find_folder_button.config(font=('Courier', 15))
        self.find_folder_button['command'] = self.find_folder

        self.check_box = Checkbutton(self)
        self.check_box_val = BooleanVar()
        self.check_box['text'] = 'Multiphase Liver CTs?\nWill change UIDs...'
        self.check_box['variable'] = self.check_box_val
        self.check_box['width'] = 20
        self.check_box.config(font=('Courier', 10))

        self.check_box_2 = Checkbutton(self)
        self.check_box_val_2 = BooleanVar()
        self.check_box_2['text'] = 'All pre-separated?\nUSE WITH CARE'
        self.check_box_2['variable'] = self.check_box_val_2
        self.check_box_2['width'] = 20
        self.check_box_2.config(font=('Courier', 10))

        self.path_text = Label(self)
        self.path_text['text'] = 'path = '
        self.path_text.config(font=('Courier', 10))

        self.Go = Button(self,width=10)
        self.Go['text'] = 'Prep!'
        self.Go['fg'] = 'green'
        self.Go.config(font=('Courier', 15))
        self.Go['width'] = 10
        self.Go['command'] = self.go_button
        self.Go['state'] = DISABLED

        self.output_folder_button = Button(self)
        self.output_folder_button['text'] = 'Pre-prepped?'
        self.output_folder_button['width'] = 30
        self.output_folder_button.config(font=('Courier', 15))
        self.output_folder_button['command'] = self.output_folder

        self.out_path_text = Label(self)
        self.out_path_text['text'] = 'out_path = '
        self.out_path_text.config(font=('Courier', 10))

        self.list_button = Button(self,width=10)
        self.list_button['text'] = 'Make List Files'
        self.list_button['fg'] = 'green'
        self.list_button.config(font=('Courier',10))
        self.list_button['width'] = 15
        self.list_button['command'] = self.list_button_fun
        self.list_button['state'] = DISABLED


        self.disclaimer = Label(self)
        self.disclaimer['text'] = 'If you have any issues with this please reach out to:\n' \
                                  'Brian Anderson, bmanderson@mdanderson.org'
        self.disclaimer.config(font=('Courier',10))

        self.QUIT = Button(self)
        self.QUIT['text'] = 'Quit'
        self.QUIT['fg'] = 'red'
        self.QUIT['command'] = self.quit
        self.QUIT['width'] = 10
        self.QUIT.config(font=('Courier', 10))

        self.find_folder_button.grid(row=0, column=0, columnspan=3)
        self.path_text.grid(row=1, column=0, columnspan=3)
        self.check_box.grid(row=2, column=3)
        self.check_box_2.grid(row=5,column=3)
        self.Go.grid(row=2, column=0, columnspan=3)

        self.output_folder_button.grid(row=3,column=0,columnspan=3)
        self.out_path_text.grid(row=4,column=0,columnspan=3)
        self.list_button.grid(row=5,column=0,columnspan=3)

        self.disclaimer.grid(row=6,column=0,columnspan=3)
        self.QUIT.grid(row=7, column=2)




    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.uid_pred = prep_dicom()
        self.pack()
        self.createWidget()
root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

