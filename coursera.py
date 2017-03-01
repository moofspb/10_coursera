import random
import requests
import argparse
from openpyxl import Workbook
from lxml import etree
from bs4 import BeautifulSoup


URL = 'https://www.coursera.org/sitemap~www~courses.xml'
RANDOM_COURSES = 20


def get_page_content(url):
    page = requests.get(url)
    return page.content


def get_random_list(original_list, new_list_length):
    return random.sample(original_list, new_list_length)


def get_courses_list():
    xml = get_page_content(URL)
    parsed_xml = etree.XML(xml)
    text_content = parsed_xml.xpath('//text()')
    courses_urls = text_content[2::4]
    random_courses = get_random_list(courses_urls, RANDOM_COURSES)
    return random_courses


def get_course_info(course_slug):
    course_page = get_page_content(course_slug)
    page_soup = BeautifulSoup(course_page, 'lxml')
    course_name = page_soup.find('h1', class_='title display-3-text').text
    course_lang = page_soup.find('div', class_='rc-Language').contents[1]
    course_start_date = page_soup.find('div',
                                       class_='startdate rc-StartDateString caption-text').text[7:]
    course_duration = len(page_soup.find_all('div', class_='week'))
    if page_soup.find('div', class_='ratings-text bt3-hidden-xs'):
        course_rating = page_soup.find('div',
                                       class_='ratings-text bt3-hidden-xs').contents[1][20:]
    else:
        course_rating = 'No data'
    course_data = [course_name, course_lang, course_start_date,
                   course_duration, course_rating]
    return course_data


def collect_courses_data(course_urls):
    courses_data = []
    for url in course_urls:
        courses_data.append(get_course_info(url))
    return courses_data
    

def output_courses_info_to_xlsx(filename, courses_data):
    headers = ['Course Name', 'Language', 'Start Date',
               'Duration(weeks)', 'User Rating']
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(headers)
    for course in courses_data:
        worksheet.append(course)
    workbook.save(filename=filename + '.xlsx')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Coursera XML feed, \ '
                                                 'get info about 20 random \ '
                                                 'courses and save to xlsx file')
    parser.add_argument('filename', help='The name of the xlsx file without extension')
    args = parser.parse_args()
    print('The data will be saved in {}.xlsx'.format(args.filename))
    print('Getting courses list...')
    courses_urls = get_courses_list()
    print('Collecting courses data...')
    courses_data = collect_courses_data(courses_urls)
    output_courses_info_to_xlsx(args.filename, courses_data)
    print('Done!')
