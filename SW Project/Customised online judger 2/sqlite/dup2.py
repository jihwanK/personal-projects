import sqlite3
import sys
import time


#################################################################################################################################
# check if the student_sql includes such like "insert", "update", "delete", "drop", "alter" that can modify the database itself #
#################################################################################################################################

def check_sql(student_sql):
    tokens = student_sql.lower().split(' ')
    if "insert" in tokens or "update" in tokens or "delete" in tokens or "drop" in tokens or "alter" in tokens:
        print("SHOULD NOT USE insert, update, delete, drop, alter")
        exit(-1)
    try:
        start = time.time()
        cur.execute(student_sql)
        conn.commit()
        print('execution time in check_sql: ' + str(time.time()-start))
    except sqlite3.Error:
        return -1


##############################################
# get the name of columns from the given sql #
##############################################

def analyze_sql_to_get_columns(sql):
    columns = []

    splited_by_from = sql.lower().split('from')[0]
    splited_by_select = splited_by_from.split('select')[1]
    splited_by_comma = splited_by_select.split(',')

    suffix = 1
    for col in splited_by_comma:
        if 'as' in col.lower():
            splited_by_as = col.lower().split('as')[1].strip()
            if splited_by_as in columns:
                splited_by_as = splited_by_as+str(suffix)
                suffix = suffix+1
            columns.append(splited_by_as)
        else:
            ele = col.lower().strip()
            if ele in columns:
                ele = ele+str(suffix)
                suffix = suffix+1
            columns.append(ele)

    return columns


#########################
# get dictionary result #
#########################

def make_dict(query_result, columns):
    result = {}

    for j in range(len(query_result[0])):
        col_data = []
        for i in range(len(query_result)):
            col_data.append(query_result[i][j])

        if columns[0] == '*':
            result[j] = col_data
        else:
            result[columns[j]] = col_data

    return result


#########################
# get the answer result #
#########################

def get_result(sql, columns):
    result = {}
    
    # try:
    #     cur.execute(sql)
    # except sqlite3.Error:
    #     return {'sqlite_error':'occurs'}

    start = time.time()
    cur.execute(sql)
    conn.commit()
    query_result = cur.fetchall()
    print('execution time in get_result: ' + str(time.time()-start))

    #columns = analyze_sql_to_get_columns(sql)
    result = make_dict(query_result, columns)

    #conn.commit()

    return result


########################################################################
# compare the results from one from instructor, the other from student #
########################################################################

def compare_results(result_instructor, result_student):

    # first, check if the number of attributes is same
    if len(result_instructor.keys()) != len(result_student.keys()):
        print('the number of columns is different')
        return False

    if len(result_instructor.values()[0]) != len(result_student.values()[0]):
        print('the number of values is different')
        return False

    # second, if it's same, compare the values
    for key_instructor in result_instructor.keys():
        before = len(result_instructor.keys())
        for key_student in result_student.keys():
            if result_instructor[key_instructor] == result_student[key_student]:
                result_instructor.pop(key_instructor)
                result_student.pop(key_student)
                break
        after = len(result_student.keys())
        if before == after:
            return False

    return True





###############################################################
###############################################################
###############################################################








def get_columns(instructor_sql):
    start = time.time()
    cur.execute(instructor_sql.strip())
    columns = [des[0] for des in cur.description]
    conn.commit()
    print('execution time in get_columns: ' + str(time.time()-start))

    return columns






def compare_using_sql(instructor_sql, student_sql, columns):
    column_list = ''
    for ele in columns:
        if ele == columns[0]:
            column_list = ele
        else:
            column_list = column_list + ',' + ele

    num_of_col = len(columns)

    sql = '''SELECT * FROM ({instructor}) AS qwe
        WHERE NOT EXISTS (
            SELECT {columns} FROM ({student}) AS asd
            WHERE
                CASE
                    WHEN qwe.{col} IS NULL AND asd.{col} IS NULL
                    THEN 1
                    WHEN qwe.{col} IS NULL AND asd.{col} IS NOT NULL
                    THEN 0
                    WHEN qwe.{col} IS NOT NULL AND asd.{col} IS NULL
                    THEN 0
                    ELSE qwe.{col} = asd.{col}
                END
    '''.format(instructor=instructor_sql, columns=column_list, student=student_sql, col=columns[0])

            
    for i in range(1, num_of_col):
        if num_of_col != 1:
            append = '''
            AND
                CASE
                    WHEN qwe.{col} IS NULL AND asd.{col} IS NULL
                    THEN 1
                    WHEN qwe.{col} IS NULL AND asd.{col} IS NOT NULL
                    THEN 0
                    WHEN qwe.{col} IS NOT NULL AND asd.{col} IS NULL
                    THEN 0
                    ELSE qwe.{col} = asd.{col}
                END
    '''.format(col=columns[i])  
            sql = sql + append

    sql = sql + ');'

    start = time.time()
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    print('execution time in compare_using_sql: ' + str(time.time()-start))

    if len(res) == 0:
        print ('correct answer')
        return True
    else:
        print('wrong answer')
        return False




###############################################################
###############################################################
###############################################################












#################
# main function #
#################

def start(instructor_sql, student_sql):
    # if instructor_sql == student_sql:
    #     print("correct")
    #     return 0

    if check_sql(student_sql) == -1:
        # error occurs
        print("line 132")
        print("error")
        return 2

    columns_from_instrucor = get_columns(instructor_sql)
    columns_from_student = get_columns(student_sql)

    

    #conn.close()


    if 'ORDER BY' in instructor_sql.upper():
        result_instructor = get_result(instructor_sql, columns_from_instrucor)
        result_student = get_result(student_sql, columns_from_student)

        if result_student.has_key('sqlite_error'):
            # error occurs
            print("line 145")
            print("error")
            return 2

        if compare_results(result_instructor, result_student) is True:
            # correct
            print("correct")
            return 0
        else:
            # wrong answer
            print("wrong answer")
            return 1
    else:        
        #columns = get_columns(instructor_sql)
        compare_using_sql(instructor_sql, student_sql, columns_from_instrucor)



    

    


#####################################
# to check if this module runs well #
#####################################

def check_module():
    with open('input.sql', 'r') as sql:
        lines = sql.readlines()
        for i in range(len(lines)):
            print(str(i+1)+'th:')
            start_time = time.time()
            start(lines[i], lines[i])
            end_time = time.time()
            print('it took ' + str(end_time - start_time) + ' sec')
    sql.close()



# instructor_sql = sys.argv[1]
# student_sql = sys.argv[2]

conn = sqlite3.connect('example.db')
cur = conn.cursor()

if sys.argv[1] == 'check':
    check_module()
else: start(sys.argv[1], sys.argv[2])


#chcek_module()
cur.close()
conn.close()
#start(sys.argv[1], sys.argv[2])

