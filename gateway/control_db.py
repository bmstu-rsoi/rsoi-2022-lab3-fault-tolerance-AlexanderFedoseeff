import psycopg2
from psycopg2 import Error

class ControlDB:
    def __init__(self):
        self.DB_URL = "postgres://cypubjqljpvvrt:932ead6c14327f40eb1b43bb285b7c76dbfaa929c99b6ae25f7b8915f0ac301d@ec2-52-49-201-212.eu-west-1.compute.amazonaws.com:5432/d3spo9noe4jbtd"
        if not self.check_existing_persons_table():
            self.create_table()

    def check_existing_persons_table(self):
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables
               WHERE table_schema = 'public'""")
        for table in cursor.fetchall():
            if table[0] == "persons":
                cursor.close()
                return True
        cursor.close()
        connection.close()
        return False

    def create_table(self):
        table = '''
                    CREATE TABLE persons
                    (
                    id serial not null,
                       name varchar,
                       address varchar,
                       work varchar,
                       age int
                    );
                    '''
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute(table)
        connection.commit()
        cursor.close()
        connection.close()

    def get_persons(self):
        result = list()
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, address, work, age FROM persons")
            record = cursor.fetchall()
            for i in record:
                i = list(i)
                result.append({"id": i[0], "name": i[1], "address": i[2], "work": i[3], "age": i[4]})
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result

    def create_person(self, person_created):
        result = False
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            insert_query = """ INSERT INTO persons (id, name, age, address, work) VALUES (%s, %s, %s, %s, %s) """
            cursor.execute(insert_query, (person_created['id'], person_created['name'], person_created['age'], person_created['address'], person_created['work']))
            connection.commit()
            result = True
            print("запись успешно вставлена")
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result

    def update_person(self, person_updated):
        result = False
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            if 'name' in person_updated:
                insert_query = """ UPDATE persons SET name = %s WHERE id = %s"""
                cursor.execute(insert_query, (person_updated['name'], person_updated['id']))
            if 'age' in person_updated:
                insert_query = """ UPDATE persons SET age = %s WHERE id = %s"""
                cursor.execute(insert_query, (person_updated['age'], person_updated['id']))
            if 'address' in person_updated:
                insert_query = """ UPDATE persons SET address = %s WHERE id = %s"""
                cursor.execute(insert_query, (person_updated['address'], person_updated['id']))
            if 'work' in person_updated:
                insert_query = """ UPDATE persons SET work = %s WHERE id = %s"""
                cursor.execute(insert_query, (person_updated['work'], person_updated['id']))
            connection.commit()
            result = True
            print("запись успешно обновленаа")
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result

    def delete_person(self, person_id):
        result = False
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            insert_query = """ DELETE FROM persons WHERE id = '%s' """
            cursor.execute(insert_query, (person_id))
            connection.commit()
            result = True
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result