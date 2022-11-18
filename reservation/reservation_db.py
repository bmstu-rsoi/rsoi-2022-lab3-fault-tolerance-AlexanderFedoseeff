import psycopg2
from psycopg2 import Error
import datetime

class ReservationDB:
    def __init__(self):
        self.DB_URL = "postgres://cypubjqljpvvrt:932ead6c14327f40eb1b43bb285b7c76dbfaa929c99b6ae25f7b8915f0ac301d@ec2-52-49-201-212.eu-west-1.compute.amazonaws.com:5432/d3spo9noe4jbtd"
        
        if not self.check_existing_table_hotels():
            self.create_table_hotels()
        if not self.check_existing_table_reservation():
            self.create_table_reservation()

    def check_existing_table_reservation(self):
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        for table in cursor.fetchall():
            if table[0] == "reservation":
                cursor.close()
                return True
        cursor.close()
        connection.close()
        return False

    def check_existing_table_hotels(self):
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        for table in cursor.fetchall():
            if table[0] == "hotels":
                cursor.close()
                return True
        cursor.close()
        connection.close()
        return False


    def create_table_reservation(self):
        q = '''
                    CREATE TABLE reservation
                    (
                        id              SERIAL PRIMARY KEY,
                        reservation_uid uuid UNIQUE NOT NULL,
                        username        VARCHAR(80) NOT NULL,
                        payment_uid     uuid        NOT NULL,
                        hotel_id        INT REFERENCES hotels (id),
                        status          VARCHAR(20) NOT NULL
                            CHECK (status IN ('PAID', 'CANCELED')),
                        start_date      TIMESTAMP WITH TIME ZONE,
                        end_date        TIMESTAMP WITH TIME ZONE
                    );
                    '''
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute(q)
        connection.commit()
        cursor.close()
        connection.close()

    def create_table_hotels(self):
        q1 = '''
                    CREATE TABLE hotels
                    (
                        id        SERIAL PRIMARY KEY,
                        hotel_uid uuid         NOT NULL UNIQUE,
                        name      VARCHAR(255) NOT NULL,
                        country   VARCHAR(80)  NOT NULL,
                        city      VARCHAR(80)  NOT NULL,
                        address   VARCHAR(255) NOT NULL,
                        stars     INT,
                        price     INT          NOT NULL
                    );
                    '''
        q2 = '''
                    INSERT INTO hotels
                    (
                        id,
                        hotel_uid,
                        name,
                        country,
                        city,
                        address,
                        stars,
                        price
                    )
                    VALUES 
                    (
                        1,
                        '049161bb-badd-4fa8-9d90-87c9a82b0668',
                        'Ararat Park Hyatt Moscow',
                        'Россия',
                        'Москва',
                        'Неглинная ул., 4',
                        5,
                        10000
                    );
                    '''
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute(q1)
        cursor.execute(q2)
        connection.commit()
        cursor.close()
        connection.close()
        
    def get_hotels(self):
        result = list()
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            cursor.execute("SELECT id, hotel_uid, name, country, city, address, stars, price FROM hotels")
            record = cursor.fetchall()
            for i in record:
                i = list(i)
                result.append({'hotel_id': i[0], "hotelUid": i[1], "name": i[2], "country": i[3], "city": i[4], "address": i[5], "stars": i[6], "price": i[7]})
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result

    def user_reservations(self, username):
        result = list()
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            q1 = '''
                    SELECT 
                        reservation_uid,
                        payment_uid,
                        hotel_id,
                        status,
                        start_date,
                        end_date 
                    FROM
                    reservation WHERE username = %s
            '''
            q2 = '''
                    SELECT 
                        hotel_uid, 
                        name, 
                        country, 
                        city, address, 
                        stars
                    FROM 
                    hotels WHERE id = %s
            '''
            cursor.execute(q1, (username,))
            reservation = cursor.fetchall()
            print(reservation)
            for i in reservation:
                i = list(i)
                cursor.execute(q2, (i[2],))
                hotel = cursor.fetchall()
                hotel = list(hotel[0])
                result.append({
                                'reservationUid': i[0], 
                                'paymentUid': i[1], 
                                'hotel': {
                                    'hotelUid': hotel[0],
                                    'name': hotel[1],
                                    'fullAddress': hotel[2] + ', ' + hotel[3] + ', ' + hotel[4],
                                    'stars': hotel[5]
                                    }, 
                                'status': i[3], 
                                'startDate': i[4].strftime("%Y-%m-%d"), 
                                'endDate': i[5].strftime("%Y-%m-%d")})
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result

    def reservate(self, reservationUid, username, paymentUid, hotel_id, status, startDate, endDate):
        result = False
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()

            q = '''
                    INSERT INTO reservation
                    (
                        reservation_uid,
                        username,
                        payment_uid,
                        hotel_id,
                        status,
                        start_date,
                        end_date
                    )
                    VALUES 
                    (
                        %s, %s, %s, %s, %s, %s, %s
                    );
                    '''
            cursor.execute(q, (reservationUid, username, paymentUid, hotel_id, status, startDate, endDate))
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

    def cancel_reservation(self, reservationUid):
        result = ''
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            q1 = ''' UPDATE reservation SET status = %s WHERE reservation_uid = %s; '''
            cursor.execute(q1, ('CANCELED', reservationUid))
            r = cursor.rowcount
            connection.commit()
            q2 = ''' SELECT payment_uid FROM reservation WHERE reservation_uid = %s; '''
            cursor.execute(q2, (reservationUid,))
            payment_uid = cursor.fetchall()
            if r > 0:
                result = payment_uid[0]
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result