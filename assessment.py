import sqlite3
db_file = r"C:\Users\bilan\Downloads\parana_25 (2).db"
db = sqlite3.connect(db_file)
cursor = db.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
#setup login
def _display_options(all_options, title, type):
    option_num = 1
    option_list = []
    print("\n", title, "\n")

    for option in all_options:
        code = option[0]
        desc = option[1]
        print(f"{option_num}. {desc}")
        option_num += 1
        option_list.append(code)

    selected_option = 0
    while selected_option <= 0 or selected_option > len(option_list):
        selected_option = int(input(f"Enter the number of the {type}: "))

    return option_list[selected_option - 1]

#login
shopper_id = input("Enter shopper ID: ")

cursor.execute("SELECT first_name FROM shoppers WHERE shopper_id = ?", (shopper_id,))
user = cursor.fetchone()

if not user:
    print("Shopper not found. Exiting program.")
    exit()
else:
    print(f"Welcome {user[0]}")

#create a basket.
cursor.execute("""
    SELECT basket_id
    FROM shopper_baskets
    WHERE shopper_id = ?
    AND DATE(basket_created_date_time) = DATE('now')
    ORDER BY basket_created_date_time DESC
    LIMIT 1
""", (shopper_id,))

result = cursor.fetchone()

if result:
    current_basket_id = result[0]
else:
    cursor.execute("SELECT MAX(basket_id) FROM shopper_baskets")
    max_id = cursor.fetchone()[0]
    current_basket_id = (max_id + 1) if max_id else 1

    cursor.execute("""
        INSERT INTO shopper_baskets (basket_id, shopper_id, basket_created_date_time)
        VALUES (?, ?, DATETIME('now'))
    """, (current_basket_id, shopper_id))

    db.commit()

#option 1
#orer history
def view_orders():
    try:
        cursor.execute("""
            SELECT o.order_id, o.order_date, p.product_description,
                   s.seller_name, op.price, op.quantity, op.status
            FROM shopper_orders o
            JOIN ordered_products op ON o.order_id = op.order_id
            JOIN products p ON op.product_id = p.product_id
            JOIN sellers s ON op.seller_id = s.seller_id
            WHERE o.shopper_id = ?
            ORDER BY o.order_date DESC
        """, (shopper_id,))

        orders = cursor.fetchall()

        if not orders:
            print("No orders placed by this customer")
        else:
            print(f"{'Order':<8}{'Date':<12}{'Product':<25}{'Seller':<15}{'Price':<10}{'Qty':<5}{'Status'}")
            for o in orders:
                print(f"{o[0]:<8}{o[1]:<12}{o[2]:<25}{o[3]:<15}£{o[4]:<9.2f}{o[5]:<5}{o[6]}")

    except Exception as e:
        print("Error retrieving orders:", e)

#option 2
#add items
def add_item():
    global current_basket_id

    cursor.execute("SELECT category_id, category_description FROM product_categories ORDER BY category_description")
    cat_id = _display_options(cursor.fetchall(), "Product Categories", "category")

    cursor.execute("""
        SELECT product_id, product_description 
        FROM products 
        WHERE category_id = ? 
        ORDER BY product_description
    """, (cat_id,))
    prod_id = _display_options(cursor.fetchall(), "Products", "product")

    cursor.execute("""
        SELECT s.seller_id, s.seller_name, ps.price
        FROM sellers s 
        JOIN product_sellers ps ON s.seller_id = ps.seller_id
        WHERE ps.product_id = ?
        ORDER BY s.seller_name
    """, (prod_id,))
    sellers = cursor.fetchall()

    seller_id = _display_options([(s[0], f"{s[1]} - £{s[2]}") for s in sellers],
                                 "Sellers", "seller")

    qty = 0
    while qty <= 0:
        try:
            qty = int(input("Enter quantity: "))
            if qty <= 0:
                print("The quantity must be greater than 0")
        except ValueError:
            print("Invalid number")

    cursor.execute("""
        SELECT price 
        FROM product_sellers 
        WHERE product_id = ? AND seller_id = ?
    """, (prod_id, seller_id))

    price = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price)
        VALUES (?, ?, ?, ?, ?)
    """, (current_basket_id, prod_id, seller_id, qty, price))

    db.commit()
    print("Item added to your basket")

#option 3
#Display basket
def view_basket():
    cursor.execute("""
        SELECT p.product_description, s.seller_name, bc.price, bc.quantity
        FROM basket_contents bc
        JOIN products p ON bc.product_id = p.product_id
        JOIN sellers s ON bc.seller_id = s.seller_id
        WHERE bc.basket_id = ?
    """, (current_basket_id,))

    items = cursor.fetchall()

    if not items:
        print("Your basket is empty")
        return

    total = 0
    print(f"\nBasket ID: {current_basket_id}")

    for i, item in enumerate(items, 1):
        line = item[2] * item[3]
        total += line
        print(f"{i}. {item[0]} from {item[1]} | {item[3]} x £{item[2]:.2f} = £{line:.2f}")

    print(f"Total: £{total:.2f}")

#option 4
#update quantity
def update_item():
    cursor.execute("""
        SELECT bc.rowid, p.product_description, bc.quantity
        FROM basket_contents bc
        JOIN products p ON bc.product_id = p.product_id
        WHERE bc.basket_id = ?
    """, (current_basket_id,))

    items = cursor.fetchall()

    if not items:
        print("Your basket is empty")
        return

    for i, item in enumerate(items, 1):
        print(f"{i}. {item[1]} (Qty: {item[2]})")

    choice = 0

    while choice <= 0 or choice > len(items):
        try:
            choice = int(input("Select item number: "))
            if choice <= 0 or choice > len(items):
                print("Invalid basket item number")
        except ValueError:
            print("Please enter a valid number")
    rowid = items[choice - 1][0]

    new_qty = 0

    while new_qty <= 0:
        try:
            new_qty = int(input("Enter new quantity: "))
            if new_qty <= 0:
                print("The quantity must be greater than 0")
        except ValueError:
            print("Please enter a valid number")

    cursor.execute("""
        UPDATE basket_contents
        SET quantity = ?
        WHERE rowid = ?
    """, (new_qty, rowid))

    db.commit()
    print("Basket updated")

#option 5
#Remove item
def remove_item():
    cursor.execute("""
        SELECT bc.rowid, p.product_description
        FROM basket_contents bc
        JOIN products p ON bc.product_id = p.product_id
        WHERE bc.basket_id = ?
    """, (current_basket_id,))

    items = cursor.fetchall()

    if not items:
        print("Your basket is empty")
        return

    for i, item in enumerate(items, 1):
        print(f"{i}. {item[1]}")

    choice = 0

    while choice <= 0 or choice > len(items):
        try:
            choice = int(input("Select item to remove: "))
            if choice <= 0 or choice > len(items):
                print("Invalid basket item number")
        except ValueError:
            print("Please enter a valid number")

    rowid = items[choice - 1][0]

    confirm = input("Confirm delete (Y/N): ").upper()

    if confirm == "Y":
        cursor.execute("DELETE FROM basket_contents WHERE rowid = ?", (rowid,))
        db.commit()
        print("Item removed")

def checkout():
    try:
        view_basket()

        confirm = input("Proceed to checkout? (Y/N): ").upper()
        if confirm != "Y":
            return

        cursor.execute("""
            SELECT product_id, seller_id, quantity, price
            FROM basket_contents
            WHERE basket_id = ?
        """, (current_basket_id,))

        items = cursor.fetchall()

        if not items:
            print("Your basket is empty")
            return

        cursor.execute("""
            INSERT INTO shopper_orders (shopper_id, order_date, status)
            VALUES (?, DATETIME('now'), 'Placed')
        """, (shopper_id,))

        order_id = cursor.lastrowid

        for item in items:
            cursor.execute("""
                INSERT INTO ordered_products (order_id, product_id, seller_id, quantity, price, status)
                VALUES (?, ?, ?, ?, ?, 'Placed')
            """, (order_id, item[0], item[1], item[2], item[3]))

        cursor.execute("""
            DELETE FROM shopper_baskets 
            WHERE basket_id = ? AND shopper_id = ?
        """, (current_basket_id, shopper_id))

        db.commit()
        print("Checkout complete, your order has been placed")

    except Exception as e:
        db.rollback()
        print("Checkout failed:", e)

#Menu loop
while True:
    print("\n===== ONLINE SHOP MENU =====")
    print("1. View Order History")
    print("2. Add Item to Basket")
    print("3. View Basket")
    print("4. Update Item Quantity")
    print("5. Remove Item")
    print("6. Checkout")
    print("7. Exit")

    choice = input("Select option: ")

    if choice == "1":
        view_orders()
    elif choice == "2":
        add_item()
    elif choice == "3":
        view_basket()
    elif choice == "4":
        update_item()
    elif choice == "5":
        remove_item()
    elif choice == "6":
        checkout()
    elif choice == "7":
        break



