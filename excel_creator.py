import xlsxwriter


def create_excel(values):
    workbook = xlsxwriter.Workbook('coin_in_by_denom.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})

    #print (values)

    row = 0
    col = 0
    cell_format = workbook.add_format()
    cell_format.set_bold()

    worksheet.write(row,col, "Denom",cell_format)
    worksheet.write(row,col+1, "Coin In",cell_format)

    row = row + 1
    # Iterate over the data and write it out row by row.
    total = 0
    for denom, coinIn in (values):
        total = total + coinIn
        worksheet.write(row, col,     denom)
        worksheet.write(row, col + 1, coinIn)
        row += 1


    worksheet.write(10,0, "Day's Total",cell_format)
    worksheet.write(10,1, '${:,.2f}'.format(total),cell_format)

    #######################################################################
#
# Create a new column chart.
#
    chart1 = workbook.add_chart({'type': 'column'})

# Configure the first series.
    chart1.add_series({
        'name':       '=Sheet1!$B$1',
        'categories': '=Sheet1!$A$2:$A$7',
        'values':     '=Sheet1!$B$2:$B$7',
        'data_labels': {'value': True},
    #'values':  '=Sheet1!$B$2:INDEX($A:$A,ROWS($A:$A))',
    })

    chart1.set_title ({'name': 'Coin in by denom'})
    chart1.set_x_axis({'name': 'Denom'})
    chart1.set_y_axis({'name': 'Coin in'})

    chart1.set_style(11)
    worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})


    workbook.close()
