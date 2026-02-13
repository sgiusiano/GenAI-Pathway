"""
Paybot - AI-Powered Payroll Analysis and Recommendations Engine

This module provides comprehensive analysis of payroll data using AI to generate
executive insights, recommendations, and strategic guidance for decision-making.

Author: Apex America Analytics Team
"""

import pandas as pd
import numpy as np
from typing import Any
import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage
from langchain.callbacks.tracers.langchain import LangChainTracer
from langchain.callbacks.manager import CallbackManager

# LangSmith for tracing and monitoring
from langsmith import Client

# Logging imports
import logging


@dataclass
class PayrollKPIs:
    """Data class to store calculated payroll KPIs"""
    current_total: float
    previous_total: float
    current_employees: int
    previous_employees: int
    delta_amount: float
    delta_percentage: float
    delta_employees: int
    cost_per_employee_current: float
    cost_per_employee_previous: float
    delta_cost_per_employee: float
    top_cost_centers: list[dict[str, Any]]
    top_variations: list[dict[str, Any]]
    new_concepts: list[dict[str, Any]]
    eliminated_concepts: list[dict[str, Any]]
    status: str
    period_comparison: str


class Paybot:
    """
    AI-Powered Payroll Analysis Engine
    
    This class provides comprehensive analysis of payroll data using OpenAI's GPT models
    through LangChain, with monitoring via LangSmith. It generates executive-level
    insights, identifies trends, and provides strategic recommendations.
    """
    
    def __init__(self,
                 api_key: str | None = None,
                 langsmith_api_key: str | None = None,
                 model_name: str = "gpt-4",
                 temperature: float = 0.1):
        """
        Initialize Paybot with AI configuration
        
        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            langsmith_api_key: LangSmith API key (if None, will use LANGSMITH_API_KEY env var)
            model_name: OpenAI model to use for analysis
            temperature: Temperature for AI responses (lower = more focused)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.langsmith_api_key = langsmith_api_key or os.getenv('LANGSMITH_API_KEY')
        self.model_name = model_name
        self.temperature = temperature
        
        # Initialize LangSmith client for tracing
        if self.langsmith_api_key:
            self.langsmith_client = Client(api_key=self.langsmith_api_key)
            self.tracer = LangChainTracer(client=self.langsmith_client, project_name="paybot-analytics")
            self.callback_manager = CallbackManager([self.tracer])
        else:
            self.callback_manager = None
            
        # Initialize OpenAI model via LangChain
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model_name=self.model_name,
            temperature=self.temperature,
            callbacks=self.callback_manager.handlers if self.callback_manager else None
        )
        
        # Define analysis prompts
        self._setup_prompts()
        
        # Setup logging for LLM context tracking
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging to track LLM context and interactions"""
        self.logger = logging.getLogger(f"paybot.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
    def _log_llm_context(self, method_name: str, prompt_data: dict, formatted_prompt: str | None = None):
        """Log the context being passed to the LLM"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"LLM CONTEXT LOG - {method_name.upper()}")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Model: {self.model_name}")
        self.logger.info(f"Temperature: {self.temperature}")
        self.logger.info(f"\nInput Data Summary:")
        for key, value in prompt_data.items():
            if isinstance(value, (int, float)):
                self.logger.info(f"  {key}: {value:,.2f}")
            elif isinstance(value, str) and len(value) > 200:
                self.logger.info(f"  {key}: {value[:200]}... ({len(value)} chars total)")
            else:
                self.logger.info(f"  {key}: {value}")
        
        if formatted_prompt:
            self.logger.info(f"\nFormatted Prompt (first 500 chars):")
            self.logger.info(f"{formatted_prompt[:500]}...")
        
        self.logger.info(f"{'='*80}\n")
    
    def _setup_prompts(self):
        """Setup LangChain prompts for different types of analysis"""
        
        # Executive Summary Prompt
        self.executive_summary_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Eres un CFO senior especializado en análisis de nómina y recursos humanos con más de 15 años de experiencia. 
                Tu objetivo es proporcionar insights ejecutivos claros, concisos y accionables basados en datos de nómina.
                
                Principios para tu análisis:
                1. Enfócate en impactos financieros y operativos significativos
                2. Identifica tendencias y patrones críticos
                3. Proporciona recomendaciones específicas y medibles
                4. Usa un lenguaje ejecutivo profesional pero accesible
                5. Prioriza insights que requieren decisiones inmediatas
                
                Formato de respuesta:
                - Resumen ejecutivo (2-3 líneas clave)
                - Hallazgos principales (máximo 4 puntos)
                - Recomendaciones estratégicas (máximo 3 acciones)
                - Alertas críticas (si aplica)"""
            ),
            HumanMessagePromptTemplate.from_template(
                """Analiza los siguientes KPIs de nómina y proporciona un análisis ejecutivo:

                DATOS FINANCIEROS:
                - Nómina actual: ${current_total:,.0f}
                - Nómina anterior: ${previous_total:,.0f}
                - Variación: {delta_percentage:+.1f}% (${delta_amount:+,.0f})
                - Empleados actuales: {current_employees:,}
                - Empleados anteriores: {previous_employees:,}
                - Variación empleados: {delta_employees:+d}
                - Costo/empleado actual: ${cost_per_employee_current:,.0f}
                - Costo/empleado anterior: ${cost_per_employee_previous:,.0f}
                - Status: {status}
                - Período: {period_comparison}

                CENTROS DE COSTO TOP:
                {top_cost_centers}

                VARIACIONES PRINCIPALES:
                {top_variations}

                CONCEPTOS NUEVOS:
                {new_concepts}

                CONCEPTOS ELIMINADOS:
                {eliminated_concepts}

                Proporciona un análisis ejecutivo completo con insights accionables."""
            )
        ])
        
        # Risk Assessment Prompt
        self.risk_assessment_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Eres un especialista en gestión de riesgos financieros y compliance de nómina.
                Tu objetivo es identificar riesgos potenciales en los datos de nómina y proporcionar 
                recomendaciones para mitigarlos.
                
                Evalúa específicamente:
                1. Riesgos de compliance y regulatorios
                2. Variaciones anómalas que requieren investigación
                3. Tendencias de costos insostenibles
                4. Riesgos operativos de RRHH
                5. Exposiciones financieras"""
            ),
            HumanMessagePromptTemplate.from_template(
                """Evalúa los riesgos basados en estos datos de nómina:
                
                {payroll_data}
                
                Proporciona:
                1. Nivel de riesgo general (Bajo/Medio/Alto/Crítico)
                2. Riesgos específicos identificados
                3. Recomendaciones de mitigación
                4. Acciones inmediatas requeridas"""
            )
        ])
        
        # Trend Analysis Prompt
        self.trend_analysis_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Eres un analista financiero senior especializado en análisis de tendencias de nómina.
                Tu objetivo es identificar patrones, proyecciones y tendencias en los datos de nómina
                para informar la planificación estratégica."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Analiza las tendencias en estos datos de nómina:
                
                {trend_data}
                
                Proporciona:
                1. Tendencias identificadas
                2. Proyecciones para próximos períodos
                3. Factores que impulsan los cambios
                4. Recomendaciones para optimización"""
            )
        ])
    
    def calculate_kpis(self, data: pd.DataFrame) -> PayrollKPIs:
        """
        Calculate comprehensive payroll KPIs from the data
        
        Args:
            data: DataFrame with payroll data including YearMonth column
            
        Returns:
            PayrollKPIs object with all calculated metrics
        """
        try:
            # Get monthly statistics
            monthly_stats = data.groupby('YearMonth').agg({
                'Monto_numeric': 'sum',
                'Legajo': 'nunique'
            }).sort_index()
            monthly_stats.columns = ['Monto_Total', 'Cantidad_Empleados']
            
            if len(monthly_stats) < 2:
                raise ValueError("Need at least 2 months of data for comparison")
            
            current_month = monthly_stats.index[-1]
            previous_month = monthly_stats.index[-2]
            
            # Filter data for current and previous months
            data_current = data[data['YearMonth'] == current_month].copy()
            data_previous = data[data['YearMonth'] == previous_month].copy()
            
            # Basic KPIs
            current_total = monthly_stats.loc[current_month, 'Monto_Total']
            previous_total = monthly_stats.loc[previous_month, 'Monto_Total']
            current_employees = monthly_stats.loc[current_month, 'Cantidad_Empleados']
            previous_employees = monthly_stats.loc[previous_month, 'Cantidad_Empleados']
            
            delta_amount = current_total - previous_total
            delta_percentage = (delta_amount / previous_total) * 100 if previous_total > 0 else 0
            delta_employees = current_employees - previous_employees
            
            cost_per_employee_current = current_total / current_employees if current_employees > 0 else 0
            cost_per_employee_previous = previous_total / previous_employees if previous_employees > 0 else 0
            delta_cost_per_employee = ((cost_per_employee_current - cost_per_employee_previous) / cost_per_employee_previous) * 100 if cost_per_employee_previous > 0 else 0
            
            # Status determination
            if abs(delta_percentage) <= 3 and abs(delta_employees) <= 2:
                status = "🟢 ESTABLE"
            elif delta_percentage > 10 or abs(delta_employees) > 5:
                status = "🔴 REQUIERE ATENCIÓN"
            else:
                status = "🟡 MONITOREAR"
            
            # Top cost centers analysis
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
            
            nomina_comparison = pd.merge(nomina_current, nomina_previous, on='CECO', how='outer').fillna(0)
            nomina_comparison['Variacion_Monto'] = nomina_comparison['Monto_Actual'] - nomina_comparison['Monto_Anterior']
            nomina_comparison['Variacion_Pct'] = ((nomina_comparison['Monto_Actual'] - nomina_comparison['Monto_Anterior']) / nomina_comparison['Monto_Anterior'] * 100).fillna(0)
            nomina_comparison['Variacion_Abs'] = abs(nomina_comparison['Variacion_Monto'])
            
            top_cost_centers = nomina_comparison.nlargest(5, 'Monto_Actual')[['CECO', 'Monto_Actual', 'Empleados_Actual']].to_dict('records')
            top_variations = nomina_comparison.nlargest(5, 'Variacion_Abs')[['CECO', 'Variacion_Monto', 'Variacion_Pct']].to_dict('records')
            
            # Concepts analysis (excluding adjustments)
            ajuste_pattern = r'ajuste|aj\.|Aj|Anses'
            data_current_filtered = data_current[~data_current['Descripción'].str.contains(ajuste_pattern, case=False, na=False)]
            data_previous_filtered = data_previous[~data_previous['Descripción'].str.contains(ajuste_pattern, case=False, na=False)]
            
            conceptos_current = data_current_filtered.groupby('Descripción')['Monto_numeric'].sum().reset_index()
            conceptos_current.columns = ['Concepto', 'Monto_Actual']
            
            conceptos_previous = data_previous_filtered.groupby('Descripción')['Monto_numeric'].sum().reset_index()
            conceptos_previous.columns = ['Concepto', 'Monto_Anterior']
            
            conceptos_comparison = pd.merge(conceptos_current, conceptos_previous, on='Concepto', how='outer').fillna(0)
            
            new_concepts = conceptos_comparison[conceptos_comparison['Monto_Anterior'] == 0].head(5)[['Concepto', 'Monto_Actual']].to_dict('records')
            eliminated_concepts = conceptos_comparison[conceptos_comparison['Monto_Actual'] == 0].head(5)[['Concepto', 'Monto_Anterior']].to_dict('records')
            
            return PayrollKPIs(
                current_total=current_total,
                previous_total=previous_total,
                current_employees=current_employees,
                previous_employees=previous_employees,
                delta_amount=delta_amount,
                delta_percentage=delta_percentage,
                delta_employees=delta_employees,
                cost_per_employee_current=cost_per_employee_current,
                cost_per_employee_previous=cost_per_employee_previous,
                delta_cost_per_employee=delta_cost_per_employee,
                top_cost_centers=top_cost_centers,
                top_variations=top_variations,
                new_concepts=new_concepts,
                eliminated_concepts=eliminated_concepts,
                status=status,
                period_comparison=f"{previous_month} vs {current_month}"
            )
            
        except Exception as e:
            import traceback
            error_msg = f"Error calculating KPIs: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(f"DEBUG: {error_msg}")  # For debugging
            raise Exception(error_msg)
    
    def generate_executive_summary(self, kpis: PayrollKPIs) -> str:
        """
        Generate comprehensive executive summary using AI
        
        Args:
            kpis: PayrollKPIs object with calculated metrics
            
        Returns:
            AI-generated executive summary and recommendations
        """
        try:
            # Format the data for the prompt
            prompt_data = {
                "current_total": kpis.current_total,
                "previous_total": kpis.previous_total,
                "delta_percentage": kpis.delta_percentage,
                "delta_amount": kpis.delta_amount,
                "current_employees": kpis.current_employees,
                "previous_employees": kpis.previous_employees,
                "delta_employees": kpis.delta_employees,
                "cost_per_employee_current": kpis.cost_per_employee_current,
                "cost_per_employee_previous": kpis.cost_per_employee_previous,
                "status": kpis.status,
                "period_comparison": kpis.period_comparison,
                "top_cost_centers": self._format_list_for_prompt(kpis.top_cost_centers),
                "top_variations": self._format_list_for_prompt(kpis.top_variations),
                "new_concepts": self._format_list_for_prompt(kpis.new_concepts),
                "eliminated_concepts": self._format_list_for_prompt(kpis.eliminated_concepts)
            }
            
            # Format the complete prompt for logging
            formatted_prompt = self.executive_summary_prompt.format(**prompt_data)
            
            # Log the context being passed to LLM
            self._log_llm_context("executive_summary", prompt_data, str(formatted_prompt))
            
            # Generate response using LangChain
            response = self.llm.invoke(formatted_prompt)
            
            self.logger.info(f"LLM Response received - Length: {len(response.content)} characters")
            
            return response.content
            
        except Exception as e:
            return f"Error generando análisis ejecutivo: {str(e)}"
    
    def generate_risk_assessment(self, kpis: PayrollKPIs) -> str:
        """
        Generate risk assessment using AI
        
        Args:
            kpis: PayrollKPIs object with calculated metrics
            
        Returns:
            AI-generated risk assessment and mitigation recommendations
        """
        try:
            payroll_data = self._format_kpis_for_prompt(kpis)
            
            # Prepare data for logging
            prompt_context = {"payroll_data": payroll_data}
            formatted_prompt = self.risk_assessment_prompt.format(payroll_data=payroll_data)
            
            # Log the context being passed to LLM
            self._log_llm_context("risk_assessment", prompt_context, str(formatted_prompt))
            
            response = self.llm.invoke(formatted_prompt)
            
            self.logger.info(f"LLM Response received - Length: {len(response.content)} characters")
            
            return response.content
            
        except Exception as e:
            return f"Error generando evaluación de riesgos: {str(e)}"
    
    def generate_trend_analysis(self, data: pd.DataFrame) -> str:
        """
        Generate trend analysis using AI
        
        Args:
            data: DataFrame with payroll data
            
        Returns:
            AI-generated trend analysis and projections
        """
        try:
            # Calculate trends over all available periods
            monthly_trends = data.groupby('YearMonth').agg({
                'Monto_numeric': 'sum',
                'Legajo': 'nunique'
            }).sort_index()
            
            trend_data = {
                "monthly_totals": monthly_trends['Monto_numeric'].to_dict(),
                "monthly_employees": monthly_trends['Legajo'].to_dict(),
                "periods_available": len(monthly_trends),
                "trend_direction": "creciente" if monthly_trends['Monto_numeric'].iloc[-1] > monthly_trends['Monto_numeric'].iloc[0] else "decreciente"
            }
            
            trend_data_json = json.dumps(trend_data, indent=2)
            prompt_context = {"trend_data": trend_data_json}
            formatted_prompt = self.trend_analysis_prompt.format(trend_data=trend_data_json)
            
            # Log the context being passed to LLM
            self._log_llm_context("trend_analysis", prompt_context, str(formatted_prompt))
            
            response = self.llm.invoke(formatted_prompt)
            
            self.logger.info(f"LLM Response received - Length: {len(response.content)} characters")
            
            return response.content
            
        except Exception as e:
            return f"Error generando análisis de tendencias: {str(e)}"
    
    def generate_comprehensive_report(self, data: pd.DataFrame) -> dict[str, str]:
        """
        Generate comprehensive report with all analyses
        
        Args:
            data: DataFrame with payroll data
            
        Returns:
            Dictionary with all analysis sections
        """
        try:
            # Calculate KPIs
            kpis = self.calculate_kpis(data)
            
            # Generate all analyses
            executive_summary = self.generate_executive_summary(kpis)
            risk_assessment = self.generate_risk_assessment(kpis)
            trend_analysis = self.generate_trend_analysis(data)
            
            return {
                "executive_summary": executive_summary,
                "risk_assessment": risk_assessment,
                "trend_analysis": trend_analysis,
                "kpis": kpis
            }
            
        except Exception as e:
            return {
                "error": f"Error generando reporte comprehensivo: {str(e)}",
                "executive_summary": "Error en análisis",
                "risk_assessment": "Error en análisis", 
                "trend_analysis": "Error en análisis"
            }
    
    def _format_list_for_prompt(self, data_list: list[dict]) -> str:
        """Format list of dictionaries for prompt inclusion"""
        if not data_list:
            return "No hay datos disponibles"
        
        formatted = []
        for item in data_list:
            try:
                # Convert numpy types to Python native types for JSON serialization
                clean_item = {}
                for key, value in item.items():
                    if hasattr(value, 'item'):  # numpy scalar
                        clean_item[key] = value.item()
                    elif isinstance(value, (int, float, str)):
                        clean_item[key] = value
                    else:
                        clean_item[key] = str(value)
                formatted.append(json.dumps(clean_item, ensure_ascii=False, default=str))
            except Exception as e:
                # Fallback to string representation if JSON fails
                formatted.append(str(item))
        return "\n".join(formatted)
    
    def _format_kpis_for_prompt(self, kpis: PayrollKPIs) -> str:
        """Format KPIs object for prompt inclusion"""
        return f"""
        Nómina Actual: ${kpis.current_total:,.0f}
        Nómina Anterior: ${kpis.previous_total:,.0f}
        Variación: {kpis.delta_percentage:+.1f}% (${kpis.delta_amount:+,.0f})
        Empleados: {kpis.current_employees:,} ({kpis.delta_employees:+d})
        Costo/Empleado: ${kpis.cost_per_employee_current:,.0f} ({kpis.delta_cost_per_employee:+.1f}%)
        Status: {kpis.status}
        Período: {kpis.period_comparison}
        
        Centros de Costo Principales:
        {self._format_list_for_prompt(kpis.top_cost_centers)}
        
        Variaciones Principales:
        {self._format_list_for_prompt(kpis.top_variations)}
        """


# Example usage and testing
if __name__ == "__main__":
    # This would be used for testing the Paybot class
    print("Paybot Analytics Engine initialized successfully!")
