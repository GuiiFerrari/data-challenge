from mysql.connector import connect, Error
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.size"] = 15


def connect_to_db() -> connect:
    """
    Connect to the database.

    Returns:
        connect
            Database connection.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
        password = f.read()
    try:
        db = connect(
            host="35.199.127.241",
            user="looqbox-challenge",
            password=password,
            database="looqbox_challenge",
        )
    except Error as e:
        print(e)
        exit(1)
    return db


def sql_test_1() -> None:
    """
    First answer to SQL test.

    Returns:
        None
    """
    db: connect = connect_to_db()
    query = """
    SELECT product_name FROM data_product
    ORDER BY product_val DESC
    LIMIT 10;"""
    with db.cursor() as cursor:
        cursor.execute(query)
        products: list = cursor.fetchall()
        for product in products:
            print(product[0])
    db.close()


def sql_test_2() -> None:
    """
    Second answer to SQL test.

    Returns:
        None
    """
    db: connect = connect_to_db()
    query = """
    SELECT DISTINCT section_name FROM data_product
    WHERE DEP_NAME = 'BEBIDAS' OR DEP_NAME = 'PADARIA';
    """
    with db.cursor() as cursor:
        cursor.execute(query)
        sections: list = cursor.fetchall()
        for section in sections:
            print(section[0])
    db.close()


def sql_test_3() -> None:
    """
    Third answer to SQL test.

    Returns:
        None
    """
    db: connect = connect_to_db()
    query = """
    SELECT data_store_cad.BUSINESS_NAME, SUM(data_store_sales.sales_value)
    FROM data_store_sales, data_store_cad
    WHERE (data_store_sales.STORE_CODE = data_store_cad.STORE_CODE)
    AND data_store_sales.date BETWEEN '2019-01-01' AND '2019-03-31'
    GROUP BY data_store_cad.BUSINESS_NAME
    ORDER BY data_store_cad.BUSINESS_NAME;"""
    with db.cursor() as cursor:
        cursor.execute(query)
        results: list = cursor.fetchall()
        print("Total sale of products")
        for result in results:
            print(f"Business name = {result[0]}. Amount = ${result[1]:.2f}")
    db.close()


def retrieve_data(
    product_code: int = None, store_code: int = None, date: list[str] = None
) -> pd.DataFrame:
    """Retrieve data from the database.

    Parameters:
        product_code: int, optional
            Product code.
        store_code: int, optional
            Store code.
        date: list[str], optional
            List of two dates.

    Returns:
        pd.DataFrame
            Dataframe with the data.
    """
    db: connect = connect_to_db()
    if product_code is None and store_code is None and date is None:
        query = """
        SELECT * FROM data_product_sales;"""
        with db.cursor() as cursor:
            cursor.execute(query)
            results: list = cursor.fetchall()
            df = pd.DataFrame(results)
            # Name of the columns
            header: list = [
                cursor.description[i][0] for i in range(len(cursor.description))
            ]
            df.columns = header
        db.close()
        return df

    query = f"""
    SELECT * FROM data_product_sales
    WHERE PRODUCT_CODE = {product_code}
    AND STORE_CODE = {store_code}
    AND DATE BETWEEN "{date[0]}" AND "{date[1]}";"""
    with db.cursor() as cursor:
        cursor.execute(query)
        results: list = cursor.fetchall()
        df = pd.DataFrame(results)
        # Name of the columns
        if df.empty is False:
            header: list = [tup[0] for tup in cursor.description]
            df.columns = header
    db.close()
    return df


def do_query(db: connect, query: str) -> pd.DataFrame:
    """
    Execute the query.

    Parameters:
        db: connect
            Database connection.
        query: str
            Query to be executed.

    Returns:
        pd.DataFrame
            Dataframe with the data.
    """
    with db.cursor() as cursor:
        cursor.execute(query)
        results: list = cursor.fetchall()
        df = pd.DataFrame(results)
        # Name of the columns
        header: list = [tup[0] for tup in cursor.description]
        df.columns = header
    return df


def case_2(query: str = None, filter: list[str] = None) -> pd.DataFrame:
    """
    Case 2 of the challenge.

    Parameters:
        query: str
            Query to be executed.
        filter: list[str]
            List of filters.

    Returns:
        pd.DataFrame
            Dataframe with the data.
    """
    db: connect = connect_to_db()
    query_1 = """
    SELECT
        STORE_CODE,
        STORE_NAME,
        START_DATE,
        END_DATE,
        BUSINESS_NAME,
        BUSINESS_CODE
    FROM data_store_cad
    """
    query_2 = """
    SELECT
        STORE_CODE,
        DATE,
        SALES_VALUE,
        SALES_QTY
        FROM data_store_sales
    WHERE DATE BETWEEN '2019-01-01' AND '2019-12-31'
    """
    df1: pd.DataFrame = do_query(db, query_1)
    df2: pd.DataFrame = do_query(db, query_2)
    d: dict = {
        store_name: store_code
        for store_code, store_name in zip(df1["STORE_CODE"], df1["STORE_NAME"])
    }
    d2: dict = {
        store_name: store_business
        for store_name, store_business in zip(
            df1["STORE_NAME"], df1["BUSINESS_NAME"]
        )
    }
    store_amount: dict = {
        store_name: df2["SALES_VALUE"]
        .loc[df2["STORE_CODE"] == d[store_name]]
        .sum()
        / df2["SALES_QTY"].loc[df2["STORE_CODE"] == d[store_name]].sum()
        for store_name in d.keys()
    }
    df3: pd.DataFrame = pd.DataFrame()
    df3["Loja"] = df1["STORE_NAME"]
    df3["Categoria"] = [d2[store_name] for store_name in df3["Loja"]]
    df3["TM"] = [
        f"{store_amount[store_name]:.2f}" for store_name in df3["Loja"]
    ]
    df3.sort_values(by=["Loja"], inplace=True)
    df3.index = range(1, len(df3) + 1)
    db.close()
    print(df3)


def case_3() -> None:
    """
    Case 3 of the challenge.

    Returns:
        None
    """
    db: connect = connect_to_db()
    query = """
    SELECT Genre, Year, RevenueMillions FROM IMDB_movies;
    """
    df: pd.DataFrame = do_query(db, query)
    db.close()
    years: list[int] = df["Year"].unique()
    index = [
        "Comedy,Drama,Romance",
        "Action,Adventure,Fantasy",
        "Crime,Drama,Thriller",
        "Animation,Adventure,Comedy",
        "Action,Adventure,Sci-Fi",
    ]
    years.sort()
    colors = ["green", "pink", "orange", "red", "blue"]
    fig = plt.figure(dpi=150)
    for year in years:
        y = [
            float(
                df.query(f"Genre == '{genre}' & Year == {year}")[
                    "RevenueMillions"
                ].sum()
            )
            for genre in index
        ]
        plt.hist(
            [[year] for _ in range(len(y))],
            weights=[[y_i] for y_i in y],
            bins=[year - 0.5, year + 0.5],
            align="mid",
            histtype="bar",
            color=colors,
            label=index,
        )
    handles, labels = plt.gca().get_legend_handles_labels()
    labels.reverse()
    handles.reverse()
    by_label = dict(zip(labels, handles))
    plt.gca().legend(
        by_label.values(),
        by_label.keys(),
        loc="upper left",
        framealpha=1.0,
        edgecolor="black",
    )
    plt.xlabel("Year")
    plt.xticks(years)
    plt.ylabel("Revenue (millions)")
    plt.title("Revenue (in millions) by genre and year")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # sql_test_1()
    # sql_test_2()
    # sql_test_3()
    # print(
    #     "Usage with arguments\n(product_code = 18 and store_code = 1 (between 2019-01-01 and 2019-03-31)):\n"
    # )
    # df: pd.DataFrame = retrieve_data(18, 1, ["2019-01-01", "2019-03-31"])
    # print(df)
    # df: pd.DataFrame = retrieve_data(1, 18, ["2019-01-01", "2019-03-31"])
    # print(df)
    # print("\nUsage without arguments:\n")
    # print(retrieve_data())
    # case_2()
    case_3()
    exit(0)
