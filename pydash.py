# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from datetime import datetime
from datetime import date

import dash
#import dash_core_components as dcc
from dash import dcc
import dash_bootstrap_components as dbc
#import dash_html_components as html
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
#import dash_table
from dash import dash_table
from nsetools import Nse
#For historical data
from nsepy import get_history


app = dash.Dash(__name__)
#Theme Change
#TODO: Logic Theme Configuration and reference URL https://bootswatch.com/default/
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

#Define portfolio function
def get_portfolio():
    df = pd.read_csv("portfolio.csv")
    #print(df.head(3))
    symbol_list = df['Stock Name']
    broker_list = df['Broker Name']
    qty_list = df['Qty']
    inv_price_list = df['Inv Price']
    nse =Nse()
    portfolio_vals = []
    for idx,symbol in enumerate(symbol_list):
        #print('Getting.... '+symbol)
        qty = qty_list[idx]
        inv_price = inv_price_list[idx]
        broker = broker_list[idx]
        q = nse.get_quote(symbol)
        inv_val = qty * inv_price
        inv_val = round(inv_val,2)
        cur_val = qty * q['lastPrice']
        cur_val = round(cur_val,2)
        tot_pnl = cur_val - inv_val
        tot_pnl = round(tot_pnl,2)
        tot_pnl_pct = ((cur_val - inv_val)/inv_val)*100
        tot_pnl_pct = round(tot_pnl_pct,2)
        high52LtpPct = ((q['lastPrice']- q['high52'])/q['high52'])*100
        high52LtpPct = round(high52LtpPct,2)
        val_dict= {'symbol' :q['symbol'],'broker':broker,'qty':qty,'invPrice':inv_price,'changeVal':q['change'],'changepct':q['pChange'],'previousClose':q['previousClose'],'lastPrice':q['lastPrice'],'invVal':inv_val,'curVal':cur_val,'pnlVal':tot_pnl,'pnlPct':tot_pnl_pct,'hihg52LtpPct':high52LtpPct,'high52':q['high52'],'low52':q['low52']}
        portfolio_vals.append(val_dict)
        #print('symbol :'+q['symbol']+',changeVal:'+str(q['change'])+',changepct:'+str(q['pChange'])+' ,previousClose:'+str(q['previousClose'])+', lastPrice:'+str(q['lastPrice'])+', high52:'+str(q['high52'])+', low52:'+str(q['low52']))
    
    portfolio_df = pd.DataFrame(portfolio_vals)
    #print(portfolio_df.head(5)) 
    return portfolio_df

#MF folio historical details https://api.mfapi.in/mf/102948
def get_mf_folio():
    df = pd.read_csv("mf_folio.csv")
    #print(df.head(3))
    folio_list = df['folio_no']
    qty_list = df['qty']
    buy_price_list = df['buy_avg_price']
    nse =Nse()
    folio_vals = []
    df = pd.read_csv("https://www.amfiindia.com/spages/NAVAll.txt",delimiter=";")
    for idx,folio_no in enumerate(folio_list):
        result_df = df.loc[df['Scheme Code'] == str(folio_no)]
        print(result_df)
        scheme_name = result_df['Scheme Name'].values[0] 
        nav_date = result_df['Date'].values[0] 
        nav = result_df['Net Asset Value'].values[0]
        buy_price = buy_price_list[idx]
        qty = qty_list[idx]
        inv_val= qty*buy_price
        inv_val= round(inv_val,2)
        cur_val = qty * float(nav)
        cur_val = round(cur_val,2)
        tot_pnl = cur_val - inv_val
        tot_pnl = round(tot_pnl,2)
        tot_pnl_pct = ((cur_val - inv_val)/inv_val)*100
        tot_pnl_pct = round(tot_pnl_pct,2)
        folio_data = {'folio_no':folio_no,'scheme_name':scheme_name,'buy_price':buy_price,'qty':qty,'nav':nav,'nav_date':nav_date,'inv_val':inv_val,'cur_val':cur_val,'tot_pnl':tot_pnl,'tot_pnl_pct':tot_pnl_pct}
        folio_vals.append(folio_data)
    folio_df = pd.DataFrame(folio_vals)
    #print(folio_df.head(8)) 
    return folio_df

def get_historical_data(symbol,start_date,end_date):
    print('get_historical_data.. called ...'+str(symbol)+','+str(start_date)+','+str(end_date))
    start_date_object = date.fromisoformat(start_date)
    start_date_string = start_date_object.strftime('%d-%b-%Y')
    end_date_object = date.fromisoformat(end_date)
    end_date_string = end_date_object.strftime('%d-%b-%Y')
    print('start_date_str :'+start_date_string+', end_date_str :'+end_date_string)
    try:
         data = get_history(symbol=symbol, start=date(2019,12,10), end=date(2020,12,10))
         print(data.head(5))
         return data
    except Exception as e:
        print(e)

def get_mf_details(folio_no):
    print('Foliono :'+str(folio_no))
    df = pd.read_csv("https://www.amfiindia.com/spages/NAVAll.txt",delimiter=";")
    #print(df.head(5))
    #result_df = df.loc[df['Scheme Code'] == '102948']
    result_df = df.loc[df['Scheme Code'] == str(folio_no)]
    scheme_name = result_df['Scheme Name'].values[0] 
    nav_date = result_df['Date'].values[0] 
    nav = result_df['Net Asset Value'].values[0]
    #print(result_df)
    #print('Scheme :'+scheme_name+'  NAV :'+str(nav)+'  Date-'+str(nav_date))
    return result_df


def get_quote(symbol):
    print('get_quote() : symbol :'+symbol)
    nse =Nse()
    q = nse.get_quote(symbol)
    print(q)
    return q

def get_nse_top_gainers():
    nse =Nse()
    q = nse.get_top_gainers()
    df = pd.DataFrame(q)
    return df


def get_nse_top_losers():
    nse =Nse()
    q = nse.get_top_losers()
    df = pd.DataFrame(q)
    return df

def get_advances_declines():
    nse =Nse()
    q = nse.get_advances_declines()
    df = pd.DataFrame(q)
    return df

def get_index_quote(index_symbol):
    nse =Nse()
    q = nse.get_index_quote(index_symbol)
    return q

#------------Styles Definition----------------
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}
#------------End of Styles Definition----------
#TODO: Logic one time Chart loading for Mutual Fund Folio
mf_df =get_mf_folio()
mf_fig = px.scatter_3d(mf_df, x='scheme_name', y='inv_val', z='tot_pnl_pct', size='cur_val', color='tot_pnl_pct',
                    hover_data=['cur_val'])
mf_fig.update_layout(scene_zaxis_type="log",height=800,width=1200)
#--- End of one time loading

app.layout = html.Div(children=[

     dcc.Tabs([
        dcc.Tab(label='PorfolioTab',style=tab_style, selected_style=tab_selected_style, children=[
        html.H3(children='Stock Portfolio'),
       
	   #Content goes here
        dbc.Row(
          dbc.Col(
               html.Div(id='lastupdated'), width={'size':3,"offset":1}
               ) #end of Col
        ),# End of row
    
    #Row Model
    #Timer Component for 1 minute Interval
    dcc.Interval(id='portfolioTimer', interval=90000, n_intervals=0),

    dbc.Row(
      dbc.Col(
       dcc.Loading(id="loading-2",children=[ 
        dash_table.DataTable(
        id='portfolioTable',
        columns=[
            {'name': 'symbol', 'id': 'symbol', 'type': 'text'},
            {'name': 'broker', 'id': 'broker', 'type': 'text'},
            {'name': 'qty', 'id': 'qty', 'type': 'numeric'},
            {'name': 'invPrice', 'id': 'invPrice', 'type': 'numeric'},
            {'name': 'PrevClose', 'id': 'previousClose', 'type': 'numeric'},
            {'name': 'Ltp', 'id': 'lastPrice', 'type': 'numeric'},
            {'name': 'DChangepct ', 'id': 'changepct', 'type': 'numeric'},
            {'name': 'DChngVal', 'id': 'changeVal', 'type': 'numeric'},
            {'name': 'Holding Value', 'id': 'invVal', 'type': 'numeric'},
            {'name': 'Market Value', 'id': 'curVal', 'type': 'numeric'},
            {'name': 'TotalPNLVal', 'id': 'pnlVal', 'type': 'numeric'},
            {'name': 'TotalPNL%', 'id': 'pnlPct', 'type': 'numeric'},
            {'name': '52WkHigh', 'id': 'high52', 'type': 'numeric'},
            {'name': '52WkLow', 'id': 'low52', 'type': 'numeric'},
            {'name': '52WkLtp%', 'id': 'hihg52LtpPct', 'type': 'numeric'},
            
        ],
        #data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=15,
        #black header
        style_header={
        'color': 'white',
        'backgroundColor': 'black',
        'fontweight':'bold'
       },
       #Gray cell
       style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
        style_cell={'textAlign':'left'},
        style_data_conditional=[
            #Positive Value for Change %
             {
                'if': {
                     'filter_query':'{changepct} > 0', 
                    'column_id':'changepct'
                    },
                  'backgroundColor':'green',
                  'color':'white'  
             },
             #Negative Value Change %
             {
                'if': {
                     'filter_query':'{changepct} < 0', 
                    'column_id':'changepct'
                    },
                  'backgroundColor':'red',
                  'color':'white'  
             },
             
              #Positive Value for Change %
             {
                'if': {
                     'filter_query':'{lastPrice} > {previousClose}', 
                    'column_id':'lastPrice'
                    },
                  'backgroundColor':'green',
                  'color':'white'  
             },
             #Negative Value Change %
             {
                'if': {
                     'filter_query':'{lastPrice} < {previousClose}', 
                    'column_id':'lastPrice'
                    },
                  'backgroundColor':'red',
                  'color':'white'  
             },
            #52 Weeks near indicator near -5.0%
             {
                'if': {
                     'filter_query':'{hihg52LtpPct} > -5.0', 
                    'column_id':'hihg52LtpPct'
                    },
                  'backgroundColor':'green',
                  'color':'white'  
             },
             #52 Weeks far indicator greater than -25.0%
             {
                'if': {
                     'filter_query':'{hihg52LtpPct} < -20.0', 
                    'column_id':'hihg52LtpPct'
                    },
                  'backgroundColor':'red',
                  'color':'white'  
             },
             #Positive Value for Total PNL
             {
                'if': {
                     'filter_query':'{pnlPct} > 50', 
                    'column_id':'pnlPct'
                    },
                  'backgroundColor':'green',
                  'color':'white'  
             },
             #Negative Value for Total PNL
             {
                'if': {
                     'filter_query':'{pnlPct} < 0', 
                    'column_id':'pnlPct'
                    },
                  'backgroundColor':'red',
                  'color':'white'  
             }
         ]

        ),],type="dot",), 
        width={'size':3,"offset":1}
        ) #Col End 
    ),  #Row End
  
    #Charts Row
     dbc.Row([
        dbc.Col(
            html.Div([
            #dbc.Spinner(children=[dcc.Graph(id='portfolio_piechart'),dcc.Graph(id='portfolio_barchart'),],color="primary",type="grow",fullscreen=False,spinner_style={"width":"10rem","height":"10rem"})
            dcc.Loading(children=[dcc.Graph(id='portfolio_piechart')],color="blue",type="circle",fullscreen=False),
            ]),

            width={'size':3,"offset":1}
        ), #Col End 
          dbc.Col(
            html.Div([
            #dbc.Spinner(children=[dcc.Graph(id='portfolio_piechart'),dcc.Graph(id='portfolio_barchart'),],color="primary",type="grow",fullscreen=False,spinner_style={"width":"10rem","height":"10rem"})
            dcc.Loading(children=[dcc.Graph(id='portfolio_barchart'),],color="blue",type="graph",fullscreen=False),
            ]),

            width={'size':3,"offset":1}
        ) #Col End 
     ]),  #Row End
    html.H3(children='Mutualfund folio'),
    #MF Table
     dbc.Row(
        dbc.Col(
         dash_table.DataTable(
        id='mfTable',
        columns=[
            {'name': 'folio_no', 'id': 'folio_no', 'type': 'text'},
            {'name': 'scheme_name', 'id': 'scheme_name', 'type': 'text'},
            {'name': 'qty', 'id': 'qty', 'type': 'numeric'},
            {'name': 'invPrice', 'id': 'buy_price', 'type': 'numeric'},
            {'name': 'Nav', 'id': 'nav', 'type': 'numeric'},
            {'name': 'nav_date ', 'id': 'nav_date', 'type': 'datetime'},
            {'name': 'Inv_val', 'id': 'inv_val', 'type': 'numeric'},
            {'name': 'Cur_val', 'id': 'cur_val', 'type': 'numeric'},
            {'name': 'tot_pnl', 'id': 'tot_pnl', 'type': 'numeric'},
            {'name': 'tot_pnl_pct', 'id': 'tot_pnl_pct', 'type': 'numeric'},
        ],
        data=get_mf_folio().to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=15,
        #black header
        style_header={
        'color': 'white',
        'backgroundColor': 'black',
        'fontweight':'bold'
       },
       #Gray cell
       style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
        style_cell={'textAlign':'left'},
        style_data_conditional=[
            #Positive Value for Change %
             {
                'if': {
                     'filter_query':'{tot_pnl_pct} > 50', 
                    'column_id':'tot_pnl_pct'
                    },
                  'backgroundColor':'green',
                  'color':'white'  
             },
             #Negative Value Change %
             {
                'if': {
                     'filter_query':'{tot_pnl_pct} < 10', 
                    'column_id':'tot_pnl_pct'
                    },
                  'backgroundColor':'red',
                  'color':'white'  
             },
         ]

         ),
        width={'size':3,"offset":1}
        ) #Col End 
     ),  #Row End

      #Charts Row
     dbc.Row(
          dbc.Col(
              dcc.Graph(id='mf_folio_chart',figure=mf_fig,style={'width':'280vh','height':'180vh'}), width={'size':6,"offset":1}
        ) #Col End 
     ),  #Row End

     ]), #End of Portfolio Tab

     
     dcc.Tab(label='NSETab',style=tab_style, selected_style=tab_selected_style, children=[
        #TODO: Logic blank seperat
        dbc.Row(
          dbc.Col(
               html.Br(), width={'size':3,"offset":1}
          )),# End of row
         
         dbc.Row([
          dbc.Col(
               html.Div(id='nifty_div'), width={'size':3,"offset":1}
               ), #end of Col
          dbc.Col(
               html.Div(id='bank_nifty_div'), width={'size':3,"offset":1}
               ) #end of Col     

        ]),# End of row

     
    
     dbc.Row([
          dbc.Col(
               html.H5(children='Top Gainers'), width={'size':3,"offset":1}
               ), #end of Col
          dbc.Col(
               html.H5(children='Top Losers'), width={'size':3,"offset":1}
               ) #end of Col     
     ]),# End of row
    
    #Content goes here
    dbc.Row(
      dbc.Col( html.Div(id='lastupdated1'), width={'size':3,"offset":1} ) #end of Col
    ),# End of row
    
    #Row Model
    #Timer Component for 1 minute Interval
    dcc.Interval(id='nsetabTimer', interval=60000, n_intervals=0),
        #Content Goes below
        dbc.Row([
        dbc.Col(
         dcc.Loading(id="loading-3",children=[    
         dash_table.DataTable(
        id='nse_top_gainer_table',
        columns=[
            {'name': 'symbol', 'id': 'symbol', 'type': 'text'},
            {'name': 'previousPrice', 'id': 'previousPrice', 'type': 'numeric'},
            {'name': 'ltp', 'id': 'ltp', 'type': 'numeric'},
            {'name': 'openPrice', 'id': 'openPrice', 'type': 'numeric'},
            {'name': 'highPrice', 'id': 'highPrice', 'type': 'numeric'},
            {'name': 'lowPrice', 'id': 'lowPrice', 'type': 'numeric'},
            {'name': 'pricePct', 'id': 'netPrice', 'type': 'numeric'},
            
        ],
        #data=get_nse_top_gainers().to_dict('records'),
        #filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=15,
        #black header
        style_header={
        'color': 'white',
        'backgroundColor': 'black',
        'fontweight':'bold'
       },
       #Gray cell
       style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
        style_cell={'textAlign':'left'},
        #TODO: Logic *** Style Condition for darkgreen above 2.5% and rest will be light green ***
        style_data_conditional=[
            #Positive Value for Change %
             {
                'if': {
                     'filter_query':'{netPrice} > 2.5', 
                    'column_id':'netPrice'
                    },
                  'backgroundColor':'green',
                  'color':'white'  
             },
             #Negative Value Change %
             {
                'if': {
                     'filter_query':'{netPrice} < 2.5', 
                    'column_id':'netPrice'
                    },
                  'backgroundColor':'lightgreen',
                  'color':'black'  
             },
         ],

        ),],type="dot",), 
        width={'size':3,"offset":1}
        ), #Col End 
        # Next Col
        dbc.Col(
        dcc.Loading(id="loading-4",children=[      
        dash_table.DataTable(
        id='nse_top_loser_table',
        columns=[
            {'name': 'symbol', 'id': 'symbol', 'type': 'text'},
            {'name': 'previousPrice', 'id': 'previousPrice', 'type': 'numeric'},
            {'name': 'ltp', 'id': 'ltp', 'type': 'numeric'},
            {'name': 'openPrice', 'id': 'openPrice', 'type': 'numeric'},
            {'name': 'highPrice', 'id': 'highPrice', 'type': 'numeric'},
            {'name': 'lowPrice', 'id': 'lowPrice', 'type': 'numeric'},
            {'name': 'pricePct', 'id': 'netPrice', 'type': 'numeric'},
            
        ],
        #data=get_nse_top_losers().to_dict('records'),
        #filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=15,
        #black header
        style_header={
        'color': 'white',
        'backgroundColor': 'black',
        'fontweight':'bold'
       },
       #Gray cell
       style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
        style_cell={'textAlign':'left'},
        #TODO: Logic *** Style Condition for darkred above 1.5% and rest will be pink ***
        style_data_conditional=[
            #Positive Value for Change %
             {
                'if': {
                     'filter_query':' {netPrice} > -1.5 && {netPrice} < 0', 
                    'column_id':'netPrice'
                    },
                  'backgroundColor':'pink',
                  'color':'black'  
             },
             #Negative Value Change %
             {
                'if': {
                     'filter_query':'{netPrice} < -1.5', 
                    'column_id':'netPrice'
                    },
                  'backgroundColor':'red',
                  'color':'white'  
             },
         ],
        ),],type="circle",), 
        width={'size':3,"offset":1}
        ) #Col End 
        ]),  #Row End

         #Charts Row
     dbc.Row(
        dbc.Col(
            html.Div([
            #dbc.Spinner(children=[dcc.Graph(id='portfolio_piechart'),dcc.Graph(id='portfolio_barchart'),],color="primary",type="grow",fullscreen=False,spinner_style={"width":"10rem","height":"10rem"})
            dcc.Loading(children=[dcc.Graph(id='adv_decline_chart')],color="blue",type="graph",fullscreen=False),
            ]),

            width={'size':6,"offset":1}
          ), #Col end
       ),  #Row End
	 ]), #End of Tab
		  
	dcc.Tab(label='StockAnalyzeTab', style=tab_style, selected_style=tab_selected_style,children=[
		  html.Div(children="Stock Analyze Tab"),
           dbc.Row([
            dbc.Col(dcc.Input(id="stock_symbol",type="text",placeholder="stock symbol",value='TATASTEEL',debounce=True),width={'size':3,"offset":1}),
            dbc.Col([ dcc.DatePickerRange(id='my-date-picker-range', min_date_allowed=date(1995, 8, 5), max_date_allowed=date(2020, 12, 10),
            initial_visible_month=date(2020, 12, 10), end_date=date(2019, 12, 10))
            ],width={'size':3,"offset":1}),
           
            ]),  #end of Row
           dbc.Row(
             dbc.Col(dcc.Loading(children=[dcc.Graph(id='stock_candlehart',style={'width':'180vh','height':'100vh'})],color="green",type="circle",fullscreen=False),
            width={'size':3,"offset":1}),
           ), #end of Row 
		  #Content Goes below
		  ]), #End of Tab
		  
	]), #End of Tabs	  

    
])

#Porfolio Tab Call backs
@app.callback(
    [
    Output('portfolioTable', 'data'),
    Output('lastupdated','children'),
    Output('portfolio_piechart', 'figure'),
    Output('portfolio_barchart', 'figure')
    ],
    [Input('portfolioTimer', 'n_intervals')]
    )
def portfolio_callback(n_intervals):
    print('Callback portfolio_callback called...')
    #Construct the portfolio values dynamically
    df1 = get_portfolio()
    data=df1.to_dict('records')
    lastupdated = "Last Updated: "+str(datetime.now())
    piechart = px.pie(data_frame = df1, values='invVal', names='broker', hole =.6,height=600,width=800)
    portfolio_bar = px.bar(df1, x="symbol", y=["invVal", "curVal", "pnlVal"], title="Stock inv cur pnlpct",height=600,width=900)
    

    return  data,lastupdated,piechart,portfolio_bar

#NSE TAB Callback
@app.callback(
    [
    Output('nse_top_gainer_table', 'data'),
    Output('nse_top_loser_table', 'data'),
    Output('lastupdated1','children'),
    Output('adv_decline_chart','figure'),
    Output('nifty_div', 'children'),
    Output('bank_nifty_div', 'children')
    ],
    [Input('nsetabTimer', 'n_intervals')]
    )
def nsetab_callback(n_intervals):
    print('Callback portfolio_callback called...')
    #Construct the portfolio values dynamically
    data = get_nse_top_gainers().to_dict('records')
    data1=get_nse_top_losers().to_dict('records')
    #data=df1.to_dict('records')
    lastupdated = "Last Updated: "+str(datetime.now())
    #piechart = px.pie(data_frame = df1, values='invVal', names='broker', hole =.6,height=400,width=800)
    #portfolio_bar = px.bar(df1, x="symbol", y=["invVal", "curVal", "pnlVal"], title="Stock inv cur pnlpct",height=600,width=900)
    df1= get_advances_declines()
    adv_dec_bar = px.bar(df1, x="indice", y=["advances", "declines", "unchanged"], title="NSE Advances declines",height=800,width=1200)
    nifty_dict =  get_index_quote('NIFTY 50')
    color_name='green'
    if float(nifty_dict['pChange'])<0:
        color_name='red'

    nifty_card = dbc.Card([
        dbc.CardHeader([html.H3("NIFTY50")]),
        dbc.CardBody([html.H5(nifty_dict['lastPrice'],style={'color':color_name}),html.P('Change :'+str(nifty_dict['change'])+'   '+str(nifty_dict['pChange'])+'%',style={'color':'red'})])
    ])
    bank_nifty_dict =  get_index_quote('NIFTY Bank')
    
    if float(bank_nifty_dict['pChange'])<0:
        color_name='red'

    bank_nifty_card = dbc.Card([
        dbc.CardHeader([html.H3("NIFTY BANK")]),
        dbc.CardBody([html.H5(bank_nifty_dict['lastPrice'],style={'color':color_name}),html.P('Change :'+str(bank_nifty_dict['change'])+'   '+str(bank_nifty_dict['pChange'])+'%',style={'color':color_name})])
    ])
    return  [data,data1,lastupdated,adv_dec_bar,nifty_card,bank_nifty_card]



#Stock chart callback
@app.callback(
    [Output('stock_candlehart', 'figure')],
    [Input('stock_symbol','value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')])
def update_stock_chart(value,start_date, end_date):
    print('Callback update_stock_chart called...'+value+', '+str(start_date)+', '+str(end_date))
    #string_prefix = 'You have selected: '
    '''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y %m, %d')
        #string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y %m, %d')
        #string_prefix = string_prefix + 'End Date: ' + end_date_string
    '''
    
    if start_date is not None:
        print('start_date is not none..') 
        if end_date is not None:
            print('end_date is not none..') 
            print('before calling.... historical..'+value+' ,'+str(start_date)+', '+str(end_date))
            #df = get_history(symbol=value, start=start_date.strftime('%Y,%m, %d'), end=end_date.strftime('%Y,%m,%d'))
            df = get_historical_data(value,start_date,end_date)
            #df = get_history(symbol=value, start=date(2019,12,10), end=date(2020,12,10))
            print('after calling.... historical')
            print(df.head(3))
            fig = go.Figure(data=[go.Candlestick(x=df.index.values,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
            return [fig]
    else:
        #df = get_historical_data(value,start_date,end_date)
        df = get_history(symbol=value, start=date(2019,12,10), end=date(2020,12,10))
        print('after calling.... historical')
        print(df.head(3))
        fig = go.Figure(data=[go.Candlestick(x=df.index.values,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
        return [fig]
        
    # Plot OHLC on 1st row
    #fig1 = fig.add_trace(go.Candlestick(x=df["Date"], open=df["AAPL.Open"], high=df["AAPL.High"], low=df["AAPL.Low"], close=df["AAPL.Close"], name="OHLC"), row=1, col=1)
    # Bar trace for volumes on 2nd row without legend
    #fig.add_trace(go.Bar(x=df['Date'], y=df['AAPL.Volume'], showlegend=False), row=2, col=1)
    # Do not show OHLC's rangeslider plot 
    #fig.update(layout_xaxis_rangeslider_visible=False)
    #if len(string_prefix) == len('You have selected: '):
    #    return 'Select a date to see it displayed here'
    #else:
    #    return string_prefix

if __name__ == '__main__':
    app.run_server(debug=True)