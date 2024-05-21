from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
from datetime import datetime
from dash import Dash, dcc, html, dash_table, Input, Output, State, ALL

app = Dash(__name__)
app.title = 'myfinanceplanner'

# -- Import and clean data (importing csv into pandas)
def load_data():
    # Connection setup   
    # Database URL  
    DATABASE_URL = "postgresql://postgresql_finance_user:Xda6CRIftQmupM1vnXit1fnbKIfcfLhc@dpg-cp1p0hud3nmc73b8v0qg-a.ohio-postgres.render.com:5432/postgresql_finance"

    # Creating an SQLAlchemy engine
    engine = create_engine(DATABASE_URL)
    
    # Use the engine to execute a query and load into DataFrame
    transactions_df = pd.read_sql("SELECT * FROM Transactions;", engine, parse_dates=['date'])
    categories_df = pd.read_sql("SELECT * FROM Categories;", engine)
    users_df = pd.read_sql("SELECT * FROM Users;", engine)
    monthly_budgets_df = pd.read_sql("SELECT * FROM MonthlyBudgets;", engine, parse_dates=['budgetmonth'])
    categorical_budgets_df = pd.read_sql("SELECT * FROM CategoricalBudgets;", engine)
    engine.dispose()  # Close the connection safely

    return transactions_df, categories_df, users_df, monthly_budgets_df, categorical_budgets_df

def load_local_database():
    # Load data from CSV files
    transactions_df = pd.read_csv('../localdb/transactions.csv', parse_dates=['date'])
    categories_df = pd.read_csv('../localdb/categories.csv')
    users_df = pd.read_csv('../localdb/users.csv')
    monthly_budgets_df = pd.read_csv('../localdb/monthlybudgets.csv', parse_dates=['budgetmonth'])
    categorical_budgets_df = pd.read_csv('../localdb/categoricalbudgets.csv')

    return transactions_df, categories_df, users_df, monthly_budgets_df, categorical_budgets_df

# Loading data
transactions_df, categories_df, users_df, monthly_budgets_df, categorical_budgets_df = load_local_database()
# transactions_df, categories_df, users_df, budgets_df = load_data()
# print('\nTRANSACTIONS DB\n', transactions_df[:5])
# print('CATEGORIES DB\n', categories_df[:5])
# print('USERS DB\n', users_df[:5])
# print('MONTHLY BUDGETS DB\n', monthly_budgets_df[:5])
# print('CATEGORICAL BUDGETS DB\n', categorical_budgets_df[:5])

# Dictionary to convert month names to integer values
monthsToInt = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

# Reverse the dictionary to convert the integers to month names
IntToMonths = {v: k for k, v in monthsToInt.items()} 

current_month = datetime.now().month
current_year = datetime.now().year

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("My Financial Dashboard", style={'text-align': 'center'}),

    dcc.RadioItems(id='chart_type',
                   options=[
                       {'label': 'Line Chart', 'value': 'line'},
                       {'label': 'Bar Chart', 'value': 'bar'},
                       {'label': 'Stacked Bar Chart', 'value': 'stacked_bar'}
                   ],
                   value='line',
                   style={'margin-top': '20px'}
                   ),

    # Put month selector in a container so it can be hidden when not needed
    html.Div(id='month_selector_container', children=[
        html.H4("Select Month", style = {'text-align': 'left'}),
        dcc.Dropdown(id="slct_month",
                    options= [{'label': key, 'value': value} for key, value in monthsToInt.items()], # Convert the python dictionary to a list of dictionaries in HTML
                    multi=False,
                    value=current_month, # Initial value
                    style={'width': "40%"}
                    ),
    ]),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_spending_map', figure={}),

    html.H2("Add a New Transaction", style={'text-align': 'center'}),
        dcc.DatePickerSingle(
            id='input_date',
            date=pd.Timestamp.now().strftime('%Y-%m-%d'),
            display_format='YYYY-MM-DD',
            style={'width': '10%', 'margin': '10px auto', 'display': 'block'}
        ),
        dcc.Input(
            id='input_amount',
            type='number',
            min=0,
            placeholder='Amount',
            style={'width': '10%', 'margin': '10px auto', 'display': 'block'}
        ),
        dcc.Dropdown(
            id='input_category',
            options=[{'label': category, 'value': category} for category in categories_df['name']],
            placeholder='Select Category',
            style={'width': '40%', 'margin': '10px auto', 'display': 'block'}
        ),
        dcc.Input(
            id='input_description',
            type='text',
            placeholder='Description',
            style={'width': '40%', 'margin': '10px auto', 'display': 'block'}
        ),
        html.Button('Add Transaction', id='submit_transaction', n_clicks=0, style={'width': '20%', 'margin': '10px auto', 'display': 'block'}),
    html.Div(id='transaction_status', style={'text-align': 'center'}), # Display the status of the transaction   

    html.H2("Manage Budget", style={'text-align': 'center'}),
    html.Div(id='budget_month_selector', children=[
        dcc.Dropdown(id="slct_budget_month",
                    options= [{'label': key, 'value': value} for key, value in monthsToInt.items()],
                    multi=False,
                    value=current_month, # Initial value
                    style={'width': "40%", 'margin': '10px auto', 'display': 'inline-block'}
                    ),
        dcc.Dropdown(id="slct_budget_year",
                    options= [{'label': year, 'value': year} for year in range(2023, current_year+2)],
                    multi=False,
                    value=current_year, # Initial value
                    style={'width': '150px', 'margin': '10px auto 10px 10px', 'display': 'inline-block'}
                    ),
    ], style={'text-align': 'center'}),
    html.Div([
        html.Label("Total Budget:"),
        dcc.Input(
            id='input_total_budget',
            type='number',
            min=0,
            style={'margin-left': '10px', 'margin-bottom': '20px'}
        ),
        html.Div(id='budget_overview', style={'text-align': 'center', 'margin-bottom': '20px'}), # Display the total budget
        html.Button('Update Total Budget', id='submit_total_budget', n_clicks=0, style={'width': '20%', 'margin': '10px auto', 'display': 'block'}),
        html.Div(id='total_budget_status', style={'text-align': 'center'})
    ], style={'text-align': 'center'}),
    html.Div([
        dash_table.DataTable(
            id='budget_table',
            columns=[
                {'name': 'Category', 'id': 'categoryname', 'type': 'text'},
                {'name': 'Budget', 'id': 'categorybudget', 'type': 'numeric', 'editable': True}
            ],
            data=[],
            style_table={'width': '60%', 'margin': 'auto'},
            style_cell={'textAlign': 'left'}
        )
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    html.Div(id='unallocated_budget', style={'text-align': 'center', 'margin-bottom': '20px'}), # Display the unallocated budget
    html.Div([
        dcc.Dropdown(
            id='budget_category_dropdown',
            options=[{'label': category, 'value': category} for category in categorical_budgets_df['categoryname']],
            placeholder='Select Category',
            style={'width': '40%', 'margin': '10px auto', 'display': 'inline-block'}
        ),
        dcc.Input(
            id='budget_category_input',
            type='number',
            min=0,
            placeholder='Enter Budget',
            style={'width': '40%', 'margin': '10px auto', 'display': 'inline-block', 'margin-left': '10px'}
        ),
        html.Button('Update Category Budget', id='submit_category_budget', n_clicks=0, style={'width': '20%', 'margin': '10px auto', 'display': 'block'}),
        html.Div(id='category_budget_status', style={'text-align': 'center'})
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Hidden div to store update triggers
    html.Div(id='update_trigger', style={'display': 'none'})
])

# ------------------------------------------------------------------------------
@app.callback(
    [Output('my_spending_map', 'figure')],
    [Input('chart_type', 'value'),
     Input('slct_month', 'value')]
)

def update_graph(chart_type, selected_month):
    # Filter the DataFrame to the selected month
    filtered_df = transactions_df[transactions_df['date'].dt.month == selected_month]

    if chart_type == 'line':
        # Group by day of the month and sum the amounts
        daily_spending = filtered_df.groupby(filtered_df['date'].dt.day)['amount'].sum().reset_index()
        daily_spending.columns = ['Day', 'Total Spent']

        # Create a line chart with Plotly Express
        fig = px.line(
            daily_spending, x='Day', y='Total Spent',
            title=f'Spending Trend for {IntToMonths[selected_month]}',
            labels={'Day': 'Day of the Month', 'Total Spent': 'Amount Spent ($)'},
            markers=True, # Makes it easier to see individual data points
            range_x=[1, 31] # Show all days of the month
            )
        
        # Show the x-axis ticks for each day of the month
        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear'
            )
        )
    
    elif chart_type == 'bar':
        # Group by category and sum the amounts
        category_spending = filtered_df.groupby('categoryname')['amount'].sum().reset_index()
        category_spending.columns = ['Category', 'Total Spent']

        # Create a bar chart with Plotly Express
        fig = px.bar(
            category_spending, x='Category', y='Total Spent',
            title=f'Spending by Category for {IntToMonths[selected_month]}',
            labels={'category': 'Category', 'amount': 'Amount Spent ($)'},
            color='Category'
            )
    
    elif chart_type == 'stacked_bar':
        # Group by category and sum the amounts
        daily_category_spending = filtered_df.groupby([filtered_df['date'].dt.day, 'categoryname'])['amount'].sum().reset_index()
        daily_category_spending.columns = ['Day', 'Category', 'Total Spent']
        # print("\nSTACKED BAR CHART\n", daily_category_spending)

        # Create a stacked bar chart with Plotly Express
        fig = px.bar(
            daily_category_spending, x='Day', y='Total Spent', color='Category',
            title=f'Spending by Category for {IntToMonths[selected_month]}',
            labels={'Day': 'Day of the Month', 'Total Spent': 'Amount Spent ($)'}
            )
        
        # Show the x-axis ticks for each day of the month
        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear'
            )
        )

    return [fig]

# ------------------------------------------------------------------------------
@app.callback(
    Output('transaction_status', 'children'),
    [Input('submit_transaction', 'n_clicks')],
    [State('input_date', 'date'), State('input_amount', 'value'), State('input_category', 'value'), State('input_description', 'value')]
)

def add_transaction(n_clicks, date, amount, category, description):
    # If button has been clicked and all fields have been filled out
    if n_clicks > 0 and date and amount and category:
        # Load the latest transactions DB
        transactions_df = pd.read_csv('../localdb/transactions.csv', parse_dates=['date'])

        # Add the new transaction to the DataFrame
        new_transaction = {
            'transactionid': transactions_df['transactionid'].max() + 1, # Increment the transaction ID
            'userid': 1, # Hardcoded for now
            'date': date,
            'categoryname': category,
            'amount': amount, 
            'description': description
            }
        
        # Append the new transaction to the end of the DataFrame
        transactions_df.loc[len(transactions_df)] = new_transaction
        
        # Save the updated DataFrame to the CSV file
        transactions_df.to_csv('../localdb/transactions.csv', index=False)

        return f"Transaction added: {date}, {amount}, {category}"
    elif n_clicks > 0:
        if not date:
            return "Please select a date"
        elif not amount:
            return "Please enter an amount"
        elif not category:
            return "Please select a category"
    return "" # If the button has not been clicked

# ------------------------------------------------------------------------------
@app.callback(
    [Output('budget_overview', 'children'),
     Output('input_total_budget', 'value'),
     Output('budget_table', 'data'),
     Output('unallocated_budget', 'children')],
    [Input('slct_budget_month', 'value'),
     Input('slct_budget_year', 'value'),
     Input('update_trigger', 'children')]
)

def display_budget_overview(selected_month, selected_year, _):
    # Convert the selected month and year to a datetime object
    selected_date = pd.to_datetime(f'{selected_year}-{selected_month:02d}-01')

    # Load the latest budgets DB
    monthly_budgets_df = pd.read_csv('../localdb/monthlybudgets.csv', parse_dates=['budgetmonth'])
    categorical_budgets_df = pd.read_csv('../localdb/categoricalbudgets.csv')
    
    monthly_budget_row = monthly_budgets_df[monthly_budgets_df['budgetmonth'] == selected_date]
    if monthly_budget_row.empty:
        total_budget = 0
    else:
        total_budget = int(monthly_budget_row['totalbudget'].values[0])

    budget_overview = f"Total Budget for {selected_date.strftime('%Y-%m')}: ${total_budget}"

    # Display the allocated budget for each category
    budget_table_data = categorical_budgets_df.to_dict('records')

    # Calculate the unallocated budget
    allocated_budget = categorical_budgets_df['categorybudget'].sum()
    unallocated_budget = int(total_budget - allocated_budget)

    # Customize the display message based on the budget surplus/deficit
    if unallocated_budget < 0:
        unallocated_budget_display = f"Exceeding Monthly Budget by ${-unallocated_budget}"
    elif unallocated_budget > 0:
        unallocated_budget_display = f"Remaining Monthly Budget of ${unallocated_budget}"
    else:
        unallocated_budget_display = f"${total_budget} Budget Fully Allocated"

    return budget_overview, total_budget, budget_table_data, unallocated_budget_display

# ------------------------------------------------------------------------------
@app.callback(
    Output('total_budget_status', 'children'),
    [Input('submit_total_budget', 'n_clicks')],
    [State('slct_budget_month', 'value'), 
     State('slct_budget_year', 'value'), 
     State('input_total_budget', 'value')]
)

def update_total_budget(n_clicks, selected_month, selected_year, total_budget):
    if n_clicks > 0:
        if total_budget is None or total_budget == '':
            return "Please enter a total budget"

        # Convert the selected month and year to a datetime object
        selected_date = pd.to_datetime(f'{selected_year}-{selected_month:02d}-01')

        # Load the latest budgets DB before updating
        monthly_budgets_df = pd.read_csv('../localdb/monthlybudgets.csv', parse_dates=['budgetmonth'])

        # Update or insert the monthly budget
        if selected_date in monthly_budgets_df['budgetmonth'].values:
            monthly_budgets_df.loc[monthly_budgets_df['budgetmonth'] == selected_date, 'totalbudget'] = total_budget
        else:
            new_monthly_budget = {
                'budgetid': monthly_budgets_df['budgetid'].max() + 1,
                'userid': 1,  # Hardcoded for now
                'totalbudget': total_budget,
                'budgetmonth': selected_date
            }
            monthly_budgets_df.loc[len(monthly_budgets_df)] = new_monthly_budget

        # Save the updated DataFrame to the CSV file
        monthly_budgets_df.to_csv('../localdb/monthlybudgets.csv', index=False)

        return "Total budget updated successfully!"
    return ""

# ------------------------------------------------------------------------------
@app.callback(
    Output('category_budget_status', 'children'),
    [Input('submit_category_budget', 'n_clicks')],
    [State('budget_category_dropdown', 'value'), 
     State('budget_category_input', 'value')]
)

def update_category_budget(n_clicks, selected_category, new_category_budget):
    if n_clicks > 0:
        if selected_category and new_category_budget is not None:
            # Load the latest categorical budgets DB before updating
            categorical_budgets_df = pd.read_csv('../localdb/categoricalbudgets.csv')

            # Update the selected category's budget
            categorical_budgets_df.loc[categorical_budgets_df['categoryname'] == selected_category, 'categorybudget'] = new_category_budget

            # Save the updated DataFrame to the CSV file
            categorical_budgets_df.to_csv('../localdb/categoricalbudgets.csv', index=False)

            return "Category budget updated successfully!"
        elif not selected_category:
            return "Please select a category"
        elif new_category_budget is None:
            return "Please enter a budget amount"
    return ""

# ------------------------------------------------------------------------------
@app.callback(
    Output('update_trigger', 'children'),
    [Input('submit_total_budget', 'n_clicks'),
     Input('submit_category_budget', 'n_clicks')]
)
def trigger_update(total_budget_clicks, category_budget_clicks):
    return total_budget_clicks + category_budget_clicks

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)