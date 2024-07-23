import plotly.express as px
from shiny.express import render, input, ui
from shinywidgets import render_plotly, render_altair, render_widget
from pathlib import Path
from shiny import reactive
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import altair as alt
import folium
from folium.plugins import HeatMap


# ui.head_content(
ui.tags.link(rel="shotcut icon", href=r"C:\Users\USER\Downloads\shiny-python-projects\assets\shiny-logo.png", type="x-icon"),
    # )

ui.tags.style(
    """
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center; /* Centers the content horizontally */
        height: 60px;
    }

    .title-container h2 {
        color: white;
        padding: 5px;
        margin: 0;
    }

    body {
        background-color: #438364;
    }

    .modebar{
        display: none;
    }
    """
)

FONT_COLOR = "#30913a"
FONT_TYPE = "Arial"


def style_plotly_pie_chart(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",  # Remove background color
        showlegend=True,  # Show the legend for pie chart
        legend=dict(
            orientation="h",  # Set the legend to be horizontal
            x=0.5,
            y=-0.1,
            xanchor="center",
            yanchor="bottom",
            bgcolor="rgba(255,255,255,0.5)",  # Optional: Add background color to legend
            font=dict(color="black"),  # Set legend text color to black
        ),
        font=dict(family="Arial", size=12, color=FONT_COLOR),
    )
    fig.update_traces(
        domain=dict(
            x=[0, 1], y=[0.1, 1]
        )  # Adjust position of the pie chart within the plot
    )
    return fig


ui.page_opts(
    window_title="Sales Dashboard",
    # title="Sales Dashboard for Electronics Store",
    fillable=False,
)

@reactive.calc
def dat():
    infile = Path(__file__).parent / "sales.csv"
    df = pd.read_csv(infile)
    df["time_stamp"] = pd.to_datetime(df["order_date"])
    df.rename(columns={"price_each": "unit_price"}, inplace=True)
    df["month"] = df["time_stamp"].dt.month_name()
    df["hour"] = df["time_stamp"].dt.hour
    df["value"] = df["quantity_ordered"] * df["unit_price"]
    return df


with ui.div(class_="header-container"):
    with ui.div(class_="title-container"):
        ui.h2("Sales Dashboard for Electronics Store")

with ui.card():
    ui.card_header("Sales by City 2023")

    with ui.layout_sidebar():
        with ui.sidebar(bg="#f8f8f8", open="open"):
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

        @render_widget
        def sales_over_time_altair():
            df = dat()
            # Group the data by city and month, then sum the quantities ordered
            sales = (
                df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
            )

            # Filter the sales data to only include the selected city
            sales_by_city = sales[sales["city"] == input.city()]

            # Define the order of months
            month_orders = list(calendar.month_name)[1:]

            font_props = alt.Axis(
                labelFont="Arial",
                labelColor="black",
                titleFont="Arial",
                titleColor=FONT_COLOR,
                tickSize=0,
                labelAngle=0,
            )
            # Create the bar chart
            chart = (
                alt.Chart(sales_by_city)
                .mark_bar(color="#30913a")
                .encode(
                    x=alt.X("month", sort=month_orders, title="Month", axis=font_props),
                    y=alt.Y(
                        "quantity_ordered", title="Quantity Ordered", axis=font_props
                    ),
                    tooltip=["month", "quantity_ordered"],
                )
                .properties(title=alt.Title(f"Sales over Time -- {input.city()}"))
                .configure_axis(grid=False)
                .configure_title(font="Arial", color=FONT_COLOR)
            )

            return chart


with ui.layout_column_wrap(width=1 / 2):
    with ui.navset_card_underline(
        id="tab", footer=ui.input_numeric("n", "Number of Items", 5, min=0, max=20)
    ):
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

                # Create the pie chart
                fig = px.pie(
                    top_sales,
                    names="product",
                    values="quantity_ordered",
                    color="quantity_ordered",
                    color_discrete_sequence=px.colors.sequential.Greens,
                )

                # Apply the standardized style
                fig = style_plotly_pie_chart(fig)

                return fig

        with ui.nav_panel("Top Sellers Value ($)"):

            @render_plotly
            def plot_top_sellers_value():
                df = dat()
                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nlargest(input.n())
                    .reset_index()
                )
                # Create the pie chart
                fig = px.pie(
                    top_sales,
                    names="product",
                    values="value",
                    color="value",
                    color_discrete_sequence=px.colors.sequential.Greens,
                )

                # Apply the standardized style
                fig = style_plotly_pie_chart(fig)

                return fig

        with ui.nav_panel("Lowest Sellers"):

            @render_plotly
            def plot_lowest_sellers():
                df = dat()
                top_sales = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                # Create the pie chart
                fig = px.pie(
                    top_sales,
                    names="product",
                    values="quantity_ordered",
                )
                red_gradient = [
                    "#FFEBEE",  # Light red
                    "#FFCDD2",
                    "#EF9A9A",
                    "#E57373",
                    "#EF5350",  # Medium red
                    "#F44336",
                    "#D32F2F",  # Dark red
                ]
                # Apply the custom color scale
                fig.update_traces(marker=dict(colors=red_gradient))
                # Apply the standardized style
                fig = style_plotly_pie_chart(fig)

                return fig

        with ui.nav_panel("Lowest Sellers Value ($)"):

            @render_plotly
            def plot_lowest_sellers_value():
                df = dat()
                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                red_gradient = [
                    "#FFEBEE",  # Light red
                    "#FFCDD2",
                    "#EF9A9A",
                    "#E57373",
                    "#EF5350",  # Medium red
                    "#F44336",
                    "#D32F2F",  # Dark red
                ]
                # Create the pie chart
                fig = px.pie(
                    top_sales,
                    names="product",
                    values="value",
                )

                # Apply the custom color scale
                fig.update_traces(marker=dict(colors=red_gradient))
                # Apply the standardized style
                fig = style_plotly_pie_chart(fig)

                return fig

    with ui.card():
        ui.card_header("Sales by Time of Day Heatmap")

        @render.plot
        def plot_sales_by_time():
            df = dat()
            sales_by_hour = (
                df["hour"].value_counts().reindex(np.arange(0, 24), fill_value=0)
            )

            heatmap_data = sales_by_hour.values.reshape(24, 1)
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt="d",
                cmap="Greens",
                cbar=False,
                xticklabels=[],
                yticklabels=[f"{i}:00" for i in range(24)],
            )

            # plt.title("Number of Orders by Hour of Day")
            plt.xlabel("Order Count", color=FONT_COLOR, fontname=FONT_TYPE)
            plt.ylabel("Hour of Day", color=FONT_COLOR, fontname=FONT_TYPE)

            # Change the tick label color and font
            plt.yticks(color="black", fontname=FONT_TYPE)
            # plt.xticks(color=FONT_COLOR, fontname=FONT_TYPE)


with ui.card():
    ui.card_header("Sales by Location Map")

    @render.ui
    def plot_us_heatmap():
        df = dat()

        heatmap_data = df[["lat", "long", "quantity_ordered"]].values

        map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
        green_gradient = {
            0.0: "#E8F5E9",  # Light green
            0.2: "#C8E6C9",
            0.4: "#81C784",
            0.6: "#66BB6A",
            0.8: "#4CAF50",  # Medium green
            1.0: "#388E3C",  # Dark green
        }

        # Add the heatmap layer with the blue gradient
        HeatMap(heatmap_data, gradient=green_gradient).add_to(map)

        return map


with ui.card():
    ui.card_header("Sample Sales Data")

    @render.data_frame
    def sample_sales_data():
        return render.DataGrid(dat().head(1000), selection_mode="row", filters=True)
