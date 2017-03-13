import random
import requests
import argparse
from collections import namedtuple
from openpyxl import Workbook
from lxml import etree
from bs4 import BeautifulSoup


URL = 'https://www.coursera.org/sitemap~www~courses.xml'


def get_random_list(original_list, new_list_length):
    return random.sample(original_list, new_list_length)


def get_random_courses_urls(url, quantity_of_random_courses=20):
    page = requests.get(url)
    xml = page.content
    parsed_xml = etree.XML(xml)
    text_content = parsed_xml.xpath('//text()')
    all_courses_urls = text_content[2::4]
    random_courses = get_random_list(all_courses_urls, quantity_of_random_courses)
    return random_courses


def get_course_info(url):
    page = requests.get(url)
    course_page = page.content
    page_soup = BeautifulSoup(course_page, 'lxml')
    course_title = page_soup.find('h1', class_='title display-3-text').text
    course_lang = page_soup.find('div', class_='rc-Language').contents[1]
    course_start_date = page_soup.find('div',
                                       class_='startdate rc-StartDateString caption-text').text[7:]
    course_duration = len(page_soup.find_all('div', class_='week'))
    if page_soup.find('div', class_='ratings-text bt3-hidden-xs'):
        course_rating = float(page_soup.find('div',
                                             class_='ratings-text bt3-hidden-xs').contents[1][20:])
    else:
        course_rating = None
    course_data = namedtuple('course_data', ['course_title', 'course_lang', 'course_start_date',
                                             'course_duration', 'course_rating'])
    return course_data(course_title, course_lang, course_start_date,
                       course_duration, course_rating)


def collect_courses_data(course_urls):
    return [get_course_info(url) for url in course_urls]


def output_courses_info_to_workbook(all_courses_data):
    headers = ['Title', 'Language', 'Start Date',
               'Duration(weeks)', 'User Rating']
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(headers)
    for course in all_courses_data:
        worksheet.append(course)
    return workbook


def save_to_xlsx(filename, workbook):
    workbook.save(filename=filename + '.xlsx')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Coursera XML feed, \ '
                                                 'get info about 20 random \ '
                                                 'courses and save to xlsx file')
    parser.add_argument('filename', help='The name of the xlsx file without extension')
    args = parser.parse_args()
    print('The data will be saved in {}.xlsx'.format(args.filename))
    print('Getting courses list...')
    courses_urls = get_random_courses_urls(URL)
    print('Collecting courses data...')
    courses_data = collect_courses_data(courses_urls)
    print(courses_data)
    workbook = output_courses_info_to_workbook(courses_data)
    save_to_xlsx(args.filename, workbook)
    print('Done!')
