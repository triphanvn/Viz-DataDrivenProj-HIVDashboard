from shiny import App, render, ui, reactive
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from shinywidgets import output_widget, render_widget

###############################################################################
# Load datasets
df_deaths_new_cases = pd.read_csv("data/deaths-and-new-cases-of-hiv.csv")
df_art_24 = pd.read_csv("data/antiretroviral-therapy-coverage.csv")
df_art = pd.read_csv("data/antiretroviral-therapy-coverage-among-people-living-with-hiv.csv")

df_children_newly_infected = pd.read_csv("data/children-newly-infected-with-hiv.csv")
df_adult_newly_infected = pd.read_csv("data/adults-newly-infected-with-hiv.csv")

df_prevalence_male = pd.read_csv("data/prevalence-of-hiv-male-teenager.csv")
df_prevalence_female = pd.read_csv("data/prevalence-of-hiv-female-teenager.csv")

###############################################################################
# Preprocessing
# Deaths and new cases dataset
df_deaths_new_cases = df_deaths_new_cases[df_deaths_new_cases['Code'].notna()]
df_deaths_new_cases = df_deaths_new_cases.rename(columns={
    'Entity': 'Country',
    'Incidence - HIV/AIDS - Sex: Both - Age: All Ages (Number)': 'New Cases',
    'Deaths - HIV/AIDS - Sex: Both - Age: All Ages (Number)': 'Deaths',
})
df_deaths_new_cases = df_deaths_new_cases.drop(columns=['Prevalence - HIV/AIDS - Sex: Both - Age: All Ages (Number)'])

# ART dataset
df_art = df_art[df_art['Code'].notna()]
df_art = df_art.rename(columns={
    'Entity': 'Country',
    'Antiretroviral therapy coverage (% of people living with HIV)': 'ART',
})

# Merge data set for part 1
df_deaths_new_cases = df_deaths_new_cases.merge(
    df_art[['Country', 'Code', 'Year', 'ART']],
    on=['Country', 'Code', 'Year'],
    how='left'
)

# Fill missing ART values with 0
df_deaths_new_cases['ART'] = df_deaths_new_cases['ART'].fillna(0)

# Prevalence of HIV by gender
df_prevalence_male = df_prevalence_male[df_prevalence_male['Country Code'].notna()]
df_prevalence_male = df_prevalence_male.rename(columns={
    'Country Name': 'Country',
    'Country Code': 'Code',
})
df_prevalence_male = df_prevalence_male.drop(columns=['Indicator Name', 'Indicator Code'])

df_prevalence_female = df_prevalence_female[df_prevalence_female['Country Code'].notna()]
df_prevalence_female = df_prevalence_female.rename(columns={
    'Country Name': 'Country',
    'Country Code': 'Code',
})
df_prevalence_female = df_prevalence_female.drop(columns=['Indicator Name', 'Indicator Code'])

# Reshape the datasets (Prevalence of HIV female/male teenager)
## Male
df_prevalence_male_reshaped = df_prevalence_male.melt(
    id_vars=['Country', 'Code'], var_name='Year', value_name='Prevalence_male'
)
df_prevalence_male_reshaped = df_prevalence_male_reshaped[df_prevalence_male_reshaped['Year'].str.isnumeric()]
df_prevalence_male_reshaped['Year'] = df_prevalence_male_reshaped['Year'].astype(int)
df_prevalence_male_reshaped = df_prevalence_male_reshaped.dropna(subset=['Prevalence_male'])
## Female
df_prevalence_female_reshaped = df_prevalence_female.melt(
    id_vars=['Country', 'Code'], var_name='Year', value_name='Prevalence_female'
)
df_prevalence_female_reshaped = df_prevalence_female_reshaped[df_prevalence_female_reshaped['Year'].str.isnumeric()]
df_prevalence_female_reshaped['Year'] = df_prevalence_female_reshaped['Year'].astype(int)
df_prevalence_female_reshaped = df_prevalence_female_reshaped.dropna(subset=['Prevalence_female'])

# children/adult newly infected with hiv
df_children_newly_infected = df_children_newly_infected[df_children_newly_infected['Country Code'].notna()]
df_children_newly_infected = df_children_newly_infected.rename(columns={
    'Country Name': 'Country',
    'Country Code': 'Code',
    'children_newly_infected': 'Children'
})
df_children_newly_infected = df_children_newly_infected.drop(columns=['Indicator Name', 'Indicator Code'])

df_adult_newly_infected = df_adult_newly_infected[df_adult_newly_infected['Country Code'].notna()]
df_adult_newly_infected = df_adult_newly_infected.rename(columns={
    'Country Name': 'Country',
    'Country Code': 'Code',
    'adult_newly_infected': 'Adult'
})
df_adult_newly_infected = df_adult_newly_infected.drop(columns=['Indicator Name', 'Indicator Code'])

# Reshape the datasets (children-newly-infected-with-hiv, adults-newly-infected-with-hiv)
# For children newly infected
df_children_newly_infected_reshaped = df_children_newly_infected.melt(
    id_vars=['Country', 'Code'], var_name='Year', value_name='Children'
)

df_children_newly_infected_reshaped = df_children_newly_infected_reshaped[
    df_children_newly_infected_reshaped['Year'].str.isnumeric()
]
df_children_newly_infected_reshaped['Year'] = df_children_newly_infected_reshaped['Year'].astype(int)
df_children_newly_infected_reshaped = df_children_newly_infected_reshaped.dropna(subset=['Children'])

# For adult newly infected
df_adult_newly_infected_reshaped = df_adult_newly_infected.melt(
    id_vars=['Country', 'Code'], var_name='Year', value_name='Adult'
)
df_adult_newly_infected_reshaped = df_adult_newly_infected_reshaped[
    df_adult_newly_infected_reshaped['Year'].str.isnumeric()
]
df_adult_newly_infected_reshaped['Year'] = df_adult_newly_infected_reshaped['Year'].astype(int)
df_adult_newly_infected_reshaped = df_adult_newly_infected_reshaped.dropna(subset=['Adult'])

# List all countries, years
countries = sorted(df_deaths_new_cases['Country'].unique())

years_scatter = sorted(df_prevalence_male_reshaped['Year'].unique())
years_scatter = [str(year) for year in years_scatter]

countries_list = sorted(df_prevalence_male_reshaped['Country'].unique())

years_children = df_children_newly_infected_reshaped['Year'].unique()
years_adult = df_adult_newly_infected_reshaped['Year'].unique()
available_years = sorted(set(years_children).union(years_adult))

# ###############################################################################
# UI layout
app_ui = ui.page_fluid(
    ui.TagList(
        ui.panel_title("", "HIV Dashboard"),
        ui.h2(
            "🧪 HIV Dashboard",
            style="color:#800000; font-family:monospace; background-color:#fff3cd; padding:10px; border-radius:8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);"
        )
    ),

    ui.div(style="margin-top: 20px;"),
    
    ui.panel_well(
        ui.h4("HIV in the specific country"),
        ui.input_select("country", "Country", choices=countries, selected="Vietnam"),
        ui.output_ui("summary_cards"),
    
        ui.hr(),

        ui.layout_columns(
            # Group 1: New Cases
            ui.div(
                ui.h5("New HIV Cases Over Time"),
                ui.output_plot("new_cases_line"),
                # output_widget("new_cases_line"),
                ui.input_slider("new_cases_years", "Select Year Range",
                    min=df_deaths_new_cases['Year'].min(),
                    max=df_deaths_new_cases['Year'].max(),
                    value=(df_deaths_new_cases['Year'].min(), df_deaths_new_cases['Year'].max()),
                    step=1,
                    sep="",
                    width="100%"),
            ),
            # Group 2: Deaths
            ui.div(
                ui.h5("HIV-related Deaths Over Time"),
                ui.output_plot("deaths_line"),
                # output_widget("deaths_line"),
                ui.input_slider("deaths_years", "Select Year Range",
                    min=df_deaths_new_cases['Year'].min(),
                    max=df_deaths_new_cases['Year'].max(),
                    value=(df_deaths_new_cases['Year'].min(), df_deaths_new_cases['Year'].max()),
                    step=1,
                    sep="",
                    width="100%"),
            ),
            # Group 3: ART Coverage
            ui.div(
                ui.h5("ART Coverage Over Time"),
                # output_widget("art_coverage_line"),
                ui.output_plot("art_coverage_line"),
                ui.input_slider("art_years", "Select Year Range",
                    min=df_deaths_new_cases['Year'].min(),
                    max=df_deaths_new_cases['Year'].max(),
                    value=(df_deaths_new_cases['Year'].min(), df_deaths_new_cases['Year'].max()),
                    step=1,
                    sep="",
                    width="100%"),
            ),
        ),
        ui.p(
            "The data is sourced from the UNICEF Data Warehouse",
            style="font-size: 0.9em; color: #555; margin-top: 20px;"
        )
    ),

    ui.div(style="margin-top: 20px;"),

    ui.panel_well(
        ui.h4("Prevalence of HIV by gender (teenager)"),
        ui.layout_columns(
            # Column 1 (1 portion): Both selectors stacked vertically in one card
            ui.card(
                # ui.input_select("year", "Year", choices=years_scatter, selected="2019"),
                ui.input_slider(
                    "year",
                    "Year (Animation supported)",
                    min=min(years_scatter),
                    max=max(years_scatter),
                    value=1990,
                    step=1,
                    sep="",
                    width="100%",
                    animate={"interval": 2000, "loop": False}
                ),
                ui.input_select("country_scatter", "Highlight Country", choices=countries_list, selected="Viet Nam"),
                style="width: 100%"
            ),
            # Column 2 (2 portions): Scatter plot output
            ui.card(
                ui.output_plot("gender_scatter"),
                # output_widget("gender_scatter"),
                style="width: 100%"
            ),
            col_widths=[4, 8],
        ),
        ui.p(
            "The data is sourced from the UNICEF Data Warehouse",
            style="font-size: 0.9em; color: #555; margin-top: 20px;"
        )
    ),

    ui.div(style="margin-top: 20px;"),

    ui.panel_well(
        ui.h4("HIV distribution across countries"),
        ui.row(
            ui.column(
                8,
                output_widget("geo_map"),
                ui.input_slider(
                    "year_slider",
                    "Select Year",
                    min=min(available_years),
                    max=max(available_years),
                    value=max(available_years),
                    step=1,
                    sep="",
                    width="100%",
                )
            ),
            ui.column(
                4,
                ui.h5("Select the dataset"),
                ui.div(
                    ui.value_box("Newly infected with HIV", "Children (ages 0-14)", color="blue"),
                    onclick="Shiny.setInputValue('dataset_type', 'children', {priority: 'event'})",
                    style="cursor: pointer; margin-bottom: 10px;"
                ),
                
                ui.div(
                    ui.value_box("Newly infected with HIV", "Adults (ages 15-49)", color="green"),
                    onclick="Shiny.setInputValue('dataset_type', 'adult', {priority: 'event'})",
                    style="cursor: pointer;"
                ),

                ui.hr()
            ),
        ),
        ui.p(
            "The data is sourced from the World Bank Open Data",
            style="font-size: 0.9em; color: #555; margin-top: 20px;"
        )
    ),
    ui.p(
        "@Phan Minh Tri, 2025",
        style="font-size: 0.9em; color: #555; margin-top: 20px;"
    )
)
import plotly.io as pio
###############################################################################
# Server logic
def server(input, output, session):
    @reactive.Calc
    def selected_country_data():
        return input.country()

    @output
    @render.ui
    def summary_cards():
        df = df_deaths_new_cases[df_deaths_new_cases["Country"] == selected_country_data()]
        latest = df[df["Year"] == df["Year"].max()]
        year = latest["Year"].values[0]
        new_cases = int(latest["New Cases"].values[0])
        deaths = int(latest["Deaths"].values[0])
        coverage = int(latest["ART"].values[0])

        return ui.layout_column_wrap(
            ui.value_box(
                title="New HIV Cases",
                value=f"{new_cases:,} cases | {year}",
                theme="danger"
            ),
            ui.value_box(
                title="HIV-related Deaths",
                value=f"{deaths:,} cases | {year}",
                theme="secondary"
            ),
            ui.value_box(
                title="ART Coverage",
                value=f"{coverage}% | {year}",
                theme="success"
            ),
        )

    @output
    @render.plot
    def new_cases_line():
        df = df_deaths_new_cases[df_deaths_new_cases["Country"] == selected_country_data()]
        year_range = input.new_cases_years()
        df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

        fig, ax = plt.subplots()
        ax.plot(df["Year"], df["New Cases"], marker='o', linestyle='-', color='#dc3545')
        ax.set_xlabel("Year")
        ax.set_ylabel("New Cases")
        ax.grid(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        return fig

    @render.plot
    def deaths_line():
        df = df_deaths_new_cases[df_deaths_new_cases["Country"] == selected_country_data()]
        year_range = input.deaths_years()
        df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

        fig, ax = plt.subplots()
        ax.plot(df["Year"], df["Deaths"], marker='o', linestyle='-', color='#6c757d')
        ax.set_xlabel("Year")
        ax.set_ylabel("Deaths")
        ax.grid(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        return fig

    @render.plot
    def art_coverage_line():
        df = df_deaths_new_cases[df_deaths_new_cases["Country"] == selected_country_data()]
        year_range = input.art_years()
        df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

        fig, ax = plt.subplots()
        ax.plot(df["Year"], df["ART"], marker='o', linestyle='-', color='#28a745')
        ax.set_xlabel("Year")
        ax.set_ylabel("ART (%)")
        ax.grid(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        return fig
    
    @output
    @render.plot
    def gender_scatter():
        year = int(input.year())
        df_m = df_prevalence_male_reshaped[df_prevalence_male_reshaped["Year"] == year]
        df_f = df_prevalence_female_reshaped[df_prevalence_female_reshaped["Year"] == year]

        merged = pd.merge(df_m, df_f, on=["Country", "Code", "Year"])

        fig, ax = plt.subplots()
        ax.scatter(
            merged["Prevalence_male"],
            merged["Prevalence_female"],
            s=30,  # marker size
            alpha=0.7,
            label="Countries"
        )

        ax.set_title(f"HIV Prevalence by Gender in {year}")
        ax.set_xlabel("Male Prevalence")
        ax.set_ylabel("Female Prevalence")

        # Highlight selected country
        selected = merged[merged["Country"] == input.country_scatter()]
        if not selected.empty:
            x_val = selected["Prevalence_male"].values[0]
            y_val = selected["Prevalence_female"].values[0]
            
            # Plot the highlighted point
            ax.scatter(
                x_val,
                y_val,
                color="red",
                s=100,
                label=input.country_scatter()
            )
            
            # Annotate with (x, y) value
            ax.annotate(
                f"({x_val:.2f}, {y_val:.2f})",
                (x_val, y_val),
                textcoords="offset points",
                xytext=(-10, 20),  # offset to avoid overlapping the point
                ha='left',
                fontsize=12,
                color='red'
            )

        ax.legend()
        ax.grid(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        return fig


    # NOTE: The render_widget generates an interactive plot that is too slow, which significantly impacts performance. As a result, I switched to static images using Matplotlib.
    # @output
    # @render_widget
    # def new_cases_line():
    #     df = df_deaths_new_cases[df_deaths_new_cases["Country"] == selected_country_data()]
    #     year_range = input.new_cases_years()
    #     df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    #     return px.line(df, x="Year", y="New Cases", title="Number of new cases")


    # @output
    # @render_widget
    # def deaths_line():
    #     df = df_deaths_new_cases[df_deaths_new_cases["Country"] == selected_country_data()]
    #     year_range = input.deaths_years()
    #     df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    #     return px.line(df, x="Year", y="Deaths", title="Number of deaths")


    # @output
    # @render_widget
    # def art_coverage_line():
    #     df = df_deaths_new_cases[df_deaths_new_cases["Country"] == selected_country_data()]
    #     year_range = input.art_years()
    #     df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    #     if df.empty:
    #         return px.line(title="ART coverage - No data")
    #     return px.line(df, x="Year", y="ART", title="ART coverage (%)")

    # @output
    # @render_widget
    # def gender_scatter():
    #     year = int(input.year())
    #     df_m = df_prevalence_male_reshaped[df_prevalence_male_reshaped["Year"] == year]
    #     df_f = df_prevalence_female_reshaped[df_prevalence_female_reshaped["Year"] == year]
        
    #     merged = pd.merge(df_m, df_f, on=["Country", "Code", "Year"])
        
    #     fig = px.scatter(
    #         merged,
    #         x="Prevalence_male",
    #         y="Prevalence_female",
    #         hover_name="Country",
    #         labels={
    #             "Prevalence_male": "Male Prevalence",
    #             "Prevalence_female": "Female Prevalence"
    #         },
    #         title=f"HIV Prevalence by Gender in {year}"
    #     )
        
    #     selected = merged[merged["Country"] == input.country_scatter()]
    #     if not selected.empty:
    #         fig.add_scatter(
    #             x=selected["Prevalence_male"],
    #             y=selected["Prevalence_female"],
    #             mode="markers",
    #             marker=dict(color="orange", size=12),
    #             name=input.country_scatter()
    #         )
        
    #     return fig
   
    # Reactive dataset selector: children or adult
    @reactive.Calc
    def selected_dataset():
        if input.dataset_type() == "children":
            return df_children_newly_infected_reshaped, 'Children'
        else:
            return df_adult_newly_infected_reshaped, 'Adult'

    # Render interactive geo map for all countries by selected year
    @output
    @render_widget
    def geo_map():
        df, value_col = selected_dataset()
        year = input.year_slider()

        df_year = df[df['Year'] == year]

        # Set the color bar title dynamically
        colorbar_title = (
            "Children Newly Infected" if input.dataset_type() == "children" else "Adult Newly Infected"
        )

        fig = px.choropleth(
            df_year,
            locations="Code",
            color=value_col,
            hover_name="Country",
            # color_continuous_scale="Reds",
            color_continuous_scale=px.colors.sequential.Plasma,
            title=f"{input.dataset_type().capitalize()} Newly Infected - {year}",
        )
        fig.update_layout(
            margin={"r":0,"t":30,"l":0,"b":0},
            coloraxis_colorbar=dict(
                title=colorbar_title
            )
        )
        return fig

###############################################################################
# Run the app
app = App(app_ui, server)

# End of code