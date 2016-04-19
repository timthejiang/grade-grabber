from flask import Flask, render_template, request, url_for, abort, flash, redirect
from flaskext.mysql import MySQL
from json import dumps 

from cred import Cred

from string import ascii_lowercase, ascii_uppercase


app = Flask(__name__)
app.secret_key = 'i_really_love_cookies'
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = Cred['MYSQL_DATABASE_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = Cred['MYSQL_DATABASE_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = Cred['MYSQL_DATABASE_DB']
app.config['MYSQL_DATABASE_HOST'] = Cred['MYSQL_DATABASE_HOST']

mysql.init_app(app)
db_connection = mysql.connect()

NUMS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

# def query_all():
# 	#__entry__ handles connection into cursor
# 	with db_connection as cursor:
# 		query = """SELECT s.crn, s.raw_term, c.subject, c.course_number, c.title,
# 		g.average_gpa, g.a_plus_count, g.a_count, g.a_minus_count,
# 		g.b_plus_count, g.b_count, g.b_minus_count,
# 		g.c_plus_count, g.c_count, g.c_minus_count,
# 		g.d_plus_count, g.d_count, g.d_minus_count,
# 		g.f_count, s.instructor, s.section
# 		FROM courses AS c
# 		INNER JOIN semesters AS s ON c.c_id = s.c_id
# 		INNER JOIN grade_counts AS g ON s.s_id = g.s_id"""
# 		cursor.execute(query)
# 		results = cursor.fetchall()
# 	return results

# c_id is an optional paramater
# default behavior queries grade aggregates
# for all distinct courses
# when c_id is applied, queries only for one course
# for c_id search, call query_grade_aggs(c_id=#)
def query_grade_aggs(**c_id):
	query = 'SELECT * FROM grade_aggregates;'
	arg = None
	if('c_id' in c_id):
		arg = c_id['c_id']
		query =  query[:len(query)-1] + ' WHERE c_id = %s;'

	with db_connection as cursor:
		if arg == None:
			cursor.execute(query)
		else:
			cursor.execute(query, [arg])
		results = cursor.fetchall()

	return results 

def get_all_s_ids(subject, number):
	query = """SELECT s.s_id FROM semesters AS s 
	INNER JOIN courses AS c ON s.c_id = c.c_id 
	WHERE c.subject = %s AND c.course_number = %s"""
	args = (subject, number)
	with db_connection as cursor:
		cursor.execute(query, args)
		results = cursor.fetchall()
	return results

def get_aggs_from_subj_num(subject, number):
	if subject == "" or number == "":
		return None

	query = """SELECT c_id FROM courses WHERE subject = (%s) AND course_number = (%s)"""
	args = (subject, number)

	with db_connection as cursor:
		cursor.execute(query, args)
		results = cursor.fetchone()
		if results is None:
			return None
		c_id = results[0]
		query = """SELECT * FROM grade_aggregates WHERE c_id = (%s)"""
		cursor.execute(query, [c_id])
		results = cursor.fetchone()

		return results

def get_semesters_from_c_id(c_id):
	query = """SELECT
	s.parsed_term, s.instructor,
	g.average_gpa, g.a_plus_count, g.a_count, g.a_minus_count,
	g.b_plus_count, g.b_count, g.b_minus_count, g.c_plus_count,
	g.c_count, g.c_minus_count, g.d_plus_count, g.d_count, g.d_minus_count,
	g.f_count, g.w_count 
	FROM courses AS c INNER JOIN semesters AS s ON c.c_id = s.c_id
	INNER JOIN grade_counts AS g ON s.s_id = g.s_id
	WHERE s.c_id = (%s) ORDER BY s.raw_term DESC"""

	with db_connection as cursor:
		cursor.execute(query, [c_id])
		results = cursor.fetchall()
	return results


#Deprecated - phase this function out
def query_by_crn_term(crn, term):
	with db_connection as cursor:
		query = 'SELECT * FROM semesters WHERE crn = (%s) AND raw_term = (%s)'
		args = crn, term
		cursor.execute(query, args)
		return cursor.fetchone(),

#Returns all columns except ID for all course records
#Queries by subject and number thanks to handy table constraints
def query_by_subj_num(subj, num):
		query = """SELECT s.crn, s.raw_term, c.subject, c.course_number, c.title,
		g.average_gpa, g.a_plus_count, g.a_count, g.a_minus_count,
		g.b_plus_count, g.b_count, g.b_minus_count,
		g.c_plus_count, g.c_count, g.c_minus_count,
		g.d_plus_count, g.d_count, g.d_minus_count,
		g.f_count, s.instructor, s.section
		FROM courses AS c
		INNER JOIN semesters AS s ON c.c_id = s.c_id
		INNER JOIN grade_counts AS g ON s.s_id = g.s_id
		WHERE c.subject = %s AND c.course_number = %s"""
		with db_connection as cursor:
			#args = subj, str(num)
			cursor.execute(query, [subj, num])
			return cursor.fetchall()

def query_by_s_id(s_id):
	query = """SELECT s.s_id, s.crn, s.raw_term, c.subject, c.course_number, c.title,
		g.average_gpa, g.a_plus_count, g.a_count, g.a_minus_count,
		g.b_plus_count, g.b_count, g.b_minus_count,
		g.c_plus_count, g.c_count, g.c_minus_count,
		g.d_plus_count, g.d_count, g.d_minus_count,
		g.f_count, s.instructor, s.section
		FROM courses AS c
		INNER JOIN semesters AS s ON c.c_id = s.c_id
		INNER JOIN grade_counts AS g ON s.s_id = g.s_id
		WHERE s.s_id = %s"""
	with db_connection as cursor:
		cursor.execute(query, [s_id])
		results = cursor.fetchone()
	return results,


def record_is_duplicate(crn, raw_term, section):
	query = 'SELECT COUNT(*) FROM semesters WHERE crn = (%s) AND raw_term = (%s) AND section = (%s)'
	args = crn, raw_term, section
	with db_connection as cursor:
		cursor.execute(query, args)
		results = cursor.fetchone()
	if results[0] > 0:
		return True
	else:
		return False

#takes SELECT * FROM grade_aggregates output
#returns aggregates counts of letter grades
#grades_viz = [['A+', #], ['A', #]...]
def prep_aggs_row_for_viz(grades_row):
	if grades_row[5] is None:
		#We don't have counts for this class :(
		return None


	grades_viz = [["A+", int(grades_row[5])],
				["A", int(grades_row[6])],
				["A-", int(grades_row[7])],
				["B+", int(grades_row[8])],
				["B", int(grades_row[9])],
				["B-", int(grades_row[10])],
				["C+", int(grades_row[11])],
				["C", int(grades_row[12])],
				["C-", int(grades_row[13])],
				["D+", int(grades_row[14])],
				["D", int(grades_row[15])],
				["D-", int(grades_row[16])],
				["F", int(grades_row[17])],
				["W", int(grades_row[18])]]

	return grades_viz


#Record is a dictionary of values:
#[Subject, Course#, Title, CRN, Term, Average GPA, A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F]
def insert_record(record):
	if record_is_duplicate(record['crn'], record['term'], record['section']):
		flash('Course with identical CRN, term, section already exists in database - try updating the record instead.')
		return None
	#First check if distinct course is in courses table - add if not
	query = 'SELECT COUNT(*) FROM courses WHERE subject = (%s) AND course_number = (%s) AND title = (%s)'
	args = record['subject'], record['number'], record['title']
	with db_connection as cursor:
		cursor.execute(query, args)
		results = cursor.fetchone()
		print results
	#No distinct course yet
	if results[0] == 0:
		course_insert = 'INSERT INTO courses (subject, course_number, title) VALUES ((%s), (%s), (%s))'
		cursor.execute(course_insert, args)
		cursor.execute('SELECT LAST_INSERT_ID() FROM courses')
		c_id = cursor.fetchone()
	cursor.execute('SELECT c_id FROM courses WHERE subject = (%s) AND course_number = (%s) AND title = (%s)', args)
	c_id = cursor.fetchone()
	#Add course details to semesters
	semester_insert = """INSERT INTO semesters (c_id, raw_term, parsed_term, section, instructor, crn) VALUES (%s, %s, %s, %s, %s, %s)"""
	args = c_id, record['term'], 'FA14', record['section'], record['instructor'], record['crn']
	cursor.execute(semester_insert, args)
	#Add grade_counts data
	cursor.execute('SELECT LAST_INSERT_ID() FROM semesters')
	s_id = cursor.fetchone()
	
	if not (record['avg_gpa'] and record['aplus'] and record['a'] and record['aminus'] and record['bplus'] and record['b'] and record['bminus'] and record['cplus'] and record['c'] and record['cminus'] and record['dplus'] and record['d'] and record['dminus'] and record['f']):
		values = (s_id, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
		grade_insert = 'INSERT INTO grade_counts (s_id, average_gpa, a_plus_count, a_count, a_minus_count, b_plus_count, b_count, b_minus_count, c_plus_count, c_count, c_minus_count, d_plus_count, d_count, d_minus_count, f_count, w_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
	else:
		values = (s_id, record['avg_gpa'], record['aplus'], record['a'], record['aminus'], record['bplus'], record['b'], record['bminus'], record['cplus'], record['c'], record['cminus'], record['dplus'], record['d'], record['dminus'], record['f'], record['w'])
		grade_insert = 'INSERT INTO grade_counts VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
	# subject = record['subject'].upper()
	# section = record['section'].upper()

	with db_connection as cursor:
		cursor.execute(grade_insert, values)
		db_connection.commit()
		flash('Insertion successful')
	return 1, s_id


def delete_by_crn_term(crn, term):
	row = query_by_crn_term(crn, term)[0]
	if not row:
		return None
	else:
		with db_connection as cursor:
			deletion = 'DELETE FROM semesters WHERE s_id = %s;'
			grade_deletion = 'DELETE FROM grade_counts WHERE s_id = %s'
			args = (row[1],)
			cursor.execute(deletion, args)
			cursor.execute(grade_deletion, args)
			db_connection.commit
			return row
		return None

# Used for autocomplete
# Returns a list of ["subjNum: title"] for course candidates
def query_candidate_courses(subj, num):
	subj = subj
	num = num
	query = """SELECT DISTINCT c_id, subject, course_number, title FROM courses 
	WHERE subject = %s AND course_number = %s"""
	args = (subj, num)

	with db_connection as cursor:
		cursor.execute(query, args)
		results = cursor.fetchall()
	print results
	return results 



# Returns a list of matches for term
# of the format "SubjNum: Title"
# @app.route("/autocomplete/<term>")
# def autocomplete(term):
# 	subj = ""
# 	num = ""
# 	for char in term:
# 		if char in ascii_lowercase or char in ascii_uppercase:
# 			subj += char
# 		elif char is ' ':
# 			continue
# 		elif char in NUMS:
# 			num += char

# 	results = query_possible_courses(subj, num)
# 	return dumps(results)

# Returns True if multiple courses are listed under 
# a subject number pair in courses 
def has_multiple_courses(subj, num):
	with db_connection as cursor:
		query = 'SELECT COUNT(*) FROM courses WHERE subject = %s AND course_number = %s'
		args = (subj, num)
		cursor.execute(query, args)
		count = cursor.fetchone()
		count = count[0]
	if count > 1:
		return True
	else:
		return False 


@app.route("/", methods=['GET', 'POST'])
def front():
	# print query_grade_aggs()
	if request.method == 'GET':
		return render_template('index.html')
	
	elif request.method == 'POST':
		# print request.form['subj_num']
		query = request.form['subj_num']

		if len(query) < 1:
			flash("We can't read your mind! Enter a course subject and number, like CS411.", 'message')
			return render_template('index.html')

		subj = ""
		num = ""



		for char in query:
			if char is ' ':
				continue
			elif char in NUMS:
				num += char
			elif char not in ascii_lowercase and char not in ascii_uppercase and char != ' ':
				flash("Invalid input included in search: " + char, "message")
				return render_template('index.html')
			else:
				subj += char

		# print num + " " + subj

		# print results
		# print barData

		multipleCourses = has_multiple_courses(subj, num)
		if multipleCourses:
			# Return all courses on confirmation template
			choices = query_candidate_courses(subj, num)
			print choices
			return render_template("confirm_course.html", choices=choices)
		else:
			results = get_aggs_from_subj_num(subj, num)

			if results is None:
				flash('Course does not exist!', 'alert')
				return render_template('index.html')
			else:
				barData = prep_aggs_row_for_viz(results)
				className = results[1] + str(results[2]) + ": " + results[3]
				tableResults = results[4:]
				overall_grades = query_grade_aggs(c_id=results[0])[0]
				print overall_grades
				semDetails = get_semesters_from_c_id(results[0])

				return render_template('query.html', shortName = (subj + str(num)), className = className, results=tableResults, semDetails = semDetails, barData = barData, overall_grades=overall_grades)


		

	#return render_template('index.html')

# @app.route("/update", methods=['GET', 'POST'])
# def update():
# 	return 'Success'

@app.route("/query/<c_id>")
def show_selected_course(c_id):
	results = query_grade_aggs(c_id=c_id)
	results = results[0]
	if results is None:
		flash('Course does not exist!', 'alert')
		return render_template('index.html')
	else:
		barData = prep_aggs_row_for_viz(results)
		className = results[1] + str(results[2]) + ": " + results[3]
		tableResults = results[4:]
		overall_grades = query_grade_aggs(c_id=results[0])[0]
		print overall_grades
		semDetails = get_semesters_from_c_id(results[0])

		return render_template('query.html', shortName = (results[1] + str(results[2])), className = className, results=tableResults, semDetails = semDetails, barData = barData, overall_grades=overall_grades)

@app.route('/surprise')
def show_random_course():
	with db_connection as cursor:
		cursor.execute('SELECT c_id FROM courses ORDER BY RAND() LIMIT 1')
		c_id = cursor.fetchone()[0]
	return show_selected_course(c_id)

@app.route("/modify", methods=['GET', 'POST'])
def modify():
	#status = insert_record(['CS', '411', 'Database Systems', '11111', '120313', '3.5', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Tyler Davis', 2112])
	if request.method == 'POST':
		#query = 'SELECT * FROM course '

		#Searching for a course
		if 'search' in request.form:
			subject = request.form['subject']
			number = request.form['number']
			results = query_by_subj_num(subject, number)
			return render_template('query.html', results=results)

		#Updating a record
		elif 'update_query' in request.form:
			subject = request.form['subject']
			number = request.form['number']
			#print crn
			s_ids = get_all_s_ids(subject, number)
			results = ()
			#with db_connection as cursor:
			for s_id in s_ids:
				row = query_by_s_id(s_id)
				#row = s_id + row
				results += row

			# results = []
			# for s_id, each in zip(tupleList, s_ids):
			# 	results.append([s_id])
			# 	index = results.index()
			# 	for attribute in each:


				# query = 'SELECT * FROM courses WHERE subject = (%s) AND course_number = (%s);'
				# args = subject, number
				# cursor.execute(query, args)
				# result = cursor.fetchone()
			#Reorder columns
			# result = result,
			# print result
			# result = result[0]
			#return redirect(url_for('update'))
			return render_template('update.html', s_ids = s_ids, result=results)

		elif 'update_conf' in request.form:
			return 'Success'

		#Inserting a record
		elif 'insert' in request.form:
			#minimal form validation
			if request.form['subject'] and request.form['number'] and request.form['title'] and request.form['crn'] and request.form['term'] and request.form['section'] and request.form['instructor']:
				status = insert_record(request.form)
				if status == None:
					return render_template('modify.html')
				else:
					return render_template('query.html', results=query_by_s_id(status[1]))
			else:
				flash('Insertion requires the following fields at minimum: subject, course number, title, CRN and section.')
			return render_template('modify.html')

		elif 'delete' in request.form:
			row = delete_by_crn_term(request.form['crn'], request.form['term'])
			if row:
				flash('Successfully deleted:\n (%s)' % str(row))
			else:
				flash('Grade report does not exist, nothing deleted.')
			return render_template('modify.html')

	else:
		return render_template('modify.html')


if __name__ == "__main__":
	app.run(debug=True)
