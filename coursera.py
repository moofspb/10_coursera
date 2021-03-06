import random
import requests
import argparse
from collections import namedtuple
from openpyxl import Workbook
from lxml import etree
from bs4 import BeautifulSoup


URL = 'https://www.coursera.org/sitemap~www~courses.xml'


def get_random_courses_pages(url, quantity_of_random_courses=20):
    page = requests.get(url)
    xml = page.content
    parsed_xml = etree.XML(xml)
    text_content = parsed_xml.xpath('//text()')
    all_courses_urls = text_content[2::4]
    random_courses = random.sample(all_courses_urls, quantity_of_random_courses)
    courses_pages = [requests.get(url).content for url in random_courses]
    return courses_pages


def parse_course_data(html):
    page_soup = BeautifulSoup(html, 'lxml')
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


def collect_courses_data(course_pages):
    return [parse_course_data(page) for page in course_pages]


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
    courses_urls = get_random_courses_pages(URL)
    print('Collecting courses data...')
    courses_data = collect_courses_data(courses_urls)
    workbook = output_courses_info_to_workbook(courses_data)
    save_to_xlsx(args.filename, workbook)
    print('Done!')
