import psycopg2
from psycopg2 import Error

class LoyaltyDB:
    def __init__(self):
        self.DB_URL = "postgres://cypubjqljpvvrt:932ead6c14327f40eb1b43bb285b7c76dbfaa929c99b6ae25f7b8915f0ac301d@ec2-52-49-201-212.eu-west-1.compute.amazonaws.com:5432/d3spo9noe4jbtd"
        
        if not self.check_existing_table_loyalty():
            self.create_table_loyalty()


    def check_existing_table_loyalty(self):
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables
               WHERE table_schema = 'public'""")
        for table in cursor.fetchall():
            if table[0] == "loyalty":
                cursor.close()
                return True
        cursor.close()
        connection.close()
        return False


    def create_table_loyalty(self):
        q1 = '''
                    CREATE TABLE loyalty
                    (
                        id                SERIAL PRIMARY KEY,
                        username          VARCHAR(80) NOT NULL UNIQUE,
                        reservation_count INT         NOT NULL DEFAULT 0,
                        status            VARCHAR(80) NOT NULL DEFAULT 'BRONZE'
                            CHECK (status IN ('BRONZE', 'SILVER', 'GOLD')),
                        discount          INT         NOT NULL
                    );
                    '''
        q2 = '''
                    INSERT INTO loyalty
                    (
                        id,
                        username,
                        reservation_count,
                        status,
                        discount
                    )
                    VALUES 
                    (
                        1,
                        'Test Max',
                        25,
                        'GOLD',
                        10
                    );
                    '''
        connection = psycopg2.connect(self.DB_URL, sslmode="require")
        cursor = connection.cursor()
        cursor.execute(q1)
        cursor.execute(q2)
        connection.commit()
        cursor.close()
        connection.close()

    
    def get_loyalty(self, username):
        result = list()
        try:
            connection = psycopg2.connect(self.DB_URL, sslmode="require")
            cursor = connection.cursor()
            cursor.execute(''' SELECT reservation_count, status, discount, username FROM loyalty WHERE username = %s ''', (username,))

            record = cursor.fetchall()
            print(record)
            result.append({'reservationCount': record[0][0], 'status': record[0][1], 'discount': record[0][2]})

        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result

    def loyalty_up(self, username):
        result = False
        try:
            current_loyalty = self.get_loyalty(username)
            if len(current_loyalty) > 0:
                current_reservation_count = current_loyalty[0]['reservationCount']
                current_status = current_loyalty[0]['status']
                current_discount = current_loyalty[0]['discount']
                target_reservation_count = current_reservation_count + 1
                if target_reservation_count < 10:
                    target_status = 'BRONZE'
                    target_discount = 5
                elif target_reservation_count < 20:
                    target_status = 'SILVER'
                    target_discount = 7
                else:
                    target_status = 'GOLD'
                    target_discount = 10
                connection = psycopg2.connect(self.DB_URL, sslmode="require")
                cursor = connection.cursor()
                q = ''' UPDATE loyalty SET reservation_count = %s, status = %s, discount = %s WHERE username = %s; '''
                cursor.execute(q, (target_reservation_count, target_status, target_discount, username))
                connection.commit()
                result = True
            else:
                q = '''
                INSERT INTO loyalty
                (
                    username,
                    reservation_count,
                    status,
                    discount
                )
                VALUES (%s, %s, %s, %s);
                '''
                cursor.execute(q, (username, 1, 'BRONZE', 5))
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

    def loyalty_down(self, username):
        result = False
        try:
            current_loyalty = self.get_loyalty(username)
            if len(current_loyalty) > 0:
                current_reservation_count = current_loyalty[0]['reservationCount']
                current_status = current_loyalty[0]['status']
                current_discount = current_loyalty[0]['discount']
                target_reservation_count = current_reservation_count - 1
                if target_reservation_count < 10:
                    target_status = 'BRONZE'
                    target_discount = 5
                elif target_reservation_count < 20:
                    target_status = 'SILVER'
                    target_discount = 7
                else:
                    target_status = 'GOLD'
                    target_discount = 10
                connection = psycopg2.connect(self.DB_URL, sslmode="require")
                cursor = connection.cursor()
                q = ''' UPDATE loyalty SET reservation_count = %s, status = %s, discount = %s WHERE username = %s; '''
                cursor.execute(q, (target_reservation_count, target_status, target_discount, username))
                connection.commit()
                result = True
            else:
                result = False
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
        return result
    
    def create_user(self, username):
        q = '''
            INSERT INTO loyalty
            (
                username,
                reservation_count,
                status,
                discount
            )
            VALUES (%s, %s, %s, %s);
            '''
