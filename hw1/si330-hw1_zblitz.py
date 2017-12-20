import csv

def read_department_file(filename):

    dept_for_program = {}

    with open(filename,'r') as input_file:
        program_dept_reader = csv.DictReader(input_file)
        for response in program_dept_reader:
            major = response['major']
            department = response['department']

            if department == "":
                dept_for_program[major] = 'Unknown'
            else:
                dept_for_program[major] = department

    return dept_for_program


def student_records(filename, major_department_dictionary):
    ANONID_DEPT_GPA = []
    with open(filename) as input_file:
        student_record_reader = csv.DictReader(input_file, fieldnames= None)
        for row in student_record_reader:
            major_1 = row['MAJOR1_DESCR']
            gpa = row['HSGPA']
            id = row['ANONID']

            if major_1 in major_department_dictionary.keys():
                if major_department_dictionary[major_1] == 'Psychology Department':
                    dept = major_department_dictionary[major_1]
                    info_tuple = (id, dept, gpa)
                    ANONID_DEPT_GPA.append(info_tuple)

    return ANONID_DEPT_GPA



def main():
    student_data = {}
    major_department_dictionary = read_department_file("program.dept.csv")
    student_records_tuple_list = student_records('student.record.cut.csv', major_department_dictionary)

    total_gpa = 0
    total_number_of_gpas = 0
    total_number_of_gpas_to_dismiss = 0
    rows = 0
    with open('psych_output_zblitz.csv','w') as output_file:
        psych_output_writer = csv.DictWriter(output_file,fieldnames=['ANONID','DEPT','HSGPA',], extrasaction='ignore', delimiter=',', quotechar='"')
        psych_output_writer.writeheader()

        for info in student_records_tuple_list:
            id = info[0]
            dept = info[1]
            gpa = info[2]
            student_data["ANONID"] = (id)
            student_data["DEPT"] = dept
            student_data["HSGPA"] = gpa
            psych_output_writer.writerow(student_data)

            if gpa == "NA":
                total_number_of_gpas_to_dismiss +=1
            elif gpa == "0":
                total_number_of_gpas_to_dismiss +=1
            else:
                total_gpa += float(gpa)

            total_number_of_gpas +=1
            rows +=1

    # print(total_gpa)
    # print(total_number_of_gpas)
    # print(total_number_of_gpas_to_dismiss)

    students_to_count = total_number_of_gpas - total_number_of_gpas_to_dismiss
    average_gpa = (total_gpa)/(students_to_count)
    final_gpa_average_number = round(average_gpa,2)

    # print(final_gpa_average_number)
    # print(rows)
    # print(students_to_count)


    print("Done! Wrote a total of " + str(rows) + " rows.")
    print("The mean GPA is " + str(final_gpa_average_number) + ", based on " + str(students_to_count) + " students.")



test = main()







