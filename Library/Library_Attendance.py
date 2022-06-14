import sqlite3
from datetime import datetime, timedelta
from sqlite3 import Error
from reportlab.pdfgen import canvas


def exportPdf(fileName, connectionObject):
    c = canvas.Canvas(fileName)
    img_file = "DJSCE_Header.png"
    # Header
    x_start = 50
    y_start = 690
    c.drawImage(
        img_file, x_start, y_start, width=500, preserveAspectRatio=True, mask="auto"
    )
    c.setFont('Helvetica-Bold', 14)
    c.drawString(225, 740, "Attendance for {title}".format(title=fileName[8:-4]))
    c.line(20, 730, 575, 730)
    c.setFont('Helvetica', 12)

    databaseResults = connectionObject.fetchall()
    labels = ["id: ", "SAP: ", "   Date: ", "   In: ", "   out: ", "is_in: "]
    y_pos = [x for x in range(700, 0, -30)]
    # print(databaseResults)
    for i, data in enumerate(databaseResults):
        dataStringList = [labels[j] + str(entry) for j, entry in enumerate(data)]
        dataStringList.pop(-1)
        dataStringList.pop(0)
        # print(dataStringList)
        if i % 22 == 0 and i != 0:
            c.showPage()
            c.drawImage(img_file, x_start, y_start, width=500, preserveAspectRatio=True, mask="auto")
            c.setFont('Helvetica-Bold', 14)
            c.drawString(225, 740, "Attendance for {title}".format(title=fileName[8:-4]))
            c.line(20, 730, 575, 730)

            c.setFont('Helvetica', 12)

        c.drawString(100, y_pos[i % 22], " ".join(dataStringList))
    c.save()


# All the queries
update_data = """ UPDATE LIBRARY SET exittime=?, is_in=? WHERE (sapid,is_in)=(?,?);"""
check_entry_data = """ SELECT * FROM LIBRARY WHERE (sapid,in_date,is_in)=(?,?,?); """
insert_data = """ INSERT INTO LIBRARY ( sapid, in_date, entrytime, is_in ) VALUES ( ?,?,?,? );"""

retrieve_all_data = """SELECT * FROM LIBRARY"""


# Create table and establish a connection
def create_table_connection():
    str_date = datetime.now().strftime("%b-%Y")
    # str_date = 'Aug-2019'
    file_name = "library-" + str_date + ".db"
    conn = sqlite3.connect(file_name)
    create_table = """ CREATE TABLE IF NOT EXISTS LIBRARY (
                                        id integer PRIMARY KEY,
                                        sapid text NOT NULL,
                                        in_date text NOT NULL,
                                        entrytime text NOT NULL,
                                        exittime text,
                                        is_in integer
                                    ); """
    try:
        c = conn.cursor()
        c.execute(create_table)
        return conn
    except Error as e:
        print(e)


# Entry of sap id scanned by the machine
def data_entry(conn, sap_id):
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M:%S")
    c = conn.cursor()
    
    # Check if student has entered the library
    c.execute(check_entry_data, (sap_id, date, 1))
    row = c.fetchall()

    # print(row)  # Just for tests

    # update exit time if entered else create entry
    if row:
        c.execute(update_data, (time, 0, sap_id, 1))
    else:
        # print(date + " " + time)
        # query = insert_data.format(sap_id, date, time, 1)
        c.execute(insert_data, (sap_id, date, time, 1))
    conn.commit()


def pdf_generation(str_date, conn):
    file_name = "library-" + str_date + ".pdf"
    print(file_name)
    exportPdf(file_name, conn)


# Main function to start the system
def main():
    c = create_table_connection()
    sap_id = ""

    # A loop for endlessly taking input unless quit upon..
    while sap_id is not "q":
        sap_id = input("Enter the SAP ID:")
        if sap_id != "q" and sap_id != "p" and sap_id != "r" and sap_id!="":
            data_entry(c, sap_id)
            # p = c.execute(retrieve_all_data)
            # print([row for row in p])
        if sap_id is "p":
            str_date = datetime.now().strftime("%b-%Y")
            p = c.execute(retrieve_all_data)
            pdf_generation(str_date, p)
        if sap_id is 'r':
            name = input('Enter database month as (Aug-2019):')
            if name is not 'q':
                file_name = "library-" + name + ".db"
                conn = sqlite3.connect(file_name)
                c = conn.cursor()
                p = c.execute(retrieve_all_data)
                pdf_generation(name, p)


if __name__ == "__main__":
    main()
