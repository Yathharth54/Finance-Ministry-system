from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        # Logo or header styling
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102)  # Dark blue
        self.cell(0, 10, 'Budget Analysis Report', border=0, ln=1, align='C')
        self.line(10, 20, self.w - 10, 20)  # Add a line under header
        self.ln(10)
    
    def footer(self):
        # Page number styling
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def create_table(self, headers, data, col_widths=None):
        # A simple table implementation that doesn't require the table() method
        if col_widths is None:
            col_widths = [self.w / len(headers) - 10] * len(headers)
        
        # Headers
        self.set_font('Arial', 'B', 10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, str(header), 1, 0, 'C')
        self.ln()
        
        # Data
        self.set_font('Arial', '', 10)
        for row in data:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 8, str(cell), 1, 0, 'L')
            self.ln()

def compile_report(projections: dict, risk_level: str, tax_slabs: list, visual_plots_dir: str = "visual plots", 
                  output_pdf: str = "report.pdf", insights: dict = None):
    """
    Compile all data into a final PDF report with insights
    
    Args:
        projections: Dictionary containing budget projections data
        risk_level: Overall risk assessment level
        tax_slabs: List of tax brackets and rates
        visual_plots_dir: Directory containing visualization plots
        output_pdf: Output PDF filename
        insights: Dictionary containing insight paragraphs for each section
            Expected format: {
                "revenue": "Insight text about revenue...",
                "expenditure": "Insight text about expenditure...",
                "economic": "Insight text about inflation and GDP...",
                "risk": "Insight text about risk assessment...",
                "tax": "Insight text about tax policy...",
                "visual": {
                    "plot_name": "Insight text for specific visual..."
                }
            }
    """
    # Default insights if none provided
    if insights is None:
        insights = {
            "revenue": "Revenue analysis shows a balanced distribution across tax and non-tax sources, with particular strength in corporate and personal income taxes.",
            "expenditure": "The expenditure allocation prioritizes education, healthcare, and debt servicing, representing a balanced approach to public spending.",
            "economic": "The projected inflation rate slightly exceeds GDP growth, suggesting careful monitoring of fiscal policies will be needed in the coming year.",
            "risk": "The medium risk assessment indicates potential challenges that require proactive management strategies.",
            "tax": "The progressive tax structure aims to balance revenue generation with equitable distribution of tax burden across income levels.",
            "visual": {}
        }
    
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Section 1: Budget Projections
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Budget Projections", ln=1)
    pdf.ln(5)
    
    # Revenue Table
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, "Projected Revenues", ln=1)
    pdf.set_font("Arial", size=11)
    
    # Create revenue table
    headers = ["Revenue Source", "Projected Amount"]
    data = [[rev.get("name", "Unknown"), f"${rev.get('projected_amount', 0):,.2f}"] 
            for rev in projections.get("projected_revenue", [])]
    pdf.create_table(headers, data)
    
    # Revenue Insights
    if "revenue" in insights:
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, insights["revenue"])
    
    # Expenditure Table
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, "Projected Expenditures", ln=1)
    pdf.set_font("Arial", size=11)
    
    # Create expenditure table
    headers = ["Expenditure Category", "Projected Amount"]
    data = [[exp.get("name", "Unknown"), f"${exp.get('projected_amount', 0):,.2f}"] 
            for exp in projections.get("projected_expenditure", [])]
    pdf.create_table(headers, data)
    
    # Expenditure Insights
    if "expenditure" in insights:
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, insights["expenditure"])
    
    # Inflation & GDP
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, "Economic Indicators", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 6, f"Projected Inflation (2026): {projections.get('projected_inflation', {}).get('rate', 'N/A')}%", ln=1)
    pdf.cell(0, 6, f"Projected GDP Growth (2026): {projections.get('projected_gdp_growth', {}).get('rate', 'N/A')}%", ln=1)
    
    # Economic Indicators Insights
    if "economic" in insights:
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, insights["economic"])
    
    # Section 2: Risk Identification
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Risk Identification", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0)
    pdf.ln(8)
    pdf.cell(0, 10, f"Overall Risk Ranking: {risk_level.upper()}", ln=1)
    
    # Risk Insights
    if "risk" in insights:
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, insights["risk"])
    
    # Section 3: Tax Slabs
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Tax Slabs", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.ln(5)
    
    # Create tax slabs table
    headers = ["Slab", "Income Range", "Tax Rate"]
    data = [[slab.get('slab', ''), slab.get('range', ''), slab.get('tax_rate', '')] 
            for slab in tax_slabs]
    pdf.create_table(headers, data)
    
    # Tax Insights
    if "tax" in insights:
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, insights["tax"])
    
    # Section 4: Visual Plots
    if os.path.exists(visual_plots_dir):
        for image_file in sorted(os.listdir(visual_plots_dir)):
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Visual Analysis: {image_file.split('.')[0]}", ln=1)
                
                # Calculate image dimensions to maintain aspect ratio
                img_width = pdf.w - 40  # Image width (leaving margins)
                
                # Use standard image method without keep_aspect_ratio parameter
                pdf.image(os.path.join(visual_plots_dir, image_file), x=20, w=img_width)
                
                # Visual-specific insights
                image_name = image_file.split('.')[0]
                if "visual" in insights and image_name in insights["visual"]:
                    pdf.ln(5)
                    pdf.set_font("Arial", 'I', 11)
                    pdf.set_text_color(50, 50, 50)
                    pdf.multi_cell(0, 6, insights["visual"][image_name])
    else:
        pdf.add_page()
        pdf.cell(0, 10, "No visual plots found.", ln=1)
    
    pdf.output(output_pdf)
    print(f"Report compiled as {output_pdf}")