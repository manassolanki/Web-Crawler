import os
import json
import datetime
import urllib.request

from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from movie_collection_etl import MovieCollection, create_database_engine


# load the movie config from the config file
def load_etl_config():
    etl_config = None
    with open(os.path.join(os.getcwd(),'etl_config.json')) as f:
        etl_config = json.load(f)
    return etl_config


# crawl a movie from the given url
def crawl_movie_collection(movie_name, release_date, movie_url):
    # get the concerned HTML from the URL
    html_page = urllib.request.urlopen(movie_url).read().decode('utf-8')
    soup = BeautifulSoup(html_page, 'html.parser')
    main_content = soup.find_all("div", "td-ss-main-content")
    collection_table = main_content[0].find("table", "tablepress")

    if collection_table:
        for row in collection_table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            cell_list = [cell.text.strip() for cell in cells]

            # no of days till release and data of collection
            days_from_release = cell_list[0]
            no_of_days = days_from_release.lower().split('day')[1].strip()
            if '-' in no_of_days:
                no_of_days = no_of_days.split('-')[0].strip()
            collection_date = release_date + datetime.timedelta(days=int(no_of_days)-1)

            # clean the collection amount and convert into float
            if '₹' in cell_list[1]:
                movie_collection = cell_list[1].split('₹')[1]
            if 'Cr' in movie_collection:
                movie_collection = movie_collection.split('Cr')[0]
            box_office_collection = float(movie_collection.strip())*(10**7)

            yield dict(
                movie_name=movie_name,
                days_from_release=days_from_release,
                date_of_collection=collection_date,
                box_office_collection=box_office_collection
            )


# add the row in the database
def add_in_database(session, data_row):
    new_movie_collection = MovieCollection(**data_row)
    session.add(new_movie_collection)
    session.commit()


def web_crawler():
    """This function will be used to crawl the web using the ETL config information
        from the ETL json files. This also create the database connection and insert
        data into the sqlite database
    """
    etl_config = load_etl_config()

    # create the db session
    engine = create_database_engine()
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    try:
        for movie, release_date in etl_config['movies'].items():
            # format the movie name
            movie = movie.strip()
            formatted_movie_name = "-".join(movie.lower().split(" "))
            movie_url = etl_config['base_url'] + formatted_movie_name + etl_config["tail_url"]

            # format the date
            release_date = datetime.datetime.strptime(release_date, '%Y-%m-%d')

            # get the data from the generator and store in the database
            for data_row in  crawl_movie_collection(movie, release_date, movie_url):
                add_in_database(session, data_row)

    except Exception as e:
        print ('!!!!.......Error Found........!!!!!!!')
        print (e)
