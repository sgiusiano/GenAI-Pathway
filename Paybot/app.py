import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Add src directory to path for module resolution
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_loader import load_all_files_from_directory, parse_filename_metadata
from paybot import Paybot

st.set_page_config(
    page_title="Paybot - Análisis de Nómina",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apex America Style Inspiration
st.markdown("""
<style>
    /* Import Roboto font - Apex America style */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap');
    
    /* Global styling - Clean white background */
    .stApp {
        font-family: 'Roboto', sans-serif;
        background: #ffffff;
        color: #333333;
    }
    
    /* Main content area - Clean white design */
    .main .block-container {
        background: #ffffff;
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Header styling - Modern and bold */
    .main h1 {
        color: #333333;
        font-weight: 600;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -0.02em;
    }
    
    /* Subheaders - Clean hierarchy */
    .main h2 {
        color: #333333;
        font-weight: 600;
        font-size: 1.75rem;
        margin: 2rem 0 1rem 0;
        letter-spacing: -0.01em;
    }
    
    .main h3 {
        color: #333333;
        font-weight: 600;
        font-size: 1.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    
    .main h4 {
        color: #666666;
        font-weight: 500;
        font-size: 1.2rem;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Metric cards styling - Apex style clean cards */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        border-color: #20D167;
    }
    
    [data-testid="metric-container"] > div:first-child {
        font-weight: 500;
        color: #666666;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="metric-container"] > div:nth-child(2) {
        font-weight: 600;
        color: #333333;
        font-size: 2.5rem;
        line-height: 1.1;
    }
    
    [data-testid="metric-container"] > div:nth-child(3) {
        color: #20D167;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Sidebar styling - Clean dark sidebar */
    .css-1d391kg {
        background: #2c2c2c;
        border-right: 1px solid #e0e0e0;
    }
    
    .css-1d391kg h2 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .css-1d391kg .stSelectbox label,
    .css-1d391kg .stTextInput label,
    .css-1d391kg .stButton button {
        color: #ffffff;
        font-weight: 400;
    }
    
    /* Button styling - Apex green accent */
    .stButton > button {
        background: #20D167;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        text-transform: none;
    }
    
    .stButton > button:hover {
        background: #1bb05a;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(32, 209, 103, 0.3);
    }
    
    /* Tab styling - Clean and minimal */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid #e0e0e0;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 0;
        padding: 1rem 1.5rem;
        font-weight: 500;
        color: #666666;
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
        margin-bottom: -1px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #20D167;
        border-bottom-color: #20D167;
    }
    
    .stTabs [aria-selected="true"] {
        color: #20D167 !important;
        border-bottom-color: #20D167 !important;
        font-weight: 600;
    }
    
    /* Alert styling - Clean and minimal */
    .stAlert {
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Info boxes - Apex style */
    .stInfo {
        background: #f0f9ff;
        border-color: #30ccec;
        color: #0369a1;
    }
    
    .stSuccess {
        background: #f0fdf4;
        border-color: #20D167;
        color: #166534;
    }
    
    .stWarning {
        background: #fffbeb;
        border-color: #f59e0b;
        color: #92400e;
    }
    
    /* Chart containers - Clean white cards */
    .stPlotlyChart {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Custom sections */
    .section-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 2rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
    }
    
    /* Separators - Minimal lines */
    hr {
        border: none;
        height: 1px;
        background: #e0e0e0;
        margin: 2rem 0;
    }
    
    /* Text styling - Roboto clean text */
    .main p {
        color: #666666;
        line-height: 1.6;
        font-size: 1rem;
        font-weight: 400;
    }
    
    /* Status indicators - Apex colors */
    .status-green {
        color: #20D167;
        font-weight: 600;
    }
    
    .status-red {
        color: #ef4444;
        font-weight: 600;
    }
    
    .status-yellow {
        color: #f59e0b;
        font-weight: 600;
    }
    
    /* Loading spinner */
    .stSpinner {
        color: #20D167;
    }
    
    /* Content sections */
    .content-section {
        margin: 2rem 0;
        padding: 1.5rem 0;
    }
    
    /* Clean markdown styling */
    .main .stMarkdown {
        margin-bottom: 1rem;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 0.75rem;
        font-family: 'Roboto', sans-serif;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #20D167;
        box-shadow: 0 0 0 2px rgba(32, 209, 103, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Apex America Style Header with Logo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; padding: 2rem 0;">
        <div style="margin-bottom: 1.5rem;">
            <img src="https://apexamerica.com/wp-content/uploads/elementor/thumbs/logo-qpm4gr043o84a4u96y70tvkf2pcel7jgl6clcyap6o.png" 
                 alt="Apex America Logo" 
                 style="height: 60px; margin-bottom: 1rem;">
        </div>
        <h1 style="margin-bottom: 1rem; color: #333333; font-weight: 600;">Paybot Analytics</h1>
        <p style="font-size: 1.1rem; color: #666666; font-weight: 400; max-width: 600px; margin: 0 auto; line-height: 1.5;">
            Plataforma inteligente de análisis de nómina con insights automatizados para decisiones financieras estratégicas
        </p>
        <div style="margin-top: 1.5rem;">
            <span style="background: #20D167; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
                Powered by Apex America
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Apex Style Sidebar
    st.sidebar.markdown("""
    <div style="margin-bottom: 2rem;">
        <h2 style="color: #ffffff; font-size: 1.3rem; margin-bottom: 1rem; font-weight: 600;">⚙️ Configuración</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Default directory path
    default_path = "/Users/santiagoarielgiusiano/Desktop/GenAI Pathway/Paybot/data/raw"
    
    # Directory input
    data_directory = st.sidebar.text_input(
        "Ruta del Directorio de Datos",
        value=default_path,
        help="Ruta al directorio que contiene los archivos CSV de nómina"
    )
    
    # Load data button
    load_data = st.sidebar.button("🔄 Cargar Datos", type="primary")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'metadata_summary' not in st.session_state:
        st.session_state.metadata_summary = None
    
    # Load data when button is clicked
    if load_data:
        with st.spinner("Cargando datos..."):
            try:
                # Load all files from directory
                data = load_all_files_from_directory(data_directory)
                st.session_state.data = data
                
                # Create metadata summary
                metadata_summary = {
                    'total_rows': len(data),
                    'total_files': data['source_file'].nunique(),
                    'companies': data['file_company'].unique().tolist(),
                    'months': sorted(data['file_month'].unique().tolist()),
                    'years': sorted(data['file_year'].unique().tolist()),
                    'categories': data['file_category'].unique().tolist(),
                    'columns': data.columns.tolist()
                }
                st.session_state.metadata_summary = metadata_summary
                
                st.success(f"✅ Datos cargados exitosamente: {len(data):,} registros de {data['source_file'].nunique()} archivos!")
                
            except Exception as e:
                st.error(f"❌ Error al cargar datos: {str(e)}")
                return
    
    # Display data if loaded
    if st.session_state.data is not None:
        data = st.session_state.data
        # Convert to numeric, handling decimal numbers with comma separator
        data['Monto_numeric'] = pd.to_numeric(data['Monto'].str.replace(',', '.'), errors='coerce')
        metadata = st.session_state.metadata_summary
        
        # Create tabs for different views
        tabs = st.tabs(["📊 Resumen Ejecutivo", "Análisis detallado", "Paybot insghts & Recomms"])
        
        with tabs[0]:
            st.header("📊 Resumen Ejecutivo - Reporte Mensual de Nómina")
            
            # Metadata summary
            col1, col2 = st.columns(2)
            
            col_info1, col_info2, col_info3, col_info4 = st.columns(4)
            with col_info1:
                st.subheader("Empresas")
                st.write(", ".join(metadata['companies']))
            with col_info2:
                st.subheader("Meses")
                st.write(", ".join(metadata['months']))
            with col_info3:
                st.subheader("Años")
                st.write(", ".join(metadata['years']))
            with col_info4:
                st.subheader("Categorías")
                st.write(", ".join(metadata['categories']))
                
            # Calcular montos y empleados por mes
            data['YearMonth'] = data['file_year'] + '-' + data['file_month']
            monthly_stats = data.groupby('YearMonth').agg({
                'Monto_numeric': 'sum',
                'Legajo': 'nunique'  # Contar empleados únicos por mes
            }).sort_index()
            monthly_stats.columns = ['Monto_Total', 'Cantidad_Empleados']
            
            if len(monthly_stats) >= 2:
                current_month = monthly_stats.index[-1]
                previous_month = monthly_stats.index[-2]
                
                # Cálculos para KPIs ejecutivos
                current_total = monthly_stats.loc[current_month, 'Monto_Total']
                previous_total = monthly_stats.loc[previous_month, 'Monto_Total']
                current_employees = monthly_stats.loc[current_month, 'Cantidad_Empleados']
                previous_employees = monthly_stats.loc[previous_month, 'Cantidad_Empleados']
                
                delta_monto = ((current_total - previous_total) / previous_total) * 100
                delta_empleados = ((current_employees - previous_employees) / previous_employees) * 100
                delta_empleados_num = current_employees - previous_employees
                current_cost_per_employee = current_total / current_employees if current_employees > 0 else 0
                previous_cost_per_employee = previous_total / previous_employees if previous_employees > 0 else 0
                delta_cost_per_employee = ((current_cost_per_employee - previous_cost_per_employee) / previous_cost_per_employee) * 100 if previous_cost_per_employee > 0 else 0
                
                # Header ejecutivo
                st.markdown("---")
                st.markdown("## 📊 **DASHBOARD EJECUTIVO** - Análisis Mensual de Nómina")
                
                # KPIs principales en una fila destacada
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                
                with kpi1:
                    st.metric(
                        label="💰 **NÓMINA TOTAL**",
                        value=f"${current_total:,.0f}".replace(',', '.'),
                        delta=f"{delta_monto:+.1f}%" if abs(delta_monto) >= 0.1 else "Sin cambios",
                        delta_color="inverse" if delta_monto > 5 else "normal"
                    )
                
                with kpi2:
                    st.metric(
                        label="👥 **DOTACIÓN**", 
                        value=f"{current_employees:,}".replace(',', '.'),
                        delta=f"{delta_empleados_num:+d}" if delta_empleados != 0 else "Sin cambios",
                        delta_color="normal"
                    )
                
                with kpi3:
                    st.metric(
                        label="📈 **COSTO/EMPLEADO**",
                        value=f"${current_cost_per_employee:,.0f}".replace(',', '.'),
                        delta=f"{delta_cost_per_employee:+.1f}%" if abs(delta_cost_per_employee) >= 0.1 else "Sin cambios",
                        delta_color="inverse" if delta_cost_per_employee > 3 else "normal"
                    )
                
                with kpi4:
                    # Determinar estado general
                    if abs(delta_monto) <= 3 and abs(delta_empleados) <= 2:
                        status = "🟢 ESTABLE"
                        status_color = "normal"
                    elif delta_monto > 10 or abs(delta_empleados) > 5:
                        status = "🔴 REQUIERE ATENCIÓN"
                        status_color = "inverse"
                    else:
                        status = "🟡 MONITOREAR"
                        status_color = "normal"
                    
                    st.metric(
                        label="⚡ **STATUS**",
                        value=status,
                        delta=f"vs {previous_month}",
                        delta_color=status_color
                    )
                
                # Sección de análisis comparativo detallado
                st.markdown("### 📋 **Análisis Comparativo Detallado**")
                
                col_prev, col_vs, col_curr = st.columns([2, 1, 2])
                
                with col_prev:
                    st.markdown(f"#### 📅 **{previous_month.upper()}**")
                    st.markdown(f"""
                    - **Nómina Total:** ${previous_total:,.0f}
                    - **Empleados:** {previous_employees:,}
                    - **Promedio/Empleado:** ${previous_cost_per_employee:,.0f}
                    """.replace(',', '.'))
                
                with col_vs:
                    st.markdown("#### ⚖️")
                    if delta_monto > 0:
                        st.markdown("📈 **INCREMENTO**")
                    elif delta_monto < 0:
                        st.markdown("📉 **REDUCCIÓN**") 
                    else:
                        st.markdown("➡️ **ESTABLE**")
                
                with col_curr:
                    st.markdown(f"#### 📅 **{current_month.upper()}**")
                    st.markdown(f"""
                    - **Nómina Total:** ${current_total:,.0f}
                    - **Empleados:** {current_employees:,}
                    - **Promedio/Empleado:** ${current_cost_per_employee:,.0f}
                    """.replace(',', '.'))
                
                # Alertas ejecutivas si hay variaciones significativas
                if abs(delta_monto) > 5 or abs(delta_empleados) > 3:
                    st.markdown("### 🚨 **Alertas para Revisión Ejecutiva**")
                    
                    alerts = []
                    if delta_monto > 10:
                        alerts.append(f"• **Incremento significativo en nómina:** +{delta_monto:.1f}% ({(current_total - previous_total):,.0f} adicionales)")
                    elif delta_monto < -5:
                        alerts.append(f"• **Reducción en nómina:** {delta_monto:.1f}% ({abs(current_total - previous_total):,.0f} menos)")
                    
                    if delta_empleados > 5:
                        alerts.append(f"• **Incremento notable de personal:** +{delta_empleados} empleados")
                    elif delta_empleados < -3:
                        alerts.append(f"• **Reducción de personal:** {delta_empleados} empleados")
                    
                    if abs(delta_cost_per_employee) > 5:
                        direction = "incremento" if delta_cost_per_employee > 0 else "reducción"
                        alerts.append(f"• **{direction.capitalize()} en costo promedio por empleado:** {delta_cost_per_employee:+.1f}%")
                    
                    for alert in alerts:
                        st.warning(alert)
                
                st.markdown("---")
            
        with tabs[1]:
            st.header("🔍 Análisis Detallado de Variaciones")
            st.markdown("Análisis profundo de las variaciones entre períodos para identificar impactos por centro de costo y conceptos.")
            
            if len(monthly_stats) >= 2:
                current_month = monthly_stats.index[-1]
                previous_month = monthly_stats.index[-2]
                
                # Filtrar datos por mes
                data_current = data[data['YearMonth'] == current_month].copy()
                data_previous = data[data['YearMonth'] == previous_month].copy()
                
                # ===== ANÁLISIS POR CENTRO DE COSTO =====
                st.markdown("---")
                st.markdown("## 🏢 **ANÁLISIS POR CENTRO DE COSTO**")
                
                # Nómina por centro de costo
                nomina_current = data_current.groupby('CECO').agg({
                    'Monto_numeric': 'sum',
                    'Legajo': 'nunique'
                }).reset_index()
                nomina_current.columns = ['CECO', 'Monto_Actual', 'Empleados_Actual']
                
                nomina_previous = data_previous.groupby('CECO').agg({
                    'Monto_numeric': 'sum', 
                    'Legajo': 'nunique'
                }).reset_index()
                nomina_previous.columns = ['CECO', 'Monto_Anterior', 'Empleados_Anterior']
                
                # Merge para comparar
                nomina_comparison = pd.merge(nomina_current, nomina_previous, on='CECO', how='outer').fillna(0)
                nomina_comparison['Variacion_Monto'] = nomina_comparison['Monto_Actual'] - nomina_comparison['Monto_Anterior']
                nomina_comparison['Variacion_Empleados'] = nomina_comparison['Empleados_Actual'] - nomina_comparison['Empleados_Anterior']
                nomina_comparison['Variacion_Pct'] = ((nomina_comparison['Monto_Actual'] - nomina_comparison['Monto_Anterior']) / nomina_comparison['Monto_Anterior'] * 100).fillna(0)
                nomina_comparison['Variacion_Abs'] = abs(nomina_comparison['Variacion_Monto'])
                
                # TOP 5 Variaciones de Nómina por Centro de Costo
                st.markdown("### 📊 **TOP 5 - Variaciones de Nómina por Centro de Costo**")
                top5_nomina = nomina_comparison.nlargest(5, 'Variacion_Abs')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📈 **Mayores Variaciones Absolutas**")
                    for _, row in top5_nomina.iterrows():
                        delta_color = "🔴" if row['Variacion_Monto'] < 0 else "🟢"
                        st.markdown(f"""
                        **{row['CECO']}**
                        - Variación: {delta_color} ${row['Variacion_Monto']:,.0f} ({row['Variacion_Pct']:+.1f}%)
                        - Empleados: {row['Empleados_Actual']:.0f} ({row['Variacion_Empleados']:+.0f})
                        """.replace(',', '.'))
                
                with col2:
                    # Gráfico de barras moderno
                    import plotly.express as px
                    fig_nomina = px.bar(
                        top5_nomina, 
                        x='CECO', 
                        y='Variacion_Monto',
                        title=f'<b>Variaciones de Nómina por Centro de Costo</b><br><span style="font-size:12px; color:#666666;">{previous_month} vs {current_month}</span>',
                        color='Variacion_Monto',
                        color_continuous_scale=['#ef4444', '#f59e0b', '#20D167'],
                        labels={'Variacion_Monto': 'Variación ($)', 'CECO': 'Centro de Costo'}
                    )
                    fig_nomina.update_layout(
                        height=400, 
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family="Roboto, sans-serif", size=12, color="#333333"),
                        title_font=dict(size=16, color="#333333", family="Roboto"),
                        xaxis=dict(showgrid=False, showline=True, linecolor='#e0e0e0', tickfont=dict(color="#666666")),
                        yaxis=dict(showgrid=True, gridcolor='#f5f5f5', showline=True, linecolor='#e0e0e0', tickfont=dict(color="#666666"))
                    )
                    st.plotly_chart(fig_nomina, use_container_width=True)
                
                # TOP 5 Montos Totales por Centro de Costo
                st.markdown("### 💰 **TOP 5 - Montos Totales por Centro de Costo**")
                top5_montos = nomina_comparison.nlargest(5, 'Monto_Actual')
                
                col3, col4 = st.columns(2)
                
                with col3:
                    st.markdown("#### 🏆 **Centros de Costo con Mayor Inversión**")
                    for _, row in top5_montos.iterrows():
                        participacion = (row['Monto_Actual'] / nomina_comparison['Monto_Actual'].sum()) * 100
                        st.markdown(f"""
                        **{row['CECO']}**
                        - Monto Actual: ${row['Monto_Actual']:,.0f}
                        - Participación: {participacion:.1f}% del total
                        - Empleados: {row['Empleados_Actual']:.0f}
                        """.replace(',', '.'))
                
                with col4:
                    # Gráfico de participación moderno
                    fig_pie = px.pie(
                        top5_montos, 
                        values='Monto_Actual', 
                        names='CECO',
                        title=f'<b>Distribución de Nómina</b><br><span style="font-size:12px; color:#666666;">{current_month}</span>',
                        color_discrete_sequence=['#20D167', '#30ccec', '#685ae6', '#f59e0b', '#ef4444']
                    )
                    fig_pie.update_layout(
                        height=400,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family="Roboto, sans-serif", size=12, color="#333333"),
                        title_font=dict(size=16, color="#333333", family="Roboto"),
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05,
                            font=dict(size=10, color="#666666")
                        )
                    )
                    fig_pie.update_traces(
                        textposition='inside', 
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>',
                        textfont_size=10,
                        textfont_color='white'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # ===== ANÁLISIS POR CONCEPTOS =====
                # Filtrar conceptos que no contengan "ajustes" o "Aj." (case insensitive)
                ajuste_pattern = r'ajuste|aj\.|Aj|Anses'
                data_current_filtered = data_current[~data_current['Descripción'].str.contains(ajuste_pattern, case=False, na=False)]
                data_previous_filtered = data_previous[~data_previous['Descripción'].str.contains(ajuste_pattern, case=False, na=False)]

                st.markdown("---")
                st.markdown("## 💼 **ANÁLISIS POR CONCEPTOS**")
                st.markdown(f"*Nota: Se excluyen conceptos que contengan {ajuste_pattern} para mayor precisión del análisis.*")                
                
                
                # Conceptos por mes (sin ajustes)
                conceptos_current = data_current_filtered.groupby('Descripción')['Monto_numeric'].sum().reset_index()
                conceptos_current.columns = ['Concepto', 'Monto_Actual']
                
                conceptos_previous = data_previous_filtered.groupby('Descripción')['Monto_numeric'].sum().reset_index()
                conceptos_previous.columns = ['Concepto', 'Monto_Anterior']
                
                # Merge para encontrar diferencias
                conceptos_comparison = pd.merge(conceptos_current, conceptos_previous, on='Concepto', how='outer').fillna(0)
                conceptos_comparison['Variacion_Monto'] = conceptos_comparison['Monto_Actual'] - conceptos_comparison['Monto_Anterior']
                conceptos_comparison['Variacion_Pct'] = ((conceptos_comparison['Monto_Actual'] - conceptos_comparison['Monto_Anterior']) / conceptos_comparison['Monto_Anterior'] * 100).fillna(0)
                conceptos_comparison['Variacion_Abs'] = abs(conceptos_comparison['Variacion_Monto'])
                
                # Identificar conceptos nuevos y eliminados
                conceptos_nuevos = conceptos_comparison[conceptos_comparison['Monto_Anterior'] == 0]
                conceptos_eliminados = conceptos_comparison[conceptos_comparison['Monto_Actual'] == 0]
                conceptos_modificados = conceptos_comparison[(conceptos_comparison['Monto_Anterior'] > 0) & (conceptos_comparison['Monto_Actual'] > 0)]
                
                # TOP Variaciones de Conceptos
                st.markdown("### 📋 **Variaciones de Conceptos entre Períodos**")
                
                col5, col6, col7 = st.columns([1, 1, 1.2])
                
                with col5:
                    st.markdown("#### 🆕 **Conceptos Nuevos**")
                    if len(conceptos_nuevos) > 0:
                        for _, row in conceptos_nuevos.head(5).iterrows():
                            concepto_name = row['Concepto'][:40] + "..." if len(row['Concepto']) > 40 else row['Concepto']
                            st.markdown(f"""
                            **{concepto_name}**
                            - Monto: ${row['Monto_Actual']:,.0f}
                            """.replace(',', '.'))
                    else:
                        st.info("No hay conceptos nuevos")
                
                with col6:
                    st.markdown("#### ❌ **Conceptos Eliminados**")
                    if len(conceptos_eliminados) > 0:
                        for _, row in conceptos_eliminados.head(5).iterrows():
                            concepto_name = row['Concepto'][:40] + "..." if len(row['Concepto']) > 40 else row['Concepto']
                            st.markdown(f"""
                            **{concepto_name}**
                            - Monto Anterior: ${row['Monto_Anterior']:,.0f}
                            """.replace(',', '.'))
                    else:
                        st.info("No hay conceptos eliminados")
                
                with col7:
                    st.markdown("#### 📊 **Mayores Variaciones**")
                    top_variaciones = conceptos_modificados.nlargest(5, 'Variacion_Abs')
                    if len(top_variaciones) > 0:
                        for _, row in top_variaciones.iterrows():
                            delta_icon = "📈" if row['Variacion_Monto'] > 0 else "📉"
                            concepto_name = row['Concepto'][:35] + "..." if len(row['Concepto']) > 35 else row['Concepto']
                            st.markdown(f"""
                            **{concepto_name}**
                            - {delta_icon} {row['Variacion_Pct']:+.1f}%
                            - ${row['Variacion_Monto']:+,.0f}
                            """.replace(',', '.'))
                    else:
                        st.info("No hay variaciones significativas")
                
                # Resumen ejecutivo de impactos
                st.markdown("---")
                st.markdown("### 🎯 **Resumen Ejecutivo de Impactos**")
                
                total_variacion = nomina_comparison['Variacion_Monto'].sum()
                conceptos_nuevos_total = conceptos_nuevos['Monto_Actual'].sum()
                conceptos_eliminados_total = conceptos_eliminados['Monto_Anterior'].sum()
                
                col8, col9, col10 = st.columns(3)
                
                with col8:
                    st.metric(
                        "💹 **Impacto Total**",
                        f"${total_variacion:,.0f}".replace(',', '.'),
                        f"{(total_variacion/nomina_comparison['Monto_Anterior'].sum()*100):+.1f}%"
                    )
                
                with col9:
                    st.metric(
                        "🆕 **Conceptos Nuevos**",
                        f"${conceptos_nuevos_total:,.0f}".replace(',', '.'),
                        f"{len(conceptos_nuevos)} conceptos"
                    )
                
                with col10:
                    st.metric(
                        "❌ **Conceptos Eliminados**",
                        f"${conceptos_eliminados_total:,.0f}".replace(',', '.'),
                        f"{len(conceptos_eliminados)} conceptos"
                    )
            
            else:
                st.warning("⚠️ Se necesitan al menos dos períodos para realizar el análisis comparativo.")
                st.info("Carga datos de múltiples meses para visualizar variaciones y tendencias.")

        with tabs[2]:
            st.header("🤖 Paybot Insights & Recomendaciones")
            st.markdown("Análisis inteligente impulsado por IA para insights ejecutivos y recomendaciones estratégicas")
            
            # AI Configuration Section
            st.markdown("---")
            st.markdown("### ⚙️ **Configuración de IA**")
            
            # Check for environment variables
            import os
            openai_key_available = bool(os.getenv('OPENAI_API_KEY'))
            
            if openai_key_available:
                st.success("✅ OpenAI API Key detectada en variables de entorno")
            else:
                st.error("❌ OpenAI API Key no encontrada en variables de entorno")
                st.info("Configura la variable de entorno OPENAI_API_KEY para usar esta funcionalidad")
            
            # Model configuration
            col_model1, col_model2 = st.columns(2)
            with col_model1:
                model_choice = st.selectbox(
                    "Modelo de IA",
                    ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                    index=0,
                    help="Selecciona el modelo de OpenAI para el análisis"
                )
            
            with col_model2:
                temperature = st.slider(
                    "Temperatura (Creatividad)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.1,
                    step=0.1,
                    help="Controla la creatividad del análisis (0.0 = más enfocado, 1.0 = más creativo)"
                )
            
            # Generate Analysis Button
            if st.button("🚀 Generar Análisis IA", type="primary", use_container_width=True):
                if not openai_key_available:
                    st.error("❌ No se puede proceder sin OpenAI API Key en variables de entorno")
                elif len(monthly_stats) < 2:
                    st.warning("⚠️ Se necesitan al menos dos períodos para el análisis IA")
                else:
                    try:
                        with st.spinner("🤖 Analizando datos con IA... Esto puede tomar unos momentos."):
                            # Initialize Paybot (will use environment variables)
                            paybot = Paybot(
                                model_name=model_choice,
                                temperature=temperature
                            )
                            
                            # Generate comprehensive report
                            report = paybot.generate_comprehensive_report(data)
                            
                            if "error" in report:
                                st.error(f"❌ Error en el análisis: {report['error']}")
                            else:
                                # Display results
                                st.success("✅ Análisis IA completado exitosamente!")
                                
                                # Executive Summary
                                st.markdown("---")
                                st.markdown("## 📊 **Resumen Ejecutivo IA**")
                                st.markdown(
                                    f"""<div style="background: #f0fdf4; border-left: 4px solid #20D167; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                                    {report['executive_summary']}
                                    </div>""", 
                                    unsafe_allow_html=True
                                )
                                
                                # Risk Assessment
                                st.markdown("---")
                                st.markdown("## ⚠️ **Evaluación de Riesgos**")
                                st.markdown(
                                    f"""<div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                                    {report['risk_assessment']}
                                    </div>""", 
                                    unsafe_allow_html=True
                                )
                                
                                # Trend Analysis
                                st.markdown("---")
                                st.markdown("## 📈 **Análisis de Tendencias**")
                                st.markdown(
                                    f"""<div style="background: #f0f9ff; border-left: 4px solid #30ccec; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                                    {report['trend_analysis']}
                                    </div>""", 
                                    unsafe_allow_html=True
                                )
                                
                                # KPIs Summary
                                st.markdown("---")
                                st.markdown("## 📋 **KPIs Calculados**")
                                
                                if hasattr(report.get('kpis'), 'current_total'):
                                    kpis = report['kpis']
                                    
                                    # KPIs in columns
                                    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                                    
                                    with kpi_col1:
                                        st.metric(
                                            "💰 Variación Total",
                                            f"${kpis.delta_amount:,.0f}".replace(',', '.'),
                                            f"{kpis.delta_percentage:+.1f}%"
                                        )
                                    
                                    with kpi_col2:
                                        st.metric(
                                            "👥 Cambio Empleados",
                                            f"{kpis.delta_employees:+d}",
                                            f"{((kpis.delta_employees/kpis.previous_employees)*100):+.1f}%" if kpis.previous_employees > 0 else "N/A"
                                        )
                                    
                                    with kpi_col3:
                                        st.metric(
                                            "📊 Costo/Empleado",
                                            f"${kpis.cost_per_employee_current:,.0f}".replace(',', '.'),
                                            f"{kpis.delta_cost_per_employee:+.1f}%"
                                        )
                                    
                                    with kpi_col4:
                                        status_color = "🟢" if "ESTABLE" in kpis.status else "🔴" if "ATENCIÓN" in kpis.status else "🟡"
                                        st.metric(
                                            "⚡ Status",
                                            status_color,
                                            kpis.period_comparison
                                        )
                                
                                # Additional Info
                                st.markdown("---")
                                st.markdown("### 🔧 **Información Técnica**")
                                st.info(f"""
                                **Modelo utilizado:** {model_choice}  
                                **Temperatura:** {temperature}  
                                **Períodos analizados:** {len(monthly_stats)}  
                                **Monitoreo:** ❌ Sin monitoreo LangSmith
                                """)
                                
                    except Exception as e:
                        st.error(f"❌ Error durante el análisis: {str(e)}")
                        st.info("💡 Verifica que tu API key sea válida y que tengas créditos disponibles en OpenAI")
            
            # Information about the AI features
            st.markdown("---")
            st.markdown("### 💡 **Sobre el Análisis IA**")
            
            with st.expander("🔍 ¿Qué incluye el análisis IA?"):
                st.markdown("""
                **Resumen Ejecutivo:**
                - Análisis financiero comprehensivo
                - Identificación de tendencias críticas
                - Recomendaciones estratégicas específicas
                - Alertas para decisiones inmediatas
                
                **Evaluación de Riesgos:**
                - Análisis de compliance y regulaciones
                - Identificación de variaciones anómalas
                - Evaluación de sostenibilidad de costos
                - Recomendaciones de mitigación
                
                **Análisis de Tendencias:**
                - Patrones históricos identificados
                - Proyecciones para períodos futuros
                - Factores que impulsan cambios
                - Oportunidades de optimización
                """)
            
            with st.expander("🛡️ Seguridad y Privacidad"):
                st.markdown("""
                - **Datos seguros:** Tu información nunca se almacena permanentemente
                - **APIs oficiales:** Utilizamos únicamente APIs oficiales de OpenAI
                - **Monitoreo opcional:** LangSmith proporciona trazabilidad mejorada
                - **Configuración local:** Todas las claves se mantienen en tu sesión
                """)
            
            with st.expander("⚙️ Configuración Recomendada"):
                st.markdown("""
                **Para análisis ejecutivo (recomendado):**
                - Modelo: GPT-4
                - Temperatura: 0.1 (más enfocado)
                
                **Para análisis exploratorio:**
                - Modelo: GPT-4-turbo
                - Temperatura: 0.3 (más creativo)
                
                **Para pruebas rápidas:**
                - Modelo: GPT-3.5-turbo
                - Temperatura: 0.1
                """)
    
    else:
        # Show instructions when no data is loaded
        st.info("👆 Haz clic en 'Cargar Datos' en la barra lateral para comenzar a cargar tus archivos de nómina")
        
        st.markdown("""
        ### 📖 Cómo usar esta aplicación:
        
        1. **Configurar directorio de datos** - Ingresa la ruta a tus archivos CSV en la barra lateral
        2. **Hacer clic en 'Cargar Datos'** - La aplicación cargará automáticamente todos los archivos CSV y analizará metadatos
        3. **Explorar los datos** - Usa las pestañas para ver datos, análisis y detalles de archivos
        
        ### 📁 Convención de nombres de archivos:
        Tus archivos CSV deben seguir este patrón: `empresa_mes_año_categoria.csv`
        
        **Ejemplo:** `CIMSA_05_2025_agentes.csv`
        - Empresa: CIMSA
        - Mes: 05
        - Año: 2025  
        - Categoría: agentes
        
        ### 📊 Funcionalidades del reporte:
        - **Resumen Ejecutivo**: Métricas clave y montos totales
        - **Datos Detallados**: Vista filtrable de todos los registros
        - **Análisis de Variaciones**: Comparaciones mensuales y análisis de conceptos para explicar variaciones salariales
        - **Detalles por Archivo**: Información específica de cada archivo procesado
        """)

if __name__ == "__main__":
    main()
