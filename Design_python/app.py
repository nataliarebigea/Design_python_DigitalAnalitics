import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# --- 1. GENERARE/CITIRE FIȘIER CSV ---
nume_fisier = 'baza_date_materiale.csv'

# Dacă fișierul CSV nu există, îl creăm automat (pentru a evita erorile la prima rulare)
if not os.path.exists(nume_fisier):
    date_initiale = pd.DataFrame({
        'Categorie': ['Parchet', 'Parchet', 'Parchet', 'Gresie', 'Gresie', 'Gresie', 'Mocheta', 'Mocheta', 'Microciment', 'Marmura'],
        'Nume_Model': ['Stejar Deschis', 'Nuc Masiv', 'Laminat Basic', 'Mata Antiderapanta', 'Lucioasa Premium', 'Portelanata', 'Office Gri', 'Plusata Bej', 'Industrial Extra', 'Calacatta Gold'],
        'Pret_mp': [80, 250, 45, 70, 150, 110, 50, 90, 300, 550],
        'Durabilitate_Ani': [15, 50, 10, 20, 30, 40, 5, 10, 35, 100],
        'Trafic': ['Mediu', 'Intens', 'Usor', 'Mediu', 'Intens', 'Intens', 'Intens', 'Mediu', 'Intens', 'Intens']
    })
    date_initiale.to_csv(nume_fisier, index=False)

# Citim datele din CSV
df = pd.read_csv(nume_fisier)

# --- 2. STILIZARE CSS (Sidebar vs Main Content) ---
SIDEBAR_STYLE = {
    "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "300px",
    "padding": "20px 20px", "backgroundColor": "#2c3e50", "color": "white",
    "boxShadow": "2px 0px 5px rgba(0,0,0,0.2)"
}

CONTENT_STYLE = {
    "marginLeft": "320px", "padding": "20px", "backgroundColor": "#ecf0f1",
    "minHeight": "100vh", "fontFamily": "Arial, sans-serif"
}

app = dash.Dash(__name__)

# --- 3. LAYOUT-UL APLICAȚIEI ---
app.layout = html.Div([
    
    # === SIDEBAR (Panoul din stânga) ===
    html.Div(style=SIDEBAR_STYLE, children=[
        html.H2("Filtre Catalog", style={'textAlign': 'center', 'borderBottom': '1px solid #7f8c8d', 'paddingBottom': '15px'}),
        
        html.Label("Categorie Material:", style={'marginTop': '20px', 'display': 'block', 'fontWeight': 'bold'}),
        dcc.Checklist(
            id='filtru-categorie',
            options=[{'label': f" {cat}", 'value': cat} for cat in df['Categorie'].unique()],
            value=df['Categorie'].unique().tolist(), # Toate selectate by default
            style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px', 'marginTop': '10px'}
        ),
        
        html.Label("Clasă Trafic:", style={'marginTop': '30px', 'display': 'block', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='filtru-trafic',
            options=[{'label': 'Toate', 'value': 'Toate'}] + [{'label': t, 'value': t} for t in df['Trafic'].unique()],
            value='Toate',
            clearable=False,
            style={'color': 'black', 'marginTop': '10px'}
        ),
        
        html.Label("Buget Maxim (RON/m²):", style={'marginTop': '30px', 'display': 'block', 'fontWeight': 'bold'}),
        dcc.Slider(
            id='filtru-pret', min=df['Pret_mp'].min(), max=df['Pret_mp'].max(),
            step=50, value=df['Pret_mp'].max(),
            marks={int(v): str(int(v)) for v in [50, 200, 400, 600]}
        ),
        
        html.Div(style={'marginTop': '50px', 'padding': '15px', 'backgroundColor': '#34495e', 'borderRadius': '8px'}, children=[
            html.H4("Info CSV", style={'margin': '0'}),
            html.P(f"Fișier conectat: {nume_fisier}", style={'fontSize': '12px', 'color': '#bdc3c7', 'margin': '5px 0 0 0'})
        ])
    ]),
    
    # === MAIN CONTENT (Zona principală) ===
    html.Div(style=CONTENT_STYLE, children=[
        html.H1("Dashboard Analiză Materiale & Design", style={'color': '#2c3e50', 'marginTop': '0'}),
        
        # Rândul 1: Metrici Rapide
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}, children=[
                html.H4("Produse Disponibile", style={'margin': '0', 'color': '#7f8c8d'}),
                html.H2(id='metric-count', style={'margin': '10px 0 0 0', 'color': '#2980b9'})
            ]),
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}, children=[
                html.H4("Preț Mediu (Selectie)", style={'margin': '0', 'color': '#7f8c8d'}),
                html.H2(id='metric-avg-price', style={'margin': '10px 0 0 0', 'color': '#27ae60'})
            ])
        ]),
        
        # Rândul 2: Vizualizări Statistice Complexe
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            # Scatter Plot (Corelație Preț vs Durabilitate)
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px'}, children=[
                dcc.Graph(id='grafic-corelatie')
            ]),
            # Box Plot (Distribuția prețurilor)
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px'}, children=[
                dcc.Graph(id='grafic-distributie')
            ])
        ]),
        
        # Rândul 3: Simulator Cameră (conectat la cel mai ieftin material din selecție)
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px'}, children=[
            html.H3("Simulator Buget (Folosind cel mai ieftin produs din filtre)"),
            html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
                html.Div(style={'flex': '1'}, children=[
                    html.Label("Lungime Cameră (m):"),
                    dcc.Slider(id='sim-lungime', min=2, max=10, step=1, value=4),
                    html.Br(),
                    html.Label("Lățime Cameră (m):"),
                    dcc.Slider(id='sim-latime', min=2, max=10, step=1, value=3),
                ]),
                html.Div(style={'flex': '2'}, children=[
                    html.H4(id='rezultat-simulator', style={'color': '#c0392b', 'textAlign': 'center', 'marginTop': '30px'})
                ])
            ])
        ])
    ])
])

# --- 4. CALLBACK-URI (Logica de filtrare și actualizare) ---
@app.callback(
    [Output('metric-count', 'children'),
     Output('metric-avg-price', 'children'),
     Output('grafic-corelatie', 'figure'),
     Output('grafic-distributie', 'figure'),
     Output('rezultat-simulator', 'children')],
    [Input('filtru-categorie', 'value'),
     Input('filtru-trafic', 'value'),
     Input('filtru-pret', 'value'),
     Input('sim-lungime', 'value'),
     Input('sim-latime', 'value')]
)
def update_dashboard(categorii, trafic, pret_max, lungime, latime):
    # 1. Aplicare Filtre pe DataFrame-ul original (CSV)
    df_filtrat = df[df['Categorie'].isin(categorii)]
    df_filtrat = df_filtrat[df_filtrat['Pret_mp'] <= pret_max]
    if trafic != 'Toate':
        df_filtrat = df_filtrat[df_filtrat['Trafic'] == trafic]
        
    # Dacă utilizatorul a filtrat prea mult și nu mai există produse
    if df_filtrat.empty:
        return "0", "0 RON", go.Figure().update_layout(title="Fără date"), go.Figure().update_layout(title="Fără date"), "Niciun material nu corespunde filtrelor."

    # 2. Calcul Metrici Rapide
    count = len(df_filtrat)
    avg_price = df_filtrat['Pret_mp'].mean()
    
    # 3. Grafic Statistic: Scatter Plot (Relația dintre Preț, Durabilitate și Categorie)
    fig_scatter = px.scatter(
        df_filtrat, x="Pret_mp", y="Durabilitate_Ani", 
        color="Categorie", size="Pret_mp", hover_name="Nume_Model",
        title="Corelație: Preț vs. Durabilitate (ani)",
        labels={"Pret_mp": "Preț (RON/m²)", "Durabilitate_Ani": "Durată viață estimată"}
    )
    fig_scatter.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
    
    # 4. Grafic Statistic: Box Plot (Cum variază prețurile în interiorul unei categorii)
    fig_box = px.box(
        df_filtrat, x="Categorie", y="Pret_mp", color="Categorie",
        title="Distribuția Prețurilor pe Categorii",
        labels={"Pret_mp": "Preț (RON/m²)", "Categorie": ""}
    )
    fig_box.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white", showlegend=False)
    
    # 5. Logica pentru Simulatorul de Cameră (Căutăm cel mai ieftin produs din selecție)
    produs_optim = df_filtrat.loc[df_filtrat['Pret_mp'].idxmin()]
    aria = lungime * latime
    cost_est = aria * produs_optim['Pret_mp']
    
    text_simulator = f"Proiect {aria} m² | Material Recomandat: {produs_optim['Nume_Model']} ({produs_optim['Categorie']}) | Cost Material: {cost_est:,.0f} RON"

    return f"{count} produse", f"{avg_price:.0f} RON/m²", fig_scatter, fig_box, text_simulator

if __name__ == '__main__':
    app.run(debug=True)