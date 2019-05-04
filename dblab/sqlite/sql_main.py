import sqlite3  
import sys

########################

#result = {}
#columns_from_instrucor_tmp = []
#colunms_from_student_tmp = []

instructor_sql = sys.argv[1]
student_sql = sys.argv[2]


def check_sql(student_sql):
    # check if the student_sql includes such like "insert", "update", "delete", "drop", "alter" that can modify the database itself
    tokens = student_sql.lower().split(' ')
    if "insert" in tokens or "update" in tokens or "delete" in tokens or "drop" in tokens or "alter" in tokens:
        print("SHOULD NOT USE insert, update, delete, drop, alter")
        exit(-1)


def analyze_sql_to_get_columns(sql):
    columns = []

    splited_by_from = sql.lower().split('from')[0]
    splited_by_select = splited_by_from.split('select')[1]
    splited_by_comma = splited_by_select.split(',')
    for col in splited_by_comma:
        columns.append(col.strip())
    #print(columns)
    return columns

def analyze_sql_to_get_table_name(sql):
    splited_by_from = sql.lower().split('from')[-1]
    splited_by_space = splited_by_from.strip().split(' ')


def get_all_column_names_from_table(table):
    SQL = "PRAGMA table_info(%s)"
    sql_data = table

    cur.execute(SQL, sql_data)
    res = cur.fetchall()

    return res


def make_dict(query_result, columns):
    result = {}

    for j in range(len(query_result[0])):
        col_data = []
        for i in range(len(query_result)):
            col_data.append(query_result[i][j])
        result[j] = col_data
    print("len: ", len(query_result))
    print(query_result)
    return result


def instrucor(instructor_sql):
    result_instructor = {}
    
    i = 0
    cur.execute(instructor_sql)
    query_result = cur.fetchall()

    columns_from_instrucor = analyze_sql_to_get_columns(instructor_sql)
    result_instructor = make_dict(query_result, columns_from_instrucor)

    conn.commit()

    return result_instructor


def student(student_sql):
    result_student = {}

    i = 0
    try:
        cur.execute(student_sql)
    except sqlite3.Error:
        return {'sqlite_error':'occurs'}
    query_result = cur.fetchall()

    colunms_from_student = analyze_sql_to_get_columns(student_sql)
    result_student = make_dict(query_result, colunms_from_student)
  
    conn.commit()

    return result_student


def compare_results(instructor_sql, student_sql, result_instructor, result_student):

    # first, check if the number of attributes is same
    if len(analyze_sql_to_get_columns(instructor_sql)) != len(analyze_sql_to_get_columns(student_sql)):
        # but, if the sql requires all attributes from the table
        if '*' in result_instructor.keys():
            pass
        elif '*' in result_student.keys():
            pass
        return False

    # second, if it's same, compare the values
    for key in result_instructor.keys():
        try:
            if result_instructor[key] != result_student[key]:
                return False
        except KeyError:
            return False
    for key in result_student.keys():
        try:
            if result_instructor[key] != result_student[key]:
                return False
        except KeyError:
            return False

    return True
    


def start(instructor_sql, student_sql):
    check_sql(student_sql)

    result_instructor = instrucor(instructor_sql)
    result_student = student(student_sql)

    conn.close()

    if result_student.has_key('sqlite_error'):
        # error occurs
        print("error")
        return 2

    if compare_results(instructor_sql, student_sql, result_instructor, result_student) is True:
        # success
        print("success")
        return 0
    else:
         # diff answer
        print("wrong answer")
        return 1


conn = sqlite3.connect('new.db')
cur = conn.cursor()

start(instructor_sql, student_sql)