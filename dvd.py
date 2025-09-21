import os
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st 
import matplotlib.pyplot as plt
st.set_page_config(
    page_title = "Data Analysis App",
    layout = "wide"
) 
st.title("dvdrental Database Analysis")
st.write("""
Welcome to this Film Analysis App.

Use the sidebar to navigate through different sections of the dashboard.

This app will answer the following questions:
- What are the top 10 most rented movies?
- Which customers spend the most money on rentals?
- Which film categories generate the most revenue?
- What are the busiest rental periods (by day, month, or hour)?
- Which stores perform better in terms of rentals and revenue?
""")
st.sidebar.header("User Input Feature")
name = st.sidebar.text_input("Enter your name:", "Streamlit User")
st.header(f"Hello {name}! Lets create something interractive")
menu = st.sidebar.radio(
   "Choose a section:",
   ["Home", "Most_rented_movies", "top10_rented_movies", "Top_spenders_rentals", "Category_revenue", "Busiest_rental_days", "Busiest_rental_month", "Store_rentals", "Store_revenue", "Summary"]
)
import sqlalchemy 
from sqlalchemy import create_engine

# Step 1: Get DATABASE_URL from Streamlit secrets or environment variable
DATABASE_URL = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")

# Step 2: Check if DATABASE_URL is set
if not DATABASE_URL:
    st.error("DATABASE_URL not set. Please configure it in Streamlit secrets or environment variables.")
else:
    # Step 3: Create SQLAlchemy engine with SSL for Supabase
    try:
        engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
        with engine.connect() as conn:
            st.success("✅ Connected to the database successfully!")
    except Exception as e:
        st.error(f"Database connection failed: {e}")

if menu == "Home":
    st.header("Welcome to the DVD Rental Dashboard")
    st.write("Select a section from the sidebar to begin.")
elif menu == "Most_rented_movies":
    st.header("Most Rented Movies Analysis")
    #Database connection
    #What are the top 10 most rented movies?
    Most_rented_movies = pd.read_sql("""
    SELECT 
        title AS Film_title,
        COUNT(rental_id) AS Rental_count
    FROM
        rental
    JOIN
        inventory on rental.inventory_id = inventory.inventory_id
    JOIN
        film on inventory.film_id = film.film_id
    GROUP BY
        Film_title
    ORDER BY
        Rental_count DESC;""", engine)
    Most_rented_movies.index = Most_rented_movies.index + 1
    Most_rented_movies.index.name = "Rank"
    st.subheader("Most Rented Movies in Descending Order")
    Most_rented_movies
    #Slider to select number of top rented movies to display
    st.sidebar.header("Most Rented Movies in Descending Order")
        
    #rented_movies_inOrder = st.sidebar.slider("Select the number of top rented movie to display:", min_value=10, max_value=len(Most_rented_movies), value=10, step=5)
    #st.sidebar.write(f"Displaying the top {rented_movies_inOrder} most rented movies.")
    #Most_rented_movies = Most_rented_movies.head(rented_movies_inOrder)

    #Create interactive bar chart with Altair
    #import altair as alt
    #chart = (
      #  alt.Chart(Most_rented_movies)
       # .mark_bar()
        #.encode(
         ### tooltip=["film_title", "rental_count"]
    #)
     #   .properties(
    #        title="Rental Frequency of All 958 Films",
     ##      height=1000  # make tall enough to scroll
    #)
    #)

    #st.altair_chart(chart, use_container_width=True)

elif menu == "top10_rented_movies":
    st.header("Top 10 Most Rented Movies Analysis")
    #What are the top 10 most rented movies?
    top10_rented_movies = pd.read_sql("""
    SELECT 
        title AS Film_title,
        COUNT(rental_id) AS Rental_count
    FROM
        rental
    JOIN
        inventory on rental.inventory_id = inventory.inventory_id
    JOIN
        film on inventory.film_id = film.film_id
    GROUP BY
        Film_title
    ORDER BY
        Rental_count DESC LIMIT 10;""", engine)
        #df = pd.read_sql('select * from actor', 'postgresql://postgres:edisun@localhost:5432/dvdrental')
    top10_rented_movies.index = top10_rented_movies.index + 1
    top10_rented_movies.index.name = "Rank"
    st.subheader("Top 10 Most Rented Movies")
    st.write(top10_rented_movies)
    st.sidebar.header("Top 10 Most Rented Movies")
    st.sidebar.info("The table above shows the top 10 most rented movies from the dvdrental database.")

    #Bar chart of top 10 most rented movies
    import seaborn as sns
    st.subheader("The Bar chart below shows the top 10 most rented movies.")
    plt.figure(figsize=(10,5))
    # Generate 10 distinct colors starting from green using hsv colormap
    colors = plt.cm.hsv(np.linspace(0.4, 0, len(top10_rented_movies)))  
    # 0.3 in HSV ~ green; spread colors until red/purple
    plt.bar(top10_rented_movies['film_title'], top10_rented_movies['rental_count'], color=colors)
    plt.xticks(rotation=45)
    plt.xlabel("Film Title")
    plt.ylabel("Number of Rentals")
    plt.title("Top 10 Most Rented Movies")
    st.pyplot(plt)
    st.write("The bar chart above shows the top 10 most rented movies from the dvdrental database. The colors are generated using the HSV colormap to ensure distinctiveness.")

elif menu == "Top_spenders_rentals":
    st.header("Top 15 Customers Who Spent the Most on Rentals Analysis")
    #Which customers spend the most money on rentals?
    Top_spenders_rentals = pd.read_sql("""
    SELECT
        first_name||' '||last_name AS Customer_name,
        email,
        SUM(amount) AS Total_spent
    FROM
        payment
    Join
        customer ON payment.customer_id = customer.customer_id
    GROUP BY
        Customer_name,
        email
    ORDER BY
        Total_spent DESC LIMIT 15;""", engine)
    Top_spenders_rentals.index = Top_spenders_rentals.index + 1
    Top_spenders_rentals.index.name = "Rank"
    st.sidebar.header("Top 15 Customers Who Spent the Most on Rentals")
    most_spent = st.sidebar.slider("Select the number of top spenders to display:", min_value=5, max_value=len(Top_spenders_rentals), value=5, step=5)
    st.sidebar.write(f"Displaying the top {most_spent} customers who spent the most on rentals.")
    Top_spenders_rentals = Top_spenders_rentals.head(most_spent)
    st.subheader("Top 15 Customers Who Spent the Most on Rentals")
    st.write(Top_spenders_rentals)

    # Pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        Top_spenders_rentals['Total_spent'],
        labels=Top_spenders_rentals['customer_name'],
        autopct=lambda pct: f"{pct:.1f}%\n(${pct*Top_spenders_rentals['total_spent'].sum()/100:.2f})",  
        startangle=140,
        colors=plt.cm.tab20.colors  # nice distinct colors
    )
    plt.title("Top Customers by Total Spending on Rentals", fontsize=14)
    plt.tight_layout()

    # Show in Streamlit
    st.pyplot(plt)

elif menu == "Category_revenue":
    st.header("Top 5 Film Categories by Revenue Analysis")
    #Which film categories generate the most revenue?
    st.sidebar.header("Top 5 Film Categories by Revenue")
    st.subheader("Top 5 Film Categories by Revenue")
    Category_revenue = pd.read_sql("""
    SELECT
        name AS Movie_category,
        SUM(amount) as Total_Revenue
    FROM payment
    JOIN
        rental on payment.rental_id = rental.rental_id
    JOIN 
        inventory on rental.inventory_id = inventory.inventory_id
    JOIN
        film_category on inventory.film_id = film_category.film_id
    JOIN
        category on film_category.category_id = category.category_id
    GROUP BY
        Movie_category
    ORDER BY
        Total_Revenue DESC LIMIT 5;""", engine)
    Category_revenue.index = Category_revenue.index + 1
    Category_revenue.index.name = "Rank"
    st.write(Category_revenue)

    #bar chart of film categories by revenue
    st.subheader("Bar Chart of Top 5 Film Categories by Revenue")
    plt.figure(figsize=(8,5))
    plt.bar(Category_revenue['Movie_category'], Category_revenue['total_revenue'], color=plt.cm.Paired.colors)
    plt.xlabel("Movie Category")
    plt.ylabel("Total Revenue ($)")
    plt.title("Top 5 Film Categories by Revenue")
    plt.xticks(rotation=45)
    st.pyplot(plt)
    st.write("The bar chart above shows the top 5 film categories that generate the most revenue from the dvdrental database.")

elif menu == "Busiest_rental_days":
    st.header("Busiest Rental Periods Analysis by Day of the Week")
    #What are the busiest rental periods (by day, month, or hour)?
    st.sidebar.header("Busiest Rental Periods (Day, Month and Hour)")
    st.subheader("Busiest Rental Periods by Day of the Week")
    Busiest_rental_days = pd.read_sql("""
    SELECT 
        TO_CHAR(rental_date, 'Day') AS day_of_week,
        COUNT(rental_id) AS rental_count
    FROM rental
    GROUP BY day_of_week
    ORDER BY rental_count DESC;""", engine)
    # Clean up day_of_week to remove extra spaces
    Busiest_rental_days['day_of_week'] = Busiest_rental_days['day_of_week'].str.strip()
    st.write(Busiest_rental_days)

    #Line chart of busiest rental periods by day of the week
    st.subheader("Line Chart of Busiest Rental Periods by Day of the Week")
    plt.figure(figsize=(10,5))
    plt.plot(Busiest_rental_days['day_of_week'], Busiest_rental_days['rental_count'], marker='o', color='b')
    plt.xlabel("Day of the Week")
    plt.ylabel("Number of Rentals")
    plt.title("Busiest Rental Periods by Day of the Week")
    plt.grid()
    st.pyplot(plt)
    st.write("The line chart above shows the busiest rental periods by day of the week from the dvdrental database.")

elif menu == "Busiest_rental_month":
    st.header("Busiest Rental Periods Analysis by Month")
    #What are the busiest rental periods (by day, month, or hour)?
    st.sidebar.header("Busiest Rental Periods (Day, Month and Hour)")
    st.subheader("Busiest rental Month")
    Busiest_rental_month = pd.read_sql("""
    SELECT 
        TO_CHAR(rental_date, 'Month') AS rental_month,
        COUNT(rental_id) AS rental_count
    FROM rental
    GROUP BY rental_month
    ORDER BY rental_count DESC;""",engine)
    #Busiest_rental_month['Month'] = Busiest_rental_month['Month'].str.strip()
    st.write(Busiest_rental_month)

    #Line chart of busiest rental periods by month
    st.subheader("Line Chart of Busiest Rental Periods by Month")
    plt.figure(figsize=(10,5))
    plt.plot(Busiest_rental_month['rental_month'], Busiest_rental_month['rental_count'], marker='o', color='g')
    plt.xlabel("Month")
    plt.ylabel("Number of Rentals")
    plt.title("Busiest Rental Periods by Month")
    plt.grid()
    st.pyplot(plt)
    st.write("The line chart above shows the busiest rental periods by month from the dvdrental database.")

elif menu == "Busiest_rental_hour":
    st.header("Busiest Rental Periods Analysis by Hour of the Day")
    #What are the busiest rental periods (by day, month, or hour)?
    st.sidebar.header("Busiest Rental Periods (Day, Month and Hour)")
    st.subheader("Busiest rental Hour")
    Busiest_rental_hour = pd.read_sql("""
    SELECT 
        EXTRACT(HOUR FROM rental_date) AS rental_hour,
        COUNT(rental_id) AS rental_count
    FROM rental
    GROUP BY rental_hour
    ORDER BY rental_count DESC;""", engine)
    Busiest_rental_hour['rental_hour'] = Busiest_rental_hour['rental_hour'].astype(int)
    st.write(Busiest_rental_hour)

    #Line chart of busiest rental periods by hour
    st.subheader("Line Chart of Busiest Rental Periods by Hour")
    plt.figure(figsize=(10,5))
    plt.plot(Busiest_rental_hour['rental_hour'], Busiest_rental_hour['rental_count'], marker='o', color='r')
    plt.xlabel("Hour of the Day")
    plt.ylabel("Number of Rentals")
    plt.title("Busiest Rental Periods by Hour")
    plt.grid()
    st.pyplot(plt)
    st.write("The line chart above shows the busiest rental periods by hour from the dvdrental database.")

#Which stores perform better in terms of rentals and revenue?
#in terns of of rentals
elif menu == "Store_rentals":
    st.header("Store Performance Analysis in Terms of Rentals")
    st.sidebar.header("Store Performance Analysis in Terms of Rentals")
    st.subheader("Store Performance in Terms of Number of Rentals")
    Store_rentals = pd.read_sql("""
    SELECT
        staff.email,
        store.store_id,
        COUNT(rental.rental_id) AS Total_rental
    FROM
        store
    LEFT JOIN 
        staff ON staff.store_id = store.store_id
    LEFT JOIN
        rental ON staff.staff_id = rental.staff_id
    GROUP BY
        staff.email,
        store.store_id
    ORDER BY
        Total_rental DESC;
    """, engine)
    Store_rentals.index = Store_rentals.index + 1
    Store_rentals.index.name = "Rank"
    st.write(Store_rentals)

    st.subheader("Bar Chart of Store Performance in Terms of Number of Rentals")
    fig, ax = plt.subplots(figsize=(6,4))  # smaller, tighter chart
    bars = ax.bar(
        Store_rentals['store_id'].astype(str), 
        Store_rentals['total_rental'], 
        color=plt.cm.Set2.colors,
        width=0.4,   # <--- controls slimness of bars
        edgecolor="black",  # adds a clean outline
        linewidth=1
    )

    # Add labels above bars for clarity
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 50,   # adjust +50 for spacing
                f"{height:,}", ha='center', va='bottom', fontsize=9)

    # Titles and labels
    ax.set_xlabel("Store ID", fontsize=11, weight="bold")
    ax.set_ylabel("Total Rentals", fontsize=11, weight="bold")
    ax.set_title("Store Performance in Terms of Number of Rentals", fontsize=12, weight="bold")

    # Remove top and right spines (clean look)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
    st.write("The bar chart above shows the performance of each store in terms of the number of rentals from the dvdrental database.")

#in terms of revenue
elif menu == "Store_revenue":
    st.header("Store Performance Analysis in Terms of Revenue")
    st.sidebar.header("Store Performance Analysis in Terms of Revenue")
    st.subheader("Store Performance in Terms of Revenue")
    Store_revenue = pd.read_sql("""
    SELECT
        staff.email,
        store.store_id,
        SUM(payment.amount) AS Total_revenue
    FROM
        store	
    LEFT JOIN
        staff ON staff.store_id = store.store_id
    LEFT JOIN
        rental ON staff.staff_id = rental.staff_id
    LEFT JOIN
        payment ON rental.rental_id = payment.rental_id
    GROUP BY
        staff.email,
        store.store_id
    ORDER BY
        Total_revenue DESC;""", engine)
    Store_revenue.index = Store_revenue.index + 1
    Store_revenue.index.name = "Rank"
    st.write(Store_revenue)
    #bar chart of store performance in terms of revenue
    st.subheader("Bar Chart of Store Performance in Terms of Revenue")
    fig, ax = plt.subplots(figsize=(6,4))  # smaller, tighter chart
    bars = ax.bar(
        Store_revenue['store_id'].astype(str), 
        Store_revenue['total_revenue'], 
        color=plt.cm.Set3.colors,
        width=0.4,   # <--- controls slimness of bars
        edgecolor="black",  # adds a clean outline
        linewidth=1
    )
    # Add labels above bars for clarity
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 50,   # adjust +50 for spacing
                f"${height:,.2f}", ha='center', va='bottom', fontsize=9)
    # Titles and labels
    ax.set_xlabel("Store ID", fontsize=11, weight="bold")
    ax.set_ylabel("Total Revenue ($)", fontsize=11, weight="bold")
    ax.set_title("Store Performance in Terms of Revenue", fontsize=12, weight="bold")
    # Remove top and right spines (clean look)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
    st.write("The bar chart above shows the performance of each store in terms of revenue from the dvdrental database.")
elif menu == "Summary":
    st.header("Summary of Findings with Recommendations")

    st.markdown("""
    ### Top 10 Most Rented Movies
    - Bucket Brotherhood, Rocketeer Mother, Juggler Hardly, Ridgemont Submarine, Grit Clockwork, Forward Temple, Scalawag Duck, Apache Divine, Goodfellas Salute, and Rush Goodfellas.  
    **Finding:** These titles dominate rentals, reflecting strong customer preferences for certain genres and themes.  
    **Recommendation:** Stock more copies of these popular films, and promote related titles (similar actors, genres) to boost rentals further.

    ---

    ###Top 15 Customers by Spending
    - Eleanor Hunt (*eleanor.hunt@sakilacustomer.org*) is the top spender with **$211.55**.  
    **Finding:** A small group of loyal customers contributes a significant share of revenue.  
    **Recommendation:** Introduce loyalty programs, exclusive offers, or early access for these high-value customers to retain and grow their spending.

    ---

    ### Film Categories by Revenue
    | Category   | Revenue ($) |
    |------------|-------------|
    | Sports     | 4,892.19    |
    | Animation  | 4,245.31    |
    | Sci-Fi     | 4,336.01    |
    | Drama      | 4,118.46    |
    | Comedy     | 4,002.48    |

    **Finding:** Sports generates the highest revenue, while Animation and Sci-Fi also perform strongly.  
    **Recommendation:** Market campaigns should highlight these top-performing categories, while underperforming categories could either be improved with better promotion or scaled back.

    ---

    ### Busiest Rental Periods
    **By Day** – Tuesday is the busiest (2463 rentals), followed by Sunday and Saturday.  
    **Finding:** Midweek and weekend activity peaks suggest customers rent before leisure time.  
    **Recommendation:** Add staffing and promotional deals on Tuesdays/weekends to maximize efficiency and sales.

    **By Month** – July (6709 rentals) and August (5686) dominate.  
    **Finding:** Peak rentals occur during summer months, possibly linked to holidays and free time.  
    **Recommendation:** Prepare seasonal promotions (discount bundles, family packages) in advance of peak months.

    **By Hour** – Rentals peak at 3 PM (887), followed by early mornings and evenings.  
    **Finding:** Activity is spread, but afternoons show the highest demand.  
    **Recommendation:** Ensure system/server reliability and customer support during peak hours.

    ---

    ###Store Performance (Rentals)
    | Staff Email                    | Store ID | Total Rentals |
    |--------------------------------|----------|---------------|
    | Mike.Hillyer@sakilastaff.com   | 1        | 8040          |
    | Jon.Stephens@sakilastaff.com   | 2        | 8004          |

    **Finding:** Both stores perform nearly equally in rentals, with Store 1 slightly ahead.  
    **Recommendation:** Benchmark the strategies of Store 1 and apply successful practices across both to maintain balance.

    ---

    ###Store Performance (Revenue)
    | Staff Email                    | Store ID | Total Revenue |
    |--------------------------------|----------|---------------|
    | Jon.Stephens@sakilastaff.com   | 2        | 30,813.33     |
    | Mike.Hillyer@sakilastaff.com   | 1        | 30,498.71     |

    **Finding:** Store 2 edges out in revenue, though the margin is small.  
    **Recommendation:** Explore what drives higher revenue at Store 2 (e.g., pricing, upselling, local demand) and replicate in Store 1.

    ---
    """)

st.success("💡 These insights reveal customer preferences, revenue drivers, and operational patterns. By acting on these findings, management can improve efficiency, target loyal customers, and maximize profitability.")
st.sidebar.success("Thank you for using the app! Feel free to explore and interact with the data.")
st.balloons()
st.write("Developed by Edisun - Data Enthusiast")
