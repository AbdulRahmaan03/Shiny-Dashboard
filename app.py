import plotly.express as px
from shiny.express import render, input, ui
from shinywidgets import render_plotly
from pathlib import Path
from shiny import reactive
import pandas as pd
import calendar

ui.page_opts(title="Shiny Project", fillable=False)

# ui.input_checkbox("bar_color", "Make Bars Red?", False)


@reactive.calc
def color():
    return "red" if input.bar_color() else "blue"


@reactive.calc
def dat():
    infile = Path(__file__).parent / "sales.csv"
    df = pd.read_csv(infile)
    df["order_date_1"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date_1"].dt.month_name()
    df['value'] = df['quantity_ordered'] * df['price_each']
    return df


with ui.card():  
    ui.card_header("Sales by city in 2023")

    with ui.layout_sidebar():  
        with ui.sidebar(bg="#f8f8f8", open='open'):  
            ui.input_selectize(
                                    "city",
                                    "Select a City:",
                                    [
                                        "Dallas (TX)",
                                        "Boston (MA)",
                                        "Los Angeles (CA)",
                                        "San Francisco (CA)",
                                        "Seattle (WA)",
                                        "Atlanta (GA)",
                                        "New York City (NY)",
                                        "Portland (OR)",
                                        "Austin (TX)",
                                        "Portland (ME)",
                                    ],
                                    multiple=False,
                                    selected="Boston (MA)",
                                ) 
            


        @render_plotly
        def sample_over_time():
            # print(input.city())
            df = dat()
            # print(list(df['city'].unique()))
            sales = df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
            sales_by_city = sales[sales["city"] == input.city()]
            month_orders = calendar.month_name[1:]
            fig = px.bar(
                sales_by_city,
                x="month",
                y="quantity_ordered",
                title=f"Sales over Time -- {input.city()}",
                category_orders={"month": month_orders},
            )
            # fig.update_traces(marker_color=color())
            return fig

with ui.layout_column_wrap(width=1/2):
    with ui.navset_card_underline(id="tab", footer=ui.input_numeric("n", "Number of Products", 5, min=1, max=20)):  
        with ui.nav_panel("Top Sellers"):

            @render_plotly
            def plot_top_sellers():
                df = dat()
                top_sales = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nlargest(input.n())
                    .reset_index()
                )
                fig = px.bar(top_sales, x="product", y="quantity_ordered")
                # fig.update_traces(marker_color=color())
                return fig

        with ui.nav_panel("Top Sellers value ($)"):
            
            @render_plotly
            def plot_top_sellers_value():
                df = dat()
                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nlargest(input.n())
                    .reset_index()
                )
                fig = px.bar(top_sales, x="product", y="value")
                # fig.update_traces(marker_color=color())
                return fig

        with ui.nav_panel("Lowest Sellers"):
            @render_plotly
            def plot_bottom_sellers():
                df = dat()
                top_sales = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                fig = px.bar(top_sales, x="product", y="quantity_ordered")
                # fig.update_traces(marker_color=color())
                return fig

        with ui.nav_panel("Lowest Sellers Values ($)"):
            @render_plotly
            def plot_bottom_sellers_value():
                df = dat()
                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                fig = px.bar(top_sales, x="product", y="value")
                # fig.update_traces(marker_color=color())
                return fig

    with ui.card():
        ui.card_header("Sales by Time of Day Heatmap")
        "Heatmap"


with ui.card():
    ui.card_header("Sales by Location Map")
    "Placeholder"
    


with ui.card():
    ui.card_header("Sample Sales Data")

    @render.data_frame
    def sample_sales_data():
        return dat().head(1000)


# rsconnect add \
# 	  --account abdul-rahmaan \
# 	  --name abdul-rahmaan \
# 	  --token E9AB35D2519BC241ED5DF195C3DD7C3A \
# 	  --secret ASwKt5uQF/JSLGKCp4cyHaEEG6oEXO1rwt1s284k

# rsconnect deploy shiny ./ --name abdul-rahmaan --title sales-tut  
# rsconnect deploy shiny sales/data/ --name abdul-rahmaan --title sales-tut