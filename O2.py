# -*- coding: utf-8 -*-
"""
O2: Olin Organizer
SoftwareDesign Project 2015 Spring

Created on Mon Apr  6 15:53:28 2015

@author: Junhyun Nam, Jee Hyun Kim, Zi Liang Ong

@note:
    Code-style:
        - for function and class.
        - Underscore for variable.
        - Prefix 'g_' for global viarlable.
"""



############################################################################
# Imports
############################################################################

import csv



############################################################################
# Global variables
############################################################################





# def import_csv_file(filename):
# 	courselist = []
# 	with open(filename) as csvfile:
# 		reader = csv.reader(csvfile)
# 		for row in reader:
# 			print row
# 		csvfile.seek(0)
# 	return courselist

def extract_alphabet(input_string):
	return filter(lambda c: c.isalpha(), input_string)


# print import_csv_file('courselist.csv')


############################################################################
# Model Classes
############################################################################


class Course():
	""" A class that contains all the information about courses """
	def __init__(self, course_code, name, faculty, schedule_str, credit, half = False):
		self.course_code = course_code
		self.name = name
		self.faculty = faculty
		self.schedulestr = schedule_str  #store schedule temporarily as a string
		self.credit = credit
		self.schedules = []  #store schedule as a list of Schedule object
		self.half = half

		#determine credit type
		self.credit_type = extract_alphabet(self.course_code[:4])
			

	def get_course_code(self):
		return self.course_code

	def get_name(self):
		return self.name

	def get_faculty(self):
		return self.faculty

	def get_credit(self):
		return self.credit

	def get_schedules(self):
		""" return a list of schedules """
		return self.schedules

	def add_schedule(self, schedule):
		self.schedules.append(schedule)





class Schedule():
	""" A class that contains the information about schedule """
	def __init__(self, day, start_time, end_time, place):
		self.day = day
		self.start_time = start_time
		self.end_time = end_time
		self.place = place

	def get_day(self):
		return self.day

	def get_start_time(self):
		return self.start_time

	def get_end_time(self):
		return self.end_time

	def get_place(self):
		return self.place


class CourseList():
	""" A class that contains all the courses as a list """
	def __init__(self):
		self.courselist = []

	# def add_course(self, course):
	# 	self.courselist.append(course)

	def import_csv_file(self, filename):
		courselist = []
		with open(filename) as csvfile:
			reader = csv.reader(csvfile)
			next(reader)
			for row in reader:
				"""
				row[0]: Course Code
				row[1]: Course name
				row[2]: Faculty member
				row[3]: Seats open
				row[4]: status
				row[5]: Schedule
				row[6]: Credits
				row[7]: Begin date
				row[8]: End date
				"""
				courselist.append(Course(row[0], row[1], row[2], row[4], row[5], row[8] == '10/16/2015'))
			# csvfile.seek(0)
		return courselist




class Timetable():
	""" A class that contains the information about your timetable """
	def __init__(self):
		self.courses = []

	def add_course(self, course):
		self.courses.append(course)

	def remove_course(self, course_code):
		for course in self.courses:
			if course.get_course_code() == course_code:
				self.courses.remove(course)
			break


courselist = CourseList()
courselist.import_csv_file('courselist.csv')



