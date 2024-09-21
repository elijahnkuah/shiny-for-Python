import pandas as pd
import matplotlib.pyplot as plt
import tempfile
from shiny import App, ui, render

# Load the banking dataset
banking_df = pd.read_csv("loan_data.csv")

# Ensure numeric columns are properly cast
banking_df['Loan Amount'] = pd.to_numeric(banking_df['Loan Amount'], errors='coerce')  # Convert loan amount to numeric
banking_df['Date'] = pd.to_datetime(banking_df['Date'], errors='coerce')  # Ensure date is in datetime format

# Define the custom CSS and UI layout
custom_css = """
    body {
    background-color: #893395 !important;
    color: white;
    }
    .visual {
        box-shadow: inset 0px 0px 10px 0px black;
        background-color: transparent;
        padding: 10px;
        margin: 10px 0;
        min-height: 250px;
        height: auto;
    }
    .container {
        margin-top: 11px;
        padding: 10px;
    }
    .select-input {
        margin-top: 20px;
    }
    .cards .card {
        width: 100%;
        height: 150px;
        margin-bottom: 20px;
    }
    .visual-wrapper {
        padding: 15px;
        margin-bottom: 25px;
    }
    .equal-width {
        display: flex;
        justify-content: space-between;
    }
    .equal-width .visual {
        flex: 1;
        max-width: 50%;
    }
    .equal-width .visual:first-child {
        margin-right: 15px;
    }
    .custom-table {
        background-color: #F5A4C5 !important;
    }
    .custom-table td {
        color: black !important;
        border: 1px solid white !important;
    }
    .custom-table th {
        color: black !important;
        border: 1px solid white !important;
    }
    .visual-large {
        height: 500px !important;  /* Ensuring a taller height for large charts */
    }

    /* New CSS for radio buttons with borders */
    .radio-tile input[type="radio"] {
        display: none;  /* Hide the default radio buttons */
    }

    .radio-tile label {
        border: 2px solid #F5A4C5;   /* Border color */
        border-radius: 5px;          /* Rounded corners */
        padding: 10px;               /* Padding for spacing */
        margin-bottom: 10px;         /* Space between tiles */
        display: inline-block;       /* Ensure consistent width/height */
        cursor: pointer;
        text-align: center;
        width: 200px;                /* Set consistent width for all tiles */
        height: 50px;                /* Set consistent height for all tiles */
        line-height: 30px;           /* Center the text vertically */
    }

    .radio-tile input[type="radio"]:checked + label {
        background-color: #F5A4C5;   /* Highlight selected tile */
        color: black;
    }

    /* Styling for heading "Loan Status" */
    .radio-tile .control-label {
        border: none;               /* No border for the heading */
        font-weight: bold;           /* Make the heading bold */
        margin-bottom: 10px;         /* Space between the heading and the first tile */
    }

"""

app_ui = ui.page_fluid(
    ui.tags.style(custom_css),
    
    # Top section with title and branch select
    ui.row(
        ui.column(9, ui.h1("BANK LOAN ANALYSIS - FINANCIAL INSTITUTION", style="color:white; text-align:center")),
        ui.column(3, ui.input_select("branch", "Bank Branches", ["All"] + banking_df['Branch'].unique().tolist(), selected="All"))
    ),
    
    # Sidebar and Cards
    ui.row(
        ui.column(2,
            ui.div(
                ui.h2(ui.output_text("total_loan"), style="color:white"), ui.h4("Total Loan Amount", style="color:#F5A4C5"),
                class_="container visual cards card"
            ),
            ui.div(
                ui.h2(ui.output_text("total_customers"), style="color:white"), ui.h4("Number of Borrowers", style="color:#F5A4C5"),
                class_="container visual cards card"
            ),
            ui.div(
                ui.input_select("borrower", "List of Borrowers", ["All"] + banking_df['Borrower'].unique().tolist(), selected="All"),
                class_="select-input"
            ),
            ui.div(
                ui.input_radio_buttons("loan_status", "Loan Status", 
                                    choices={"All": "All", "Current": "Current", "Defaulted": "Defaulted", "PaidOff": "PaidOff"}, 
                                    selected="All", 
                                    inline=False),  # Ensure buttons are displayed vertically
                class_="select-input radio-tile"
            )
        ),
        
        # Main body with charts and table
        ui.column(10,
            # First row: Pie chart and Line chart with equal width
            ui.div(
                ui.row(
                    ui.column(6, 
                        ui.div(ui.output_image("loan_status_pie"), class_="visual visual-wrapper")  # Pie chart
                    ),
                    ui.column(6, 
                        ui.div(ui.output_image("loan_trend_line"), class_="visual visual-wrapper")  # Line chart
                    )
                )
            ),
            
            # Second row: Stacked bar chart and table with equal width
            ui.div(
                ui.row(
                    ui.column(6, 
                        ui.div(ui.output_image("branches_loan_status"), class_="visual visual-large visual-wrapper")  # Stacked bar chart
                    ),
                    ui.column(6, 
                        ui.div(ui.output_table("loan_table", height="500px"), class_="visual visual-large visual-wrapper")  # Table with fixed height
                    )
                )
            )
        )
    )
)

# Server logic
def server(input, output, session):
    # Filtered dataset by branch, loan status, and borrower
    def get_filtered_data():
        filtered_df = banking_df.copy()

        # Filter by branch if a specific branch is selected
        if input.branch() != "All":
            filtered_df = filtered_df[filtered_df['Branch'] == input.branch()]

        # Filter by loan status if a specific loan status is selected
        if input.loan_status() != "All":
            filtered_df = filtered_df[filtered_df['Loan Status'] == input.loan_status()]

        # Filter by borrower if a specific borrower is selected
        if input.borrower() != "All":
            filtered_df = filtered_df[filtered_df['Borrower'] == input.borrower()]

        return filtered_df

    # Helper function to save plots as images and return the correct format
    def save_plot_to_temp():
        temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(temp.name)
        plt.close()  # Close the figure after saving
        return {"src": temp.name}  # Return the correct dictionary format with the image source

    # Render the total loan amount in cards
    @output
    @render.text
    def total_loan():
        filtered_df = get_filtered_data()
        total = filtered_df['Loan Amount'].sum()
        return f"${total:,.2f}"

    # Render the total customers in cards
    @output
    @render.text
    def total_customers():
        filtered_df = get_filtered_data()
        return str(filtered_df['Borrower'].count())

    # Render the pie chart (Loan Status)
    @output
    @render.image
    def loan_status_pie():
        filtered_df = get_filtered_data()

        # Group by 'Loan Status' and sum the 'Loan Amount'
        status_amounts = filtered_df.groupby('Loan Status')['Loan Amount'].sum()
        print("Status amount:**********")
        print(status_amounts)
        # Calculate the percentage for each loan status
        percentages = 100 * status_amounts / status_amounts.sum()
        print("Percentages: ",percentages)
        # Format labels to include both the amount and percentage
        labels = [f'{status}: £{amount:,.2f} ({percentage:.1f}%)' 
                for status, amount, percentage in zip(status_amounts.index, status_amounts, percentages)]

        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(6.25, 4))

        # Plot the pie chart
        ax.pie(status_amounts, labels=labels, autopct=None, colors=[ '#F5A4C5', '#66b3ff','white'], 
            textprops={'color': 'white'}, wedgeprops={'width': 0.4})

        # Remove background color
        ax.set_facecolor('none')  # Remove background of the axis
        fig.patch.set_facecolor('none')  # Remove background of the figure

        # Set title
        plt.title("Loan Status Distribution", color='#F5A4C5')

        # Ensure pie chart is a perfect circle
        plt.axis('equal')

        return save_plot_to_temp()



    # Render the line chart (Loan Amount by Year)
    @output
    @render.image
    def loan_trend_line():
        filtered_df = get_filtered_data()
        filtered_df['Year'] = filtered_df['Date'].dt.year
        loan_amount_by_year = filtered_df.groupby('Year')['Loan Amount'].sum()

        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(6.8, 4))  # Adjust the size for better visuals

        # Plot the data on the axis
        loan_amount_by_year.plot(kind='line', marker='o', color='#F5A4C5', ax=ax)

        # Remove background color
        ax.set_facecolor('none')  # Remove background of the axis
        fig.patch.set_facecolor('none')  # Remove background of the figure

        # Set title and labels
        plt.title("Loan Amount Over Time", color='#F5A4C5')
        #plt.xlabel("Year", color='white')

        return save_plot_to_temp()


    # Render the stacked bar chart (Branches Loan Amount by Status)
    @output
    @render.image
    def branches_loan_status():
        filtered_df = get_filtered_data()
        branch_status = filtered_df.pivot_table(index='Branch', columns='Loan Status', values='Loan Amount', aggfunc='sum').fillna(0)
        
        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(6.8, 4.9))  # Adjust height for better fit

        # Plot the data on the axis
        branch_status.plot(kind='bar', stacked=True, color=['#F5A4C5', '#66b3ff', 'white'], ax=ax)

        # Remove background color
        ax.set_facecolor('none')  # Remove background of the axis
        fig.patch.set_facecolor('none')  # Remove background of the figure

        # Set title and legend
        plt.title("Loan Amount by Branch and Status", color='#F5A4C5')
        plt.legend(title="Loan Status", loc='upper left')

        return save_plot_to_temp()


    '''# Render the loan data table
    @output
    @render.table
    def loan_table():
        filtered_df = get_filtered_data()
        return filtered_df[['Borrower', 'Branch', 'Date', 'Loan Amount', 'Interest Rate', 'Tenor', 'Loan Status']].head(6)
'''
    @output
    @render.table
    def loan_table():
        filtered_df = get_filtered_data()
        df = filtered_df[['Borrower', 'Branch', 'Date', 'Loan Amount', 'Interest Rate', 'Tenor', 'Loan Status']].head(8)
        
        # Apply custom styles
        styled_df = df.style.set_table_attributes('class="custom-table"').set_table_styles({
            '': [{'selector': 'table', 'props': 'background-color: #F5A4C5 !important;'}],  # Set table background color
            'td': [{'selector': 'td', 'props': 'color: black !important;'}],  # Set font color to black
            'thead th': [{'selector': 'thead th', 'props': 'color: black !important; border: 1px solid white !important;'}],  # Header font color and border
            'tbody td': [{'selector': 'tbody td', 'props': 'border: 1px solid white !important;'}]  # Cell border color
        })
        
        return styled_df


# Create the app instance
app = App(app_ui, server)
