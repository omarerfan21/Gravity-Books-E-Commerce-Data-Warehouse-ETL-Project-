CREATE TABLE Dim_Books (
    BookKey INT PRIMARY KEY IDENTITY(1,1),
    BookID INT,
    Title NVARCHAR(400),
    Language_Name NVARCHAR(50),
    Publisher_Name NVARCHAR(400)
);

CREATE TABLE Dim_Customers (
    CustomerKey INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT,
    Full_Name NVARCHAR(400),
    City NVARCHAR(200),
    Country NVARCHAR(200)
);

CREATE TABLE Dim_Date (
    DateKey INT PRIMARY KEY,
    FullDate DATE,
    Year INT,
    Quarter INT,
    Month INT,
    Day INT,
    DayName NVARCHAR(20)
);

CREATE TABLE Fact_Sales (
    SalesKey INT PRIMARY KEY IDENTITY(1,1),
    BookKey INT,
    CustomerKey INT,
    OrderDateKey INT,
    Price DECIMAL(18, 2),

    CONSTRAINT FK_Fact_Books
    FOREIGN KEY (BookKey)
    REFERENCES Dim_Books(BookKey),

    CONSTRAINT FK_Fact_Customers
    FOREIGN KEY (CustomerKey)
    REFERENCES Dim_Customers(CustomerKey),

    CONSTRAINT FK_Fact_Date
    FOREIGN KEY (OrderDateKey)
    REFERENCES Dim_Date(DateKey)
);