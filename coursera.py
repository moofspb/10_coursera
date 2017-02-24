import random
import requests
import openpyxl
from lxml import etree
from bs4 import BeautifulSoup


URL = 'https://www.coursera.org/sitemap~www~courses.xml'


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
    random_courses = get_random_list(courses_urls, 20)
    return random_courses


def get_course_info(course_slug):
    pass


def output_courses_info_to_xlsx(filepath):
    pass


if __name__ == '__main__':
    get_courses_list()
