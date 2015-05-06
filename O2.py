# -*- coding: utf-8 -*-
"""
O2: Olin Organizer
SoftwareDesign Project 2015 Spring

Created on Mon Apr  6 15:53:28 2015

@author: Junhyun Nam, Jee Hyun Kim, Zi Liang Ong

"""



############################################################################
# Imports
############################################################################

import csv
import re
import random

import Tkinter as tk
import ttk

import datetime as dt
import icalendar as ical
import pytz

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

############################################################################
# Global variables
############################################################################


############################################################################
# Model Classes
############################################################################


class Course:
	""" A class that contains all the information about courses """
	def __init__(self, course_code, name, faculty, credit, half = False):
		self.course_code = course_code
		self.name = name
		self.faculty = faculty
		self.credit = credit
		self.schedules = []  #store schedule as a list of Schedule object
		self.half = half

		#determine credit type
		self.credit_type = self.extract_alphabet(self.course_code[:4])
		# self.sort_schedule()
		

	def get_course_code(self):
		""" Returns the course code """
		return self.course_code

	def get_name(self):
		""" Returns the course name """
		return self.name

	def get_faculty(self):
		""" Returns the professor """
		return self.faculty

	def get_credit(self):
		""" Returns the credit """
		return self.credit

	def get_credit_type(self):
		""" Returns the credit type """
		return self.credit_type

	def get_schedules(self):
		""" Returns the list of schedules """
		return self.schedules

	def add_schedule(self, schedule):
		""" Add Schedule object to the list of schedules """
		self.schedules.append(schedule)

	def remove_schedule(self, schedule):
		""" Remove given Schedule object from the list of schedules """
		self.schedules.remove(schedule)

	def compare_schedule(self, schedule1, schedule2):
		""" Compares two schedule and returns True or False 
			depending on if they have same schedule
		"""
		if schedule1.get_day() == schedule2.get_day() and \
		schedule1.get_start_time() == schedule2.get_start_time() and \
		schedule1.get_end_time() == schedule2.get_end_time():
			return True
		return False

	def sort_schedule(self):
		""" Goes through the schedules in a course and 
			combines the same schedules with different venue 
			into a single schedule with venue as list
		"""
		for i, schedule in enumerate(self.schedules):
			if i == len(self.schedules)-1:
				continue
			else:
				for j in range(len(self.schedules)-i):
					if j == 0:
						continue
					elif self.compare_schedule(schedule,self.schedules[i+j]):
						schedule.add_venue(self.schedules[i+j].venue)
						self.schedules.remove(self.schedules[i+j])
					else:
						break

	def get_time_str(self):
		""" Get time information of course as a string
			by accessing its schedule
		"""
		time = ''
		if self.get_schedules() != None:
			for schedule in self.get_schedules():
				time_str = schedule.get_day() + ' : ' + schedule.get_start_time() + ' - ' + schedule.get_end_time()
				if time != '':
					time += '\n'
				time += time_str
			return time

	def get_venue_str(self):
		""" Get venu information of course as a string
			by accessing its schedule
		"""
		venues = ''
		if self.get_schedules() != None:
			for schedule in self.get_schedules():
				for venue in schedule.get_venue():
					if venues != '':
						venues += '\n'
					venues +=venue
			return venues

	def extract_alphabet(self, input_string):
		""" Extract alphabet from string
			Used for get the credit type from the course code
		"""
		return filter(lambda c: c.isalpha(), input_string)

class Schedule:
	""" A class that contains the information about schedule 
		This object would be created for each class in the course
	"""
	def __init__(self, day, start_time, end_time, venue):
		self.day = day
		self.start_time = start_time
		self.end_time = end_time
		self.venue = venue #list

	def get_day(self):
		""" Returns the day """
		return self.day

	def get_start_time(self):
		""" Returns the start time """
		return self.start_time

	def get_end_time(self):
		""" Returns the end time """
		return self.end_time

	def get_venue(self):
		""" Returns the venue """
		return self.venue

	def add_venue(self, venue):
		""" Adds venue 
			use only for sort schedule in course
		"""
		self.venue.append(venue[0])


class CourseList:
	""" A class that contains all the courses as a list """
	def __init__(self):
		self.full_list = []

		self.import_csv_file('data/fall15.csv')
		self.result_list = self.full_list


	def time_converter(self,time,label):
		""" time: '10:50'	
			label: 'AM' or 'PM'

			takes in time and label and returns time in 24 hour format in string

			print time_converter(10:50,PM)
			>>> 2250
		"""
		
		if label == "AM":
			[hour,minute] = time.split(':')
			return hour+minute
		elif label == "PM":
			[hour,minute] = time.split(':')
			if hour == '12':
				pass
			else:
				hour = str(int(hour)+12)
			return hour+minute
	

	def import_csv_file(self, filename):
		""" Import csv file and creates Course object with respective
			course code, name, faculty, credits, Schedule object
		"""
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
				course = Course(row[0], row[1], row[2], row[6], row[8] == '10/16/2015')

				split_row = row[5].replace('\n',';').split(';') # ['0:00 - 0:00 AM', ' MAIN Campus, Olin Campus']
				# print split_row
				for i, string in enumerate(split_row):
					if i%2 == 0: #day, time
						split_string = string.split(' ') #['R', '6:45', '-', '9:00', 'PM']
						#making day into a list with each day as an element
						if split_string[0] == '0:00' or split_string[0] == 'No': #There will be some courses with no schedule
							continue
						else:
							day = list(split_string[0]) #['M'] or ['T', 'F']
							if re.search('[a-zA-Z]+',split_string[1]):
								start_time = self.time_converter(split_string[1][:-2],split_string[1][-2:])
							else:
								start_time = self.time_converter(split_string[1],split_string[4])
						end_time = self.time_converter(split_string[3],split_string[4])
						
					elif i%2 == 1: #Venue
						venue = string.split(',')[-1].split('-')[0].replace(' ','')
						for each_day in day:
							course.add_schedule(Schedule(each_day, start_time, end_time, [venue]))

				self.full_list.append(course)
		

	def initialize_result_list(self):
		""" Set result_list as full list of courses at the first time """
		# result_list: course list of course matching search conditions
		self.result_list = self.full_list


	def search_by_credit_type(self, credit_type):
		""" Filter courses in result_list by credit type """
		if not credit_type == 'ALL':
			search_result = []
			for course in self.result_list:
				if course.get_credit_type() == credit_type:
					search_result.append(course)
			self.result_list = search_result


	def search_by_keyword(self, keyword):
		""" Filter courses in result_list by keyword """
		search_result = []
		for course in self.result_list:
			if keyword in course.get_course_code().lower():
				search_result.append(course)
			elif keyword in course.get_name().lower():
				search_result.append(course)
			elif keyword in course.get_faculty().lower():
				search_result.append(course)
		self.result_list = search_result


	def get_result_list(self):
		""" Returns result list """
		return self.result_list


		
############################################################################
# Tkinter Classes
############################################################################

class App(tk.Frame):
	""" The top window that contains all the frames """
	def __init__(self, parent = None):
		parent.title("Olin Organizer")
		parent.geometry("1150x800")
		tk.Frame.__init__(self, parent, bg = 'White')
		self.pack()

###################################################
# classes for choose option and search

class SearchFrame(tk.Frame):
	""" One of the main frames that contains the widgets related to search courses """
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, class_ = 'SearchFrame', bg = 'White')
		self.grid(row = 0, column = 0, rowspan = 2)
		self.option_keyword = SearchKeyword(self, 'Keyword')
		self.option_credit_type = SearchOption(self, 'Credit Type', ['AHSE', 'AWAY', 'ENGR', 'MTH', 'OIE', 'OIP', 'SCI'])
		self.search_button = SearchButton(self)


	# methods related to draw

	def draw(self):
		""" Draws all the contained widgets """
		tk.Label(self, text = "", width = 5, bg = 'White').grid(row = 0, column = 0)
		self.option_keyword.label.grid(row = 1, column = 1, sticky = tk.W)
		self.option_keyword.entry.grid(row = 2, column = 1)

		# tk.Label(self, text = "", width = 5).grid(row = 3, column = 0)
		self.option_credit_type.label.grid(row = 3, column = 1, sticky = tk.W)
		self.option_credit_type.optionmenu.grid(row = 4, column = 1, sticky = tk.W+tk.E)

		tk.Label(self, text = "", width = 5, bg = 'White').grid(row = 5, column = 0)
		self.search_button.grid(row = 6, column = 2)
		self.search_button.button.grid()

		tk.Label(self, text = "", width = 5, bg = 'White').grid(row = 7, column = 0)


class SearchKeyword:
	""" A class that contains widgets related to search with keyword """
 	def __init__(self, parent, name):
		self.name = name
		self.keyword = None

		self.label = tk.Label(parent, text = self.name, bg = 'White')

		self.textvar = tk.StringVar()
		self.entry = tk.Entry(parent, textvariable = self.textvar, width = 15, bg = 'White')

	def set_keyword(self):
		""" Get written keyword from widget an save it"""
		if not self.textvar == '':
			self.keyword = self.textvar.get()
		else:
			self.keyword = None

	def get_keyword(self):
		""" Returns keyword """
		return self.keyword
		

class SearchOption:
	""" A class that can create widgets related to arbitrary search options """
	def __init__(self, parent, name, options):
		self.name = name
		self.options = options
		self.options.insert(0, 'ALL')

		self.label = tk.Label(parent, text = self.name, bg = 'White')

		self.optionvar = tk.StringVar()
		self.optionvar.set(self.options[0])
		self.optionmenu = tk.OptionMenu(parent, self.optionvar, *self.options)
		self.optionmenu.config(bg = 'White', highlightthickness = 0, activebackground = 'white')
		self.optionmenu['menu'].config(bg = 'White')

	def get_optionvar(self):
		""" Returns the selected value in optionmenu instance """
		return self.optionvar.get()

# class for search button
class SearchButton(tk.Frame):
	""" A frame that contains search button """
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, class_ = 'SearchButton')
		self.button = tk.Button(self, text = 'Search', bg = 'White')


###################################################
# classes for display search results

class CourselistFrame(tk.Frame):
	""" One of the main frames that contains widgets related to display courselist """
	def __init__(self, parent, courselist):
		tk.Frame.__init__(self, parent, class_ = 'CourselistFrame', bg = 'White')
		self.grid(row = 2, column = 0, sticky = tk.N)
		self.courselist = courselist
		self.initialize()

	def initialize(self):
		""" A set of functions that is called at the first time """
		self.current_tab = 1
		self.result_list = self.courselist.get_result_list()
		self.update_courses()
		self.add_tabs()

	def add_tabs(self):
		""" Add CourselistTab objects to the list """
		self.tabs = []

		for i in range(self.no_tabs):
			self.tabs.append(CourselistTab(self, str(i+1)))


	def update_courses(self):
		""" Update the list that contains CourselistCourse objects
			that have to be displayed
		"""
		self.courses = []

		self.no_courses = len(self.result_list)
		self.no_tabs = self.no_courses/10 + 1
		
		if self.current_tab < self.no_tabs:
			for course in self.result_list[10*(self.current_tab-1):10*self.current_tab]:
				self.courses.append(CourselistCourse(self, course))
		else:
			for course in self.result_list[10*(self.current_tab-1):]:
				self.courses.append(CourselistCourse(self, course))
	

		logger.debug("Displaying courselist is updated")


	def change_tab(self, current_tab):
		""" Changes current tab and update displaying courselist """
		self.tabs[self.current_tab-1].label.config(bg = 'white')
		self.current_tab = current_tab
		self.tabs[self.current_tab-1].label.config(bg = '#e6e6e6')
		logger.debug("clf.current_tab is changed to %d" %(self.current_tab))
		self.update_courses()



	# methods related to drawing

	def draw(self):
		""" Draws all the contained widgets """
		tk.Label(self, text = "", width = 4, bg = 'White').grid(row = 0, column = 0)
		self.draw_tabs()
		# tk.Label(self, text = '  ').grid(row = 0, column = 2)
		self.draw_courses()
		# self.set_color.draw()
	
		
		
	def draw_tabs(self):
		""" Draws CourselistTab objects """
		for i, tab in enumerate(self.tabs):
			tab.grid(row = i, column = 1)
			if self.current_tab == i+1:
				tab.label.config(bg = '#e6e6e6')
			tab.label.grid()

	def draw_courses(self):
		""" Draws CourselistCourse objects """
		for i, course in enumerate(self.courses):
			course.grid(row = i, column = 3, sticky = tk.W)
			course.label.grid()

	def remove_drawn_courses(self):
		""" Remove drawn CourselistCourse objects """
		for course in self.courses:
			course.destroy()

	def remove_drawn_tabs(self):
		""" Remove drawn CourselistTab objects """
		for tab in self.tabs:
			tab.destroy()


class CourselistTab(tk.Frame):
	""" A frame that contains tab for courselist """
	def __init__(self, parent, text):
		# text is a tab index
		tk.Frame.__init__(self, parent, class_ = 'CourselistTab')
		self.text = text
		self.label = tk.Label(self, text = self.text)
		self.label.config(bg = "White", relief = tk.GROOVE, height = 3, width = 3, padx = 3, pady = 3)

	def get_text(self):
		""" Returns the index of tab"""
		return self.text

	def get_label(self):
		""" Returns the label """
		return self.label



class CourselistCourse(tk.Frame):
	""" A frame that contains courses and label for courselist """
	def __init__(self, parent, course):
		tk.Frame.__init__(self, parent, class_ = 'CourselistCourse')
		self.name = 'CourselistCourse'
		self.course = course
		self.label = tk.Label(self, text = self.course.get_name())
		self.label.config(relief = tk.GROOVE, wraplength = 250, bg = "White", width = 31, height = 3, padx = 3, pady = 3)

	def get_course(self):
		""" Returns Course object """
		return self.course

	def get_label(self):
		""" Returns the label """
		return self.label


###################################################
# classes for display information of course

class InfoFrame(tk.Frame):
	""" One of the main frame that contains widgets related to display information of course """
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, class_ = 'InfoFrame', bg = 'White')
		self.grid(row = 0, column = 1)
		self.parent = parent
		self.current_course = None
		self.header_row = []
		self.second_row = []

		self.create_table()
		self.update_info()


	def create_table(self):
		""" Create table that displays course information
			column 0 : Course code
			column 1 : Course name
			column 2 : Professor
			column 3 : Time
			column 4 : Venue
			column 5 : credit
		"""
		self.header_row.append(tk.Label(self, text = 'Course Code', width = 12, relief = tk.GROOVE, bg = "White"))
		self.header_row.append(tk.Label(self, text = 'Course Name', width = 36, relief = tk.GROOVE, bg = "White"))
		self.header_row.append(tk.Label(self, text = 'Professor', width = 20, relief = tk.GROOVE, bg = "White"))
		self.header_row.append(tk.Label(self, text = 'Time', width = 14, relief = tk.GROOVE, bg = "White"))
		self.header_row.append(tk.Label(self, text = 'Venue', width = 10, relief = tk.GROOVE, bg = "White"))
		self.header_row.append(tk.Label(self, text = 'Credit', width = 5, relief = tk.GROOVE, bg = "White"))

		for i in range(6):
			self.second_row.append(tk.Label(self, text = " ", height = 4, bg = "White", relief = tk.GROOVE))

	def update_info(self):
		""" Display course information on the table """
		if self.current_course != None:
			self.second_row[0].config(text = self.current_course.get_course_code())
			self.second_row[1].config(text = self.current_course.get_name(), wraplength = 275, height = 4)
			self.second_row[2].config(text = self.current_course.get_faculty())
			self.second_row[3].config(text = self.current_course.get_time_str())
			self.second_row[4].config(text = self.current_course.get_venue_str())
			self.second_row[5].config(text = self.current_course.get_credit())
		logger.debug("Displaying course in info_frame is updated")

	def set_current_course(self, course):
		""" Set the course that has to be displayed """
		self.current_course = course
		logger.debug("Current course is changed to %s" %(self.current_course.get_name()))
		self.update_info()

	def draw(self):
		""" Draws all the contained widgets """
		for i in range(len(self.header_row)):
			self.header_row[i].grid(row = 0, column = i, sticky = tk.W+tk.E)
			self.second_row[i].grid(row = 1, column = i, sticky = tk.W+tk.E+tk.N+tk.S)
		tk.Label(self, text = "", width = 4, bg = 'white').grid(row = 0, column = 6)



###################################################
# classes for do some functions


class ButtonFrame(tk.Frame):
	""" One of the main frames that contains widgets that do some functions """
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, class_ = 'ButtonFrame', bg = 'white')
		self.parent = parent
		self.grid(row = 1, column = 1, sticky = tk.N)
		self.credit_label = ButtonCredit(self)
		self.clear_all_button = ButtonClearall(self)
		self.export_button = ButtonIcal(self)

	def draw(self):
		""" Draws all the contained widgets """
		self.credit_label.grid(row = 0, column = 0)
		self.credit_label.label.grid()
		tk.Label(self, text = "", bg = 'white', width = 20).grid(row = 0, column = 1)
		self.clear_all_button.grid(row = 0, column = 2, padx = 20)
		self.clear_all_button.button.grid()
		self.export_button.grid(row = 0, column = 3)
		self.export_button.button.grid()

class ButtonCredit(tk.Frame):
	""" A frame that contains label which displays current credit """
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, class_ = 'ButtonCredit', bg = 'white')
		self.parent = parent
		self.credit = 0
		self.label = tk.Label(self, text = "Credit: " + str(self.credit))
		self.label.config(bg = 'white', width = 20)

	def set_credit(self, model):
		""" Set current credit """
		self.credit = 0
		for ttcourse in model.timetable_frame.ttcourses:
			self.credit += int(ttcourse.course.get_credit())
		self.label.config(text = "Credit: " + str(self.credit))


class ButtonClearall(tk.Frame):
	def __init__(self, parent):
		""" A frame that contains button which clears all the courses currently enrolled """
		tk.Frame.__init__(self, parent, class_ = 'ButtonClearall')
		self.parent = parent
		self.button = tk.Button(self, text = 'Clear All', bg = 'white')

	def clear_all(self, model):
		""" Clear all the courses currently enrolled """
		for ttcourse in model.timetable_frame.ttcourses:
			for ttlabel in ttcourse.get_labels():
				ttlabel.destroy()
		model.timetable_frame.ttcourses = []


class ButtonIcal(tk.Frame):
	""" A frame that contains button which exports current timetable as iCal """
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, class_ = 'ButtonIcal')
		self.parent = parent
		self.button = tk.Button(self, text = 'Export as ical', bg = 'white')


	def export_as_ical(self, model):
		""" Exports current timetable as iCal """
		day_converter = {'M':'mo', 'T':'tu', 'W':'we', 'R':'th', 'F':'fr'}
		date = {'M':7, 'T':1, 'W':2, 'R':3, 'F':4}
		for ttcourse in model.timetable_frame.ttcourses:
			course = ttcourse.get_course()
			summary = course.get_course_code()
			description = course.get_name() + '\n' + 'Faculty: ' + course.get_faculty()
			count = '15'
			if course.half:
				count = '7'
			for i, schedule in enumerate(course.get_schedules()):
				st = schedule.get_start_time()
				et = schedule.get_end_time()
				day = day_converter[schedule.get_day()]
				start_date = date[schedule.get_day()]
				location = schedule.get_venue()
				st_hr = int(st[:2])
				st_mn = int(st[-2:])
				if len(st) == 3:
					st_hr = int(st[0])
				et_mn = int(et[-2:])
				et_hr = int(et[:2])
				name = 'ical/' + summary + str(i+1) +'.ics'
				self.create_ical(name, summary, description, location, count, st_hr, st_mn, et_hr, et_mn, day, start_date)



	def create_ical(self, name, summary, description, location, count, st_hr, st_mn, et_hr, et_mn, day, start_date):
		""" Create iCal file with given values """
		cal = ical.Calendar()

		""" Add Timezone """
		timezone = ical.Timezone()
		timezone.add('TZID', pytz.timezone('US/Eastern'))

		timezone_standard = ical.TimezoneStandard()
		timezone_standard.add('DTSTART', dt.datetime(1601, 11, 4, 2, 0, 0))
		timezone_standard.add('RRULE', {'FREQ':'YEARLY', 'BYDAY':'1SU', 'BYMONTH':'11'})
		timezone_standard.add('TZOFFSETFROM', dt.timedelta(hours = -4))
		timezone_standard.add('TZOFFSETTO', dt.timedelta(hours = -5))


		timezone_daylight = ical.TimezoneDaylight()
		timezone_daylight.add('DTSTART', dt.datetime(1601, 3, 11, 2, 0, 0))
		timezone_daylight.add('RRULE', {'FREQ':'YEARLY', 'BYDAY':'2SU', 'BYMONTH':'3'})
		timezone_daylight.add('TZOFFSETFROM', dt.timedelta(hours = -5))
		timezone_daylight.add('TZOFFSETTO', dt.timedelta(hours = -4))

		timezone.add_component(timezone_standard)
		timezone.add_component(timezone_daylight)

		cal.add_component(timezone)

		""" Add Event"""
		event = ical.Event()
		event.add('DTSTART', dt.datetime(2015, 9, start_date, st_hr, st_mn, 0, tzinfo = pytz.timezone('US/Eastern')))
		event.add('DTEND', dt.datetime(2015, 9, start_date, et_hr, et_mn, 0, tzinfo = pytz.timezone('US/Eastern')))
		event.add('SUMMARY', summary)
		event.add('DESCRIPTION', description)
		event.add('LOCATION',location)
		event.add('RRULE',{'FREQ': 'weekly','COUNT':count,'BYDAY':day})
		cal.add_component(event)


		f = open(name, "wb")
		f.write(cal.to_ical())
		f.close()

	def draw(self):
		""" Draw button """
		self.export_button.grid(row = 0, column = 0)



###################################################
# classes for display user's timetable graphically



class TimetableFrame(tk.Frame):
	""" One of the main frames that contains widgets related to display the timetable
		and information about current timetable
	"""
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, class_ = 'TimetableFrame', bg = 'white')

		# self.timetable = timetable
		self.ttcourses = []
		self.temporary_ttcourse = None


	def draw(self):
		""" Draws background of timetable """
		im = tk.PhotoImage(file = 'img/Timetable.gif')
		timetable=tk.Label(self, image = im)
		timetable.image = im # keep reference
		timetable.pack()

	def collision_detector(self, course):
		""" Detects whether two courses conflict or not """
		for ttcourse in self.get_ttcourses():
			for ttschedule in ttcourse.course.get_schedules():
				for schedule in course.get_schedules():
					if schedule.get_day() == ttschedule.get_day():
						if (schedule.get_start_time() >= ttschedule.get_start_time() and \
							schedule.get_start_time() <= ttschedule.get_end_time()) or \
						   (schedule.get_end_time() >= ttschedule.get_start_time() and \
						   	schedule.get_end_time() <= ttschedule.get_end_time()):
							logger.debug('Collision Detected')
							return False
		return True

	def add_course_ttf(self, course):
		""" Add course to the timetable """
		if self.collision_detector(course):
			self.ttcourses.append(TimetableCourse(self, course))
			self.draw_schedule(self.ttcourses[-1])

	def remove_course_ttf(self, course):
		""" Remove course from the timetable """
		for ttcourse in self.ttcourses:
			if ttcourse.get_course() == course:
				self.ttcourses.remove(ttcourse)
				self.undraw_schedule(ttcourse)
				break

	def draw_schedule(self, ttcourse):
		""" Draws a schedule to the timetable """
		for ttlabel in ttcourse.get_labels():
			[x_pos, y_start, height] = self.time_to_pixel(ttlabel.schedule.get_day(), 
												  		  ttlabel.schedule.get_start_time(), 
												  		  ttlabel.schedule.get_end_time())
			ttlabel.place(x=x_pos, y=y_start, width = 99, height = height)
			# ttlabel.label.grid(sticky = tk.N+tk.S+tk.W+tk.E)
			ttlabel.label.pack(fill = tk.BOTH, expand = 1)
			logger.debug("%s" %(ttlabel.label.cget('text')))

	def undraw_schedule(self, ttcourse):
		""" Removes drawn schedule from the timetable """
		for ttlabel in ttcourse.get_labels():
			ttlabel.destroy()

	def set_temporary_ttcourse(self, course):
		""" Set the course that displayed in timetable temporarily """
		self.temporary_ttcourse = TimetableCourse(self, course)
		self.draw_schedule(self.temporary_ttcourse)
		# self.draw_temporary_label()

	def remove_temporary_ttcourse(self):
		""" Removes the course that added to timetable temporarily """
		self.undraw_schedule(self.temporary_ttcourse)
		self.temporary_ttcourse = None

	def time_to_pixel(self, day, start_time, end_time):
		""" Converts start and end time of Schedule object to the location and size"""
		day_list = ['M','T','W','R','F']
		y_start = (int(start_time) - 800)/100*40 + int(start_time)%100*40/60 + 37
 		y_end = (int(end_time) - 800)/100*40 + int(end_time)%100*40/60 + 35
		for i, iday in enumerate(day_list):
			if day == iday:
				x_pos = i*100 + 72
		height = y_end - y_start
		return [x_pos, y_start, height]

	def get_ttcourses(self):
		""" Returns the list of courses in timetable """
		return self.ttcourses


class TimetableCourse:
	""" A class that contains Course object """
	def __init__(self, parent, course):
		self.parent = parent
		self.course = course
		self.labels = []
		for schedule in self.course.get_schedules():
			label = TimetableLabel(self.parent, self.course, schedule)
			self.add_label(label)
		self.set_color()

	def add_label(self, label):
		""" Adds a label to display """
		self.labels.append(label)

	def set_color(self):
		""" Set color to the label """
		# engr_list = ['misty rose', 'rosybrown1']
		color_list = {'AHS':'lemon chiffon', 'ENG': 'misty rose', 'MTH':'lavender', 'SCI':'azure', 'AWA':'navajo white', 'OIE': 'navajo white', 'OIP':'navajo white'}
		for label in self.labels:
			label.config(bg = color_list.get(self.course.get_course_code()[:3]))
			label.label.config(bg = color_list.get(self.course.get_course_code()[:3]))

	def get_labels(self):
		""" Returns the list of labels """
		return self.labels

	def get_course(self):
		""" Returns the Course object """
		return self.course


class TimetableLabel(tk.Frame):
	""" A label that actually be drawn in timetable and represents schedule """
	def __init__(self, parent, course, schedule):
		tk.Frame.__init__(self, parent, class_ = 'TimetableLabel')
		self.parent = parent
		self.course = course
		self.schedule = schedule
		# engr_list = ['misty rose', 'rosybrown1', 'plum1']
		# color_list = {'AHS':'lemon chiffon', 'ENG': 'misty rose', 'MTH':'lavender', 'SCI':'azure', 'AWA':'navajo white', 'OIE': 'navajo white', 'OIP':'navajo white'}
		self.label = tk.Label(self, text = self.course.get_course_code())

	def get_course(self):
		""" Returns the Course object """
		return self.course



class O2Model:
	""" Model for our program
		Creates main frames as children of the app
		and contains event handlers
	"""
	def __init__(self, root):
		self.root = root
		self.courselist = CourseList()

		self.app = App(root)
		self.search_frame = SearchFrame(self.app)
		self.courselist_frame = CourselistFrame(self.app, self.courselist)
		self.info_frame = InfoFrame(self.app)
		self.button_frame = ButtonFrame(self.app)


		# Timetable Part

		# Notebook Style
		styler = ttk.Style()
		styler.configure('TNotebook', background = 'White', borderwidth = 0)
		styler.configure('TNotebook.Tab', background = 'White',)
		styler.map('TNotebook.Tab', background = [('selected', '#e6e6e6'), ('active', 'white')])

		# Create 3 tabs in notebook
		self.timetable_notebook = ttk.Notebook(self.app)
		tab0 = TimetableFrame(self.timetable_notebook)
		self.timetable_notebook.add(tab0)
		self.timetable_notebook.tab(0, text = 'Timetable 1')
		
		tab1 = TimetableFrame(self.timetable_notebook)
		self.timetable_notebook.add(tab1)
		self.timetable_notebook.tab(1, text = 'Timetable 2')

		tab2 = TimetableFrame(self.timetable_notebook)
		self.timetable_notebook.add(tab2)
		self.timetable_notebook.tab(2, text = 'Timetable 3')
		
		self.timetable_frame = self.root.nametowidget(self.timetable_notebook.select())


		# Draw all the main frames
		self.search_frame.draw()
		self.courselist_frame.draw()
		self.info_frame.draw()
		self.button_frame.draw()
		self.timetable_notebook.grid(row = 2, column = 1)
		self.timetable_frame.draw()


	def get_app(self):
		""" Returns app """
		return self.app


	# event handlers

	def search_course(self):
		""" runs when the searchbutton is clicked
			get search conditions from search_frame
			and make CourseList to run search function
		"""
		logger.debug('search button clicked')

		self.search_frame.option_keyword.set_keyword()
		keyword = self.search_frame.option_keyword.get_keyword()
		credit_type = self.search_frame.option_credit_type.get_optionvar()

		self.courselist.initialize_result_list()
		if keyword != None:
			self.courselist.search_by_keyword(keyword)
		self.courselist.search_by_credit_type(credit_type)

		self.courselist_frame.remove_drawn_courses()
		self.courselist_frame.remove_drawn_tabs()
		self.courselist_frame.initialize()
		self.courselist_frame.draw()

	def change_tab(self, event):
		""" runs when the mouse enters on the tab in courselist_frame
			get number of tab from hovered tab
			and make courselist_frame to set current_tab as the hovered tab
		"""
		tab_number = int(event.widget.get_text())
		self.courselist_frame.remove_drawn_courses() # remove drawn courses
		self.courselist_frame.change_tab(tab_number) 
		self.courselist_frame.draw_courses()


	def display_info(self, event):
		""" runs when the mouse enters on the course in the courselist_frame
			get information of course from selcted course
			and make info_frame to display the course
		"""
		logger.debug("display_info is called")
		course = event.widget.get_course()
		self.info_frame.set_current_course(course)


	def add_temporary_course(self, event):
		""" runs when the mouse enters on the course in the courselist_frame
			get information of course from selected course
			and make timetable_frame to display the course temporarily
		"""
		event.widget.label.config(bg = '#e6e6e6')
		course = event.widget.get_course()
		self.timetable_frame.set_temporary_ttcourse(course)

	def remove_temporary_course(self, event):
		""" runs when the mouse leaves from the course in the courselist_frame
			get information of course from courselist
			and make timetable_frame to remove the course
		"""
		event.widget.label.config(bg = 'white')
		course = event.widget.get_course()
		self.timetable_frame.remove_temporary_ttcourse()

	def tt_add_course(self, event):
		""" runs when the course in the courselist_frame is clicked
			get information of course from clicked course
			and make timetable to add the course
			and make timetable_frame to display the course
		"""
		logger.debug("tt_add_course is called")
		parent_name = event.widget.winfo_parent() # name of parent of clicked label(frame)
		course = self.root.nametowidget(parent_name).get_course() # access the frame via root
		self.timetable_frame.add_course_ttf(course)
		self.button_frame.credit_label.set_credit(self)
		logger.debug("%s is added to ttf" %(course.get_name()))


	def tt_remove_course(self, event):
		""" runs when the course in the timetable_frame is clicked
			get information of course from clicked course
			and make timetable to remove the course
			and make timetable_frame to remove the course
		"""
		logger.debug("tt_remove_course is called")
		parent_name = event.widget.winfo_parent() # name of parent of clicked label(frame)
		course = self.root.nametowidget(parent_name).get_course() # access the frame via root
		self.timetable_frame.remove_course_ttf(course)
		self.button_frame.credit_label.set_credit(self)


	def clear_all(self, event):
		""" runs when the clear all button is pressed
			make clear_all_button to clear all
		"""
		parent_name = event.widget.winfo_parent()
		self.root.nametowidget(parent_name).clear_all(self)
		self.button_frame.credit_label.set_credit(self)
		

	def export_as_ical(self, event):
		""" runs when the export button is pressed
			make export_button to export timetable as iCal
		"""
		parent_name = event.widget.winfo_parent()
		self.root.nametowidget(parent_name).export_as_ical(self)



	def change_notebook(self, event):
		""" runs when the tab in notebook is changed
			change self.timetable_frame to current frame
		"""
		logger.debug("Timetable tab is changed")
		self.timetable_frame = self.root.nametowidget(self.timetable_notebook.select())
		self.timetable_frame.draw()
		self.button_frame.credit_label.set_credit(self)


	




############################################################################
# Controller Classes
############################################################################

class O2Controller:
	""" Model for our program
		Binds events to the widgets
	"""
	def __init__(self, model):
		self.model = model
		self.app = self.model.get_app()

		# modify specific function and add more event_detector later
		self.add_event_detector('Button', '<Button-1>', self.click_button)
		self.add_event_detector('Label', '<Button-1>', self.click_label)

		self.add_event_detector('CourselistTab', '<Enter>', self.model.change_tab)
		self.add_event_detector('CourselistCourse', '<Enter>', self.model.display_info)
		self.add_event_detector('CourselistCourse', '<Enter>', self.model.add_temporary_course)
		self.add_event_detector('CourselistCourse', '<Leave>', self.model.remove_temporary_course)
		self.add_event_detector('TimetableLabel', '<Enter>', self.model.display_info)

		self.model.timetable_notebook.bind('<<NotebookTabChanged>>', self.model.change_notebook)


	def add_event_detector(self, class_, event, function):
		""" Add event detector to certain class """
		self.app.bind_class(class_, event, function, add = '+')

	def click_button(self, event):
		""" Figure out which button is clicked
			and runs proper function
		"""
		parent_name = event.widget.winfo_parent()
		class_ = self.model.root.nametowidget(parent_name).cget('class')
		if class_ == 'SearchButton':
			self.model.search_course()
		elif class_ == 'ButtonClearall':
			self.model.clear_all(event)
		elif class_ == 'ButtonIcal':
			self.model.export_as_ical(event)

	def click_label(self, event):
		""" Figure out which label is 
			and runs proper function
		"""
		parent_name = event.widget.winfo_parent()
		class_ = self.model.root.nametowidget(parent_name).cget('class')
		if class_ == 'CourselistCourse':
			self.model.tt_add_course(event)
		elif class_ == 'TimetableLabel':
			self.model.tt_remove_course(event)





############################################################################
# Main
############################################################################

class O2Main:
	def __init__(self):
		self.root = tk.Tk()
		# self.root.configure(background = 'white')
		self.model = O2Model(self.root)
		self.controller = O2Controller(self.model)

		self.root.mainloop()




if __name__ == "__main__":
	main = O2Main()





