import sqlite3


class FastFoodDB:
    @staticmethod
    def connect():
        database = sqlite3.connect('fastfood.db')
        cursor = database.cursor()
        return database, cursor

    @staticmethod
    def close(database):
        database.close()

    @staticmethod
    def create_users_table():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(20) NOT NULL,
            telegram_id BIGINT NOT NULL UNIQUE,
            phone VARCHAR(20)
        );
        ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def first_select_user(chat_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
            SELECT * FROM users WHERE telegram_id = ?
        ''', (chat_id,))
        user = cursor.fetchone()
        FastFoodDB.close(database)
        return user

    @staticmethod
    def first_register_user(chat_id, full_name):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        INSERT INTO users(telegram_id, full_name)
        VALUES (?, ?)
        ''', (chat_id, full_name))
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def finish_register(chat_id, phone):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        UPDATE users
        SET phone = ?
        WHERE telegram_id = ?
        ''', (phone, chat_id))
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def create_cart_table():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts(
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(user_id) UNIQUE,
            total_products INTEGER DEFAULT 0,
            total_price DECIMAL(12, 2) DEFAULT 0  
        )
        ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def create_cart_products_table():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_products(
            cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER REFERENCES carts(cart_id),
            product_name VARCHAR(50) NOT NULL,
            quantity INTEGER NOT NULL,
            final_price DECIMAL(12, 2) NOT NULL,
            
            UNIQUE(cart_id, product_name)
        )
        ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def insert_to_cart(chat_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        INSERT INTO carts(user_id) VALUES
        (
            (SELECT user_id FROM users WHERE telegram_id = ?)
        )
        ''', (chat_id,))
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def update_full_name(chat_id, full_nam):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        UPDATE users
        SET full_name = ?
        WHERE telegram_id = ?
        ''', (full_nam, chat_id))
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def create_categories_table():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
         CREATE TABLE IF NOT EXISTS categories(
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name VARCHAR(20) NOT NULL UNIQUE
        )
        ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def create_products_table():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS products(
               product_id INTEGER PRIMARY KEY AUTOINCREMENT,
               category_id INTEGER NOT NULL,
               product_name VARCHAR(20) NOT NULL UNIQUE,
               price DECIMAL(12, 2) NOT NULL,
               description VARCHAR(100),
               FOREIGN KEY(category_id) REFERENCES categories(category_id)
           )
           ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def insert_categories():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        INSERT INTO categories(category_name) VALUES
        ('Лаваши'),
        ('Донары'),
        ('Ход-Доги'),
        ('Десерты'),
        ('Напитки'),
        ('Соусы')
        ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def get_categories():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT * FROM categories;
        ''')
        categories = cursor.fetchall()
        FastFoodDB.close(database)
        return categories

    @staticmethod
    def alter_product():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        ALTER TABLE products
        ADD COLUMN image TEXT;
        ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def insert_products():
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        INSERT INTO products(category_id, product_name, price, description, image) VALUES
        (1, 'Мини лаваш', 20000, 'Мясо, тесто, помидоры', 'media/lavash_1.jpg'),
        (1, 'Лаваш говяжий', 23000, 'Мясо, тесто, помидоры', 'media/lavash_2.jpg'),
        (1, 'Лаваш с сыром', 25000, 'Мясо, тесто, помидоры', 'media/lavash_3.jpg');
        ''')
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def get_products(category_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT product_id, product_name FROM products WHERE category_id = ?
        ''', (category_id,))
        products = cursor.fetchall()
        FastFoodDB.close(database)
        return products

    @staticmethod
    def get_product_detail(product_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
            SELECT * FROM products WHERE product_id = ?
            ''', (product_id,))
        product = cursor.fetchone()
        FastFoodDB.close(database)
        return product

    @staticmethod
    def get_category_this_product(product_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT category_id FROM products WHERE product_id = ?
        ''', (product_id,))
        category_id = cursor.fetchone()[0]
        FastFoodDB.close(database)
        return category_id

    @staticmethod
    def get_cart_id_by_chat_id(chat_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT cart_id FROM carts
        WHERE user_id = (SELECT user_id FROM users WHERE telegram_id = ?)
        ''', (chat_id,))
        cart_id = cursor.fetchone()[0]
        FastFoodDB.close(database)
        return cart_id

    @staticmethod
    def get_product_name_price(product_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT product_name, price FROM products WHERE product_id = ?
        ''', (product_id,))
        product_name, price = cursor.fetchone()
        FastFoodDB.close(database)
        return product_name, price

    # @staticmethod
    # def insert_new_cart_product(cart_id, product_name, quantity, final_price):
    #     database, cursor = FastFoodDB.connect()
    #     cursor.execute('''
    #     INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
    #     VALUES (?,?,?,?)
    #     ''', (cart_id, product_name, quantity, final_price))
    #     database.commit()
    #     FastFoodDB.close(database)
    #
    # @staticmethod
    # def update_cart_product(quantity, final_price, product_name, cart_id):
    #     database, cursor = FastFoodDB.connect()
    #     cursor.execute('''
    #     UPDATE cart_products
    #     SET quantity = ?,
    #     final_price = ?
    #     WHERE product_name = ? AND cart_id = ?
    #     ''', (quantity, final_price, product_name, cart_id))
    #     database.commit()
    #     FastFoodDB.close(database)


    @staticmethod
    def insert_or_update_cart_product(cart_id, product_name, quantity, final_price):
        database, cursor = FastFoodDB.connect()
        try:
            cursor.execute('''
            INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
            VALUES (?,?,?,?)
            ''', (cart_id, product_name, quantity, final_price))
            database.commit()
            return True
        except Exception as e:
            cursor.execute('''
            UPDATE cart_products
            SET quantity = ?,
            final_price = ?
            WHERE product_name = ? AND cart_id = ?
            ''', (quantity, final_price, product_name, cart_id))
            database.commit()
            return False
        finally:
            database.close()

    @staticmethod
    def sum_quantity_price(cart_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        UPDATE carts
        SET total_products = (
            SELECT SUM(quantity) FROM cart_products
            WHERE cart_id = :cart_id
        ),
        total_price = (
            SELECT SUM(final_price) FROM cart_products
            WHERE cart_id = :cart_id
        )
        WHERE cart_id = :cart_id
        ''', {'cart_id': cart_id})
        database.commit()
        FastFoodDB.close(database)

    @staticmethod
    def get_total_products_price(cart_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT total_products, total_price FROM carts WHERE cart_id = ?
        ''', (cart_id, ))
        total_products, total_price = cursor.fetchone()
        FastFoodDB.close(database)
        return total_products, total_price



    @staticmethod
    def get_cart_products(cart_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT product_name, quantity, final_price FROM cart_products
        WHERE cart_id = ?
        ''', (cart_id, ))
        cart_products = cursor.fetchall()
        FastFoodDB.close(database)
        return cart_products

    @staticmethod
    def get_cart_products_for_keyboard(cart_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        SELECT cart_product_id, product_name FROM cart_products
        WHERE cart_id = ?
        ''', (cart_id, ))
        cart_products = cursor.fetchall()
        FastFoodDB.close(database)
        return cart_products

    @staticmethod
    def delete_cart_product(cart_product_id):
        database, cursor = FastFoodDB.connect()
        cursor.execute('''
        DELETE FROM cart_products WHERE cart_product_id = ?
        ''', (cart_product_id, ))
        database.commit()
        FastFoodDB.close(database)

# FastFoodDB.create_users_table()
# FastFoodDB.create_cart_table()
# FastFoodDB.create_cart_products_table()
# FastFoodDB.create_categories_table()
# FastFoodDB.create_products_table()
# FastFoodDB.insert_categories()
# FastFoodDB.alter_product()
# FastFoodDB.insert_products()
