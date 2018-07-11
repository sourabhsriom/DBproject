import xlsxwriter

workbook = xlsxwriter.Workbook('chart_bar.xlsx')
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold': 1})

# Add the worksheet data that the charts will refer to.
headings = ['Denom', 'Coin In']
data = [
    [2, 3, 4, 5, 6, 7],
    [10, 40, 50, 20, 10, 50],

]

worksheet.write_row('A1', headings, bold)
worksheet.write_column('A2', data[0])
worksheet.write_column('B2', data[1])


#######################################################################
#
# Create a new bar chart.
#
chart1 = workbook.add_chart({'type': 'column'})

# Configure the first series.
chart1.add_series({
    'name':       '=Sheet1!$B$1',
    'categories': '=Sheet1!$A$2:INDEX($A:$A,ROWS($A:$A))',
    'values':     '=Sheet1!$B$2:$B$7',
    #'values':  '=Sheet1!$B$2:INDEX($A:$A,ROWS($A:$A))',
})

# Add a chart title and some axis labels.
chart1.set_title ({'name': 'Coin in by denom'})
chart1.set_x_axis({'name': 'Denom'})
chart1.set_y_axis({'name': 'Coin in'})

# Set an Excel chart style.
chart1.set_style(11)

# Insert the chart into the worksheet (with an offset).
worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})


workbook.close()
