import pyodbc
import pandas as pd

source_params = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=.;DATABASE=Gravity_Books;Trusted_Connection=yes;"
dest_params = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=.;DATABASE=GravityBooks_DWH;Trusted_Connection=yes;"

try:
    src_conn = pyodbc.connect(source_params)
    dest_conn = pyodbc.connect(dest_params)
    dest_cursor = dest_conn.cursor()
    dest_cursor.fast_executemany = True

    print("--- الخطوة 1: تنظيف البيانات القديمة ---")
    dest_cursor.execute("DELETE FROM Fact_Sales")
    dest_cursor.execute("DELETE FROM Dim_Books")
    dest_cursor.execute("DELETE FROM Dim_Customers")
    dest_conn.commit()

    print("\n--- الخطوة 2: تحميل جدول Dim_Books ---")
    books_query = "SELECT b.book_id, b.title, l.language_name, p.publisher_name FROM book b JOIN book_language l ON b.language_id = l.language_id JOIN publisher p ON b.publisher_id = p.publisher_id"
    df_books = pd.read_sql(books_query, src_conn)
    dest_cursor.executemany("INSERT INTO Dim_Books ([BookID], [Title], [Language_name], [Publisher_name]) VALUES (?,?,?,?)", df_books.values.tolist())
    print(f"تم تحميل {len(df_books)} كتاب بنجاح.")

    print("\n--- الخطوة 3: تحميل جدول Dim_Customers ---")
    cust_query = "SELECT customer_id, first_name + ' ' + last_name as Full_Name FROM customer"
    df_cust = pd.read_sql(cust_query, src_conn)
    df_cust['City'] = 'Unknown'
    df_cust['Country'] = 'Unknown'
    dest_cursor.executemany("INSERT INTO Dim_Customers ([CustomerID], [Full_Name], [City], [Country]) VALUES (?,?,?,?)", df_cust[['customer_id', 'Full_Name', 'City', 'Country']].values.tolist())
    print(f"تم تحميل {len(df_cust)} عميل بنجاح.")

    print("\n--- الخطوة المضافة: ملء جدول Dim_Date ---")
    start_date = '2000-01-01'
    end_date = '2030-12-31'
    dates = pd.date_range(start_date, end_date)
    df_date = pd.DataFrame({
        'DateKey': dates.strftime('%Y%m%d').astype(int),
        'FullDate': dates,
        'Year': dates.year,
        'Month': dates.month,
        'Day': dates.day
    })
    
    dest_cursor.execute("SELECT COUNT(*) FROM Dim_Date")
    if dest_cursor.fetchone()[0] == 0:
        print("جدول التاريخ فارغ، يتم ملؤه الآن...")
        dest_cursor.executemany("INSERT INTO Dim_Date (DateKey, FullDate, [Year], [Month], [Day]) VALUES (?,?,?,?,?)", df_date.values.tolist())
        dest_conn.commit()

    print("\n--- الخطوة 4: تحميل جدول الحقائق Fact_Sales ---")
    fact_sql = """
    INSERT INTO Fact_Sales ([BookKey], [CustomerKey], [OrderDateKey], [Price])
    SELECT b.BookKey, c.CustomerKey, CAST(FORMAT(src_o.order_date, 'yyyyMMdd') AS INT), src_ol.price
    FROM Gravity_Books.dbo.cust_order src_o
    JOIN Gravity_Books.dbo.order_line src_ol ON src_o.order_id = src_ol.order_id
    JOIN Dim_Books b ON src_ol.book_id = b.BookID
    JOIN Dim_Customers c ON src_o.customer_id = c.CustomerID
    """
    dest_cursor.execute(fact_sql)
    dest_conn.commit()
    print("تم تحميل Fact_Sales بنجاح!")
    print("\nالعملية اكتملت بنجاح 100%!")

except Exception as e:
    print(f"\nحدث خطأ: {e}")
    dest_conn.rollback()
finally:
    src_conn.close()
    dest_conn.close()
