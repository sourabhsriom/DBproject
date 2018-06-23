import xlsxwriter


def create_excel(values):
    workbook = xlsxwriter.Workbook('coin_in_by_denom.xlsx')
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0

    worksheet.write(row,col, "Denom")
    worksheet.write(row,col+1, "Coin In")

    row = row + 1
    # Iterate over the data and write it out row by row.
    for item, cost in (values):
        worksheet.write(row, col,     item)
        worksheet.write(row, col + 1, cost)
        row += 1

    # Write a total using a formula.
    worksheet.write(row, 0, 'Total')
    worksheet.write(row, 1, '=SUM(B1:B4)')

    workbook.close()
