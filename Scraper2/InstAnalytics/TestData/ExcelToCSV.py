import xlrd
import csv

#----------------------------------------------------------------------
def open_file(path):
    """
    Open and read an Excel file
    """
    book = xlrd.open_workbook(path)
    path = path[:-5]
    with open(f'{path}.csv', 'w') as f:
        first_sheet = book.sheet_by_index(0)
        numRows = first_sheet.nrows

        # read a cell

        for i in range(2, numRows):
            cell = first_sheet.cell(i,0)
            username = cell.value
            username = username[26:]
            f.write( username + '\n') #Give your csv text here.




open_file("grace_ferrara.xlsx")
open_file("kylie_sullivann.xlsx")
open_file("austinCambas.xlsx")
