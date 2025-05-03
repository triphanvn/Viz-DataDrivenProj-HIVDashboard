from shiny import App, render, ui, reactive  
import pandas as pd
import plotly.express as px
from shinywidgets import output_widget, render_widget
import shinywidgets

###############################################################################
# Load CSVs
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
    'Incidence - HIV/AIDS - Sex: Both - Age: All Ages (Number)': 'New Cases',
    'Deaths - HIV/AIDS - Sex: Both - Age: All Ages (Number)': 'Deaths',
})
df_prevalence_male = df_prevalence_male.drop(columns=['Indicator Name', 'Indicator Code'])

df_prevalence_female = df_prevalence_female[df_prevalence_female['Country Code'].notna()]
df_prevalence_female = df_prevalence_female.rename(columns={
    'Country Name': 'Country',
    'Country Code': 'Code',
    'Incidence - HIV/AIDS - Sex: Both - Age: All Ages (Number)': 'New Cases',
    'Deaths - HIV/AIDS - Sex: Both - Age: All Ages (Number)': 'Deaths',
})
df_prevalence_female = df_prevalence_female.drop(columns=['Indicator Name', 'Indicator Code'])

# Reshape the datasets
df_prevalence_male_reshaped = df_prevalence_male.melt(
    id_vars=['Country', 'Code'], var_name='Year', value_name='Prevalence_male'
)
df_prevalence_male_reshaped = df_prevalence_male_reshaped[df_prevalence_male_reshaped['Year'].str.isnumeric()]
df_prevalence_male_reshaped['Year'] = df_prevalence_male_reshaped['Year'].astype(int)
df_prevalence_male_reshaped = df_prevalence_male_reshaped.dropna(subset=['Prevalence_male'])
df_prevalence_female_reshaped = df_prevalence_female.melt(
    id_vars=['Country', 'Code'], var_name='Year', value_name='Prevalence_female'
)
df_prevalence_female_reshaped = df_prevalence_female_reshaped[df_prevalence_female_reshaped['Year'].str.isnumeric()]
df_prevalence_female_reshaped['Year'] = df_prevalence_female_reshaped['Year'].astype(int)
df_prevalence_female_reshaped = df_prevalence_female_reshaped.dropna(subset=['Prevalence_female'])

# List all countries
countries = sorted(df_deaths_new_cases['Country'].unique())

years_scatter = sorted(df_prevalence_male_reshaped['Year'].unique())
years_scatter = [str(year) for year in years_scatter]

countries_list = sorted(df_prevalence_male_reshaped['Country'].unique())

# ###############################################################################
# UI layout
app_ui = ui.page_fluid(
    ui.panel_title("HIV dashboard", "HIV dashboard"),
    ui.hr(),
    ui.h4("HIV in the specific country"),
    ui.input_select("country", "Country", choices=countries, selected="Vietnam"),
    ui.output_ui("summary_cards"),
    ui.hr(),

    ui.layout_columns(
        # Group 1: New Cases
        ui.div(
            ui.h5("New HIV Cases Over Time"),
            output_widget("new_cases_line"),
            ui.input_slider("new_cases_years", "Select Year Range",
                            min=df_deaths_new_cases['Year'].min(),
                            max=df_deaths_new_cases['Year'].max(),
                            value=(1990, 2020),
                            step=1,
                            width="100%"),
        ),
        # Group 2: Deaths
        ui.div(
            ui.h5("HIV-related Deaths Over Time"),
            output_widget("deaths_line"),
            ui.input_slider("deaths_years", "Select Year Range",
                            min=df_deaths_new_cases['Year'].min(),
                            max=df_deaths_new_cases['Year'].max(),
                            value=(1990, 2020),
                            step=1,
                            width="100%"),
        ),
        # Group 3: ART Coverage
        ui.div(
            ui.h5("ART Coverage Over Time"),
            output_widget("art_coverage_line"),
            ui.input_slider("art_years", "Select Year Range",
                            min=df_deaths_new_cases['Year'].min(),
                            max=df_deaths_new_cases['Year'].max(),
                            value=(1990, 2020),
                            step=1,
                            width="100%"),
        ),
    ),

    ui.hr(),
    ui.h4("Prevalence of HIV by gender (teenager)"),
    ui.layout_columns(
        # Column 1 (1 portion): Both selectors stacked vertically in one card
        ui.card(
            ui.input_select("year", "Year", choices=years_scatter, selected="2019"),
            ui.input_select("country_scatter", "Highlight Country", choices=countries_list, selected="Viet Nam"),
            style="width: 100%"
        ),
        # Column 2 (2 portions): Scatter plot output
        ui.card(
            output_widget("gender_scatter"),
            style="width: 100%"
        ),
        col_widths=[3, 7],
    )
)



    # ui.layout_sidebar(
    #     ui.sidebar(
    #         ui.h4("HIV in the specific country"),
    #         ui.input_select("country", "Country", choices=countries, selected="Vietnam"),
    #         ui.hr(),
    #         ui.output_ui("summary_cards")
    #     ),
    #     # ✅ MAIN CONTENT LAYOUT DIRECTLY HERE
    #     ui.div(
    #         ui.layout_columns(
    #             ui.output_plot("new_cases_line"),
    #             ui.output_plot("deaths_line"),
    #             ui.output_plot("art_coverage_line")
    #         ),
    #         ui.hr(),
    #         ui.h4("Prevalence of HIV by gender (teenager)"),
    #         ui.input_select("year", "Year", choices=["2019"], selected="2019"),
    #         ui.output_plot("gender_scatter"),
    #         ui.hr(),
    #         ui.h4("HIV distribution across countries"),
    #         ui.output_plot("world_map")
    #     )
    # )
# )

###############################################################################
# Server logic
def server(input, output, session):

    @reactive.Calc
    def selected_country_data():
        return df_deaths_new_cases[df_deaths_new_cases["Country"] == input.country()]

    @output
    @render.ui
    def summary_cards():
        df = selected_country_data()
        latest = df[df["Year"] == df["Year"].max()]
        year = latest["Year"].values[0]
        new_cases = int(latest["New Cases"].values[0])
        deaths = int(latest["Deaths"].values[0])
        coverage = int(latest["ART"].values[0])

        return ui.layout_columns(
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
    @render_widget
    def new_cases_line():
        df = selected_country_data()
        year_range = input.new_cases_years()
        df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
        return px.line(df, x="Year", y="New Cases", title="Number of new cases")


    @output
    @render_widget
    def deaths_line():
        df = selected_country_data()
        year_range = input.deaths_years()
        df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
        return px.line(df, x="Year", y="Deaths", title="Number of deaths")


    @output
    @render_widget
    def art_coverage_line():
        df = selected_country_data()
        year_range = input.art_years()
        df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
        if df.empty:
            return px.line(title="ART coverage - No data")
        return px.line(df, x="Year", y="ART", title="ART coverage (%)")


    @output
    @render_widget
    def gender_scatter():
        year = int(input.year())
        df_m = df_prevalence_male_reshaped[df_prevalence_male_reshaped["Year"] == year]
        df_f = df_prevalence_female_reshaped[df_prevalence_female_reshaped["Year"] == year]
        
        merged = pd.merge(df_m, df_f, on=["Country", "Code", "Year"])
        
        fig = px.scatter(
            merged,
            x="Prevalence_male",
            y="Prevalence_female",
            hover_name="Country",
            labels={
                "Prevalence_male": "Male Prevalence",
                "Prevalence_female": "Female Prevalence"
            },
            title=f"HIV Prevalence by Gender in {year}"
        )
        
        selected = merged[merged["Country"] == input.country_scatter()]
        if not selected.empty:
            fig.add_scatter(
                x=selected["Prevalence_male"],
                y=selected["Prevalence_female"],
                mode="markers",
                marker=dict(color="orange", size=12),
                name=input.country_scatter()
            )
        
        return fig

    # @output
    # @render.plot
    # def world_map():
    #     df = df_adult_newly_infected[df_adult_newly_infected["Year"] == 2019]
    #     return px.scatter_geo(
    #         df,
    #         locations="Code",
    #         color="New infections",
    #         hover_name="Country",
    #         size="New infections",
    #         projection="natural earth",
    #         title="Adults (15–49) newly infected with HIV (2019)"
    #     )

###############################################################################
# Run the app
app = App(app_ui, server)
