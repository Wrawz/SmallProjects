# pip install mysql-connector-python
# pip install matplotlib
# pip install numpy==1.19.3

import mysql.connector
from mysql.connector import errorcode
import re
import matplotlib.pyplot as plotter
import json
import numpy as np


"""
PLEASE CHECK
https://github.com/Wrawz/SmallExercises/tree/main/practicing_some_python_db/utils
FOR AN UP-TO-DATE FILE
"""


database_settings = {
    "user": "root",
    "password": "1dG81CvAkA",
    "host": "127.0.0.1",
    "database_name": "test"
}

test_database_tables = {
    "table_for_bands": "band",
    "table_for_albums": "album",
    "table_for_songs": "song",
    "table_for_users": "users",
    "table_n_to_n_songs_and_users": "song_has_users"
}

band_table_columns = {
    "band_id": "id",
    "band_name": "name",
    "band_creation_year": "creationYear"
}

album_table_columns = {
    "album_id": "id",
    "album_band_id": "band_id",
    "album_name": "name",
    "album_year_released": "yearReleased"
}

song_table_columns = {
    "song_id": "id",
    "song_album_id": "album_id",
    "song_name": "name"
}

users_table_columns = {
    "user_id": "id",
    "user_name": "name",
    "user_rg": "RG"
}

song_has_users_table_columns = {
    "song_and_users_song_id": "song_id",
    "song_and_users_users_id": "users_id"
}


def get_connection(database_configuration) -> mysql.connector.MySQLConnection:
    try:
        return mysql.connector.connect(user=database_configuration["user"],
                                       password=database_configuration["password"],
                                       host=database_configuration["host"],
                                       database=database_configuration["database_name"])
    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username and/or password are wrong.")
        elif error.errno == errorcode.ER_BAD_DB_ERROR:
            print("This database doesn't exist.")
        else:
            print("Something went wrong:")
            print(error)


def query_songs_for_bands_with_their_albums(database_configuration, band_name) -> None:
    matches = re.match("^\\w+(\\s\\w+)*$", band_name)
    if not matches:
        print("Band name doesn't match the required string.")
        return
    connection = get_connection(database_configuration)
    try:
        cursor = connection.cursor()
        # SELECT band.name AS band, album.name AS album, song.name AS song
        # FROM band
        # INNER JOIN album ON band.id = album.band_id
        # INNER JOIN song ON album.id = song.album_id
        # WHERE band.name LIKE '%{band_name}%';
        cursor.execute(f"SELECT {test_database_tables['table_for_bands']}.{band_table_columns['band_name']} AS band, "
                       f"{test_database_tables['table_for_albums']}.{album_table_columns['album_name']} AS album, "
                       f"{test_database_tables['table_for_songs']}.{song_table_columns['song_name']} AS song "
                       f"FROM {test_database_tables['table_for_bands']} "
                       f"INNER JOIN {test_database_tables['table_for_albums']} ON "
                       f"{test_database_tables['table_for_bands']}.{band_table_columns['band_id']} "
                       f"= {test_database_tables['table_for_albums']}.{album_table_columns['album_band_id']} "
                       f"INNER JOIN {test_database_tables['table_for_songs']} ON "
                       f"{test_database_tables['table_for_albums']}.{album_table_columns['album_id']} "
                       f"= {test_database_tables['table_for_songs']}.{song_table_columns['song_album_id']} "
                       f"WHERE band.name LIKE %s;", ("%" + band_name + "%",))
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            print(row)
    except mysql.connector.Error as error:
        print(error)
    else:
        cursor.close()
    finally:
        connection.close()


def query_songs_of_a_specific_user(database_configuration, username) -> None:
    matches = re.match("^[A-z]+(\\s[A-z]+)*$", username)
    if not matches:
        print("Invalid username.")
        return
    connection = get_connection(database_configuration)
    try:
        cursor = connection.cursor()
        # SELECT song.name AS songs FROM song
        # INNER JOIN song_has_users ON song.id = song_has_users.song_id
        # INNER JOIN users ON song_has_users.users_id = users.id
        # WHERE users.id = (SELECT users.id FROM users WHERE users.name LIKE '%{username}%');
        cursor.execute(f"SELECT {test_database_tables['table_for_songs']}.{song_table_columns['song_name']} AS songs "
                       f"FROM {test_database_tables['table_for_songs']} "
                       f"INNER JOIN {test_database_tables['table_n_to_n_songs_and_users']} "
                       f"ON {test_database_tables['table_for_songs']}.{song_table_columns['song_id']} "
                       f"= {test_database_tables['table_n_to_n_songs_and_users']}.{song_has_users_table_columns['song_and_users_song_id']} "
                       f"INNER JOIN {test_database_tables['table_for_users']} "
                       f"ON {test_database_tables['table_n_to_n_songs_and_users']}.{song_has_users_table_columns['song_and_users_users_id']} "
                       f"= {test_database_tables['table_for_users']}.{users_table_columns['user_id']} "
                       f"WHERE {test_database_tables['table_for_users']}.{users_table_columns['user_id']} "
                       f"= (SELECT {test_database_tables['table_for_users']}.{users_table_columns['user_id']} "
                       f"FROM {test_database_tables['table_for_users']} "
                       f"WHERE {test_database_tables['table_for_users']}.{users_table_columns['user_name']} LIKE %s);", ("%" + username + "%",))
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            print(row)
    except mysql.connector.Error as error:
        print(error)
    else:
        cursor.close()
    finally:
        connection.close()


def count_how_many_users_listen_to_each_song(database_configuration) -> list:
    connection = get_connection(database_configuration)
    song_and_number_of_listeners = []
    try:
        cursor = connection.cursor()
        # SELECT song.name AS songTitle, count(song_has_users.users_id) AS userQuantity
        # FROM song_has_users INNER JOIN song ON song.id = song_has_users.song_id GROUP BY song_has_users.song_id;
        cursor.execute(f"SELECT {test_database_tables['table_for_songs']}.{song_table_columns['song_name']} "
                       f"AS songTitle, count({test_database_tables['table_n_to_n_songs_and_users']}."
                       f"{song_has_users_table_columns['song_and_users_users_id']}) AS userQuantity "
                       f"FROM {test_database_tables['table_n_to_n_songs_and_users']} "
                       f"INNER JOIN {test_database_tables['table_for_songs']} "
                       f"ON {test_database_tables['table_for_songs']}.{song_table_columns['song_id']} "
                       f"= {test_database_tables['table_n_to_n_songs_and_users']}."
                       f"{song_has_users_table_columns['song_and_users_song_id']} "
                       f"GROUP BY {song_has_users_table_columns['song_and_users_song_id']} "
                       f"ORDER BY userQuantity DESC;")
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            song_and_number_of_listeners.append(row)
    except mysql.connector.Error as error:
        print(error)
    else:
        cursor.close()
    finally:
        connection.close()
    return song_and_number_of_listeners


def create_graph(filename) -> None:
    matches = re.match("^\\w+$", filename)
    if not matches:
        print("Invalid filename.")
        return
    data = count_how_many_users_listen_to_each_song(database_settings)
    x = []
    for each_pair in data:
        x.append(each_pair[0])
    y = []
    for each_pair in data:
        y.append(each_pair[1])
    x_axis = "Song names"
    y_axis = "Number of people"
    plotter.figure(figsize=(len(data) * 2.5, 10))
    bar_colors = get_colors_for_graph2([0, 0.6, 0], len(data), y, max(y))
    # bar_colors = get_colors_for_graph([0, 0.5, 0], len(data))
    plotter.bar(x, y, color=bar_colors)
    plotter.title("Listeners per Song")
    plotter.xlabel(x_axis)
    plotter.ylabel(y_axis)
    plotter.savefig(filename + ".png", dpi=300)


def get_colors_for_graph(tuple_color_but_in_list, graph_length) -> list[tuple[float, float, float, float]]]:
    matches = re.match("^[0-9]+$", str(graph_length))
    if not matches:
        print("Invalid length.")
        return tuple([0.0, 0.0, 0.0, 0.0])
    if len(tuple_color_but_in_list) != 3:
        print("Invalid color.")
        return tuple([0.0, 0.0, 0.0, 0.0])
    r, g, b = tuple_color_but_in_list
    alphas = np.linspace(0.2, 1, graph_length)
    returning_list = []
    for i in range(-1, -1 * (graph_length + 1), -1):
        returning_list.append(tuple([r, g, b, alphas[i]]))
    return returning_list


def get_colors_for_graph2(tuple_color_but_in_list, graph_length, result_list, highest_value) -> list[tuple[float, float, float, float]]]:
    matches = re.match("^[0-9]+$", str(graph_length))
    if not matches:
        print("Invalid length.")
        return tuple([0.0, 0.0, 0.0, 0.0])
    if len(tuple_color_but_in_list) != 3:
        print("Invalid color.")
        return tuple([0.0, 0.0, 0.0, 0.0])
    r, g, b = tuple_color_but_in_list
    alphas = []
    for i in result_list:
        alphas.append(i/highest_value)
    returning_list = []
    for i in range(0, graph_length):
        returning_list.append(tuple([r, g, b, alphas[i]]))
    return returning_list


json_phone_numbers = [
    {"phone numbers": [{"John": "987654321"}, {"Mary": "988887777"}, {"Anna": "911112222"}]}
]

string_people_ages = '{"John": 34, "Mary": 26, "Anna": 28}'

json_people_ages = {"John": 25, "Mary": 29, "Anna": 30}


def get_items_from_json_file(file_name_with_extension) -> dict:
    with open(file_name_with_extension, "r") as file:
        file_content = json.load(file)
    return file_content


def create_json_files_from_lists_with_dictionaries_inside(file_name, list_with_dictionaries_inside) -> None:
    with open(file_name, "w") as file:
        json.dump(list_with_dictionaries_inside, file)
        

if __name__ == "__main__":
    query_songs_for_bands_with_their_albums(database_settings, "beatles")
    query_songs_of_a_specific_user(database_settings, "maria")
    query_songs_of_a_specific_user(database_settings, "daniel")
    create_graph("idk")
    json_file_items = get_items_from_json_file("test.json")
    print(json_file_items["books"][0])
    create_json_files_from_lists_with_dictionaries_inside("test2.json", json_phone_numbers)
    people_age1 = json.loads(string_people_ages)
    print(people_age1["John"])
    people_age2 = json.dumps(json_people_ages)
    print(people_age2)
