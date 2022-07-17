from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteCombobox
import csv


def probe_trunct(seq, memo={}):
    complements = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', '*': '*', 'N': 'N'}
    if seq not in memo:
        memo[seq] = ''.join([complements[nt] for nt in reversed(seq)])
    probe_seq = memo[seq]
    probe_seq = probe_seq[:15]
    return probe_seq

def callback():
    if barcode_sel.get() == '' and marker_sel.get() == '':
        messagebox.showerror(title='Missing values', message='No barcode ID and marker selected.')
    elif marker_sel.get() == '':
        messagebox.showerror(title='Missing values', message='No marker selected.')
    elif barcode_sel.get() == '':
        messagebox.showerror(title='Missing values', message='No barcode ID selected.')
    else:
        probe_id = marker_prefix[marker_list.index(marker_sel.get())] + barcode_sel.get()
        probe_seq = marker_seq[marker_list.index(marker_sel.get())] + 'TTTTT' \
                    + probe_trunct(barcode_seq[barcode_id.index(barcode_sel.get())])
        idt_output = probe_id + '\t' + probe_seq + '\t' + '250nm' + '\n'
        output.insert('1.0', idt_output)

# Import CSV list
barcode_id = []
barcode_seq = []
barcode_list = []
with open(r'barcodes_list_v2.csv') as f:
    s = csv.DictReader(f, delimiter='\t')
    [(barcode_id.append(row['Barcode']),
      barcode_seq.append(row['Sequence']),
      barcode_list.append((row['Barcode'], row['Sequence'])))
     for row in s]

# Create object
window = Tk()

# Add window title
window.title('TRACER barcode selection')

# GUI label
# ttk.Label(window, text='TRACER barcode selection',font=('Arial', 20)).grid(row=0, column=1)

# Define GUI geometry
window.geometry('470x400')

# Create barcode label
ttk.Label(window, text='Select barcode ID').grid(row=15, column=0, padx=20, pady=10)

# Create barcode combobox menu
n = StringVar()
barcode_sel = ttk.Combobox(window, width=30, textvariable=n)
barcode_sel['values'] = barcode_id
barcode_sel.grid(row=15, column=1)

# Create marker label
ttk.Label(window, text='Select marker').grid(row=20, column=0, padx=20, pady=10)

# Marker list
marker_list = ('Fluorescein (FAM)',
               'Tetramethylrhodamine (TAMRA)',
               'Alexa Fluor 647 (AF647)',
               'TYE 705 (TYE705)',
               'TAMRA + TYE655 (TA+TY655)',
               'TAMRA + TYE705 (TA+TY705)')

marker_prefix = ('fl_',
                 'ta_',
                 'af_',
                 'ty_',
                 't6_',
                 'ty_')

marker_seq = ('AGACGAGGCCCTAGA',
              'GCATTGCGTTCAACT',
              'TATATGAGCTAGCCG',
              'CATGCATCCAACGCG',
              'TATATGAGCTAGCCG',
              'CATGCATCCAACGCG')

# Create marker combobox menu
marker_sel = AutocompleteCombobox(window, width=30, completevalues=marker_list)
marker_sel.grid(row=20, column=1)

# Create button
ttk.Button(window, text='Add to list', command=callback).grid(row=30, column=0, padx=20, pady=10)

# Create textframe output
output = Text(window)
output.place(x=10, y=150, height=200, width=440)

# Create GUI
window.mainloop()
