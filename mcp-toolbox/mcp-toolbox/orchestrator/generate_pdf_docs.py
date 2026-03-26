#!/usr/bin/env python3
"""
Generate PDF documentation from markdown files
"""
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import re

def markdown_to_pdf(markdown_file, output_pdf):
    """Convert markdown file to PDF"""
    
    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF document
    doc = SimpleDocTemplate(output_pdf, pagesize=A4, 
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#1f77b4')
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        textColor=HexColor('#2e8b57')
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=HexColor('#4682b4')
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leftIndent=20,
        backgroundColor=HexColor('#f5f5f5')
    )
    
    # Story elements
    story = []
    
    # Split content into lines
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            story.append(Spacer(1, 6))
            i += 1
            continue
        
        # Main title (first # heading)
        if line.startswith('# ') and i < 5:
            title = line[2:].strip()
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
        
        # Heading 1
        elif line.startswith('## '):
            heading = line[3:].strip()
            story.append(Paragraph(heading, heading1_style))
            story.append(Spacer(1, 6))
        
        # Heading 2
        elif line.startswith('### '):
            heading = line[4:].strip()
            story.append(Paragraph(heading, heading2_style))
            story.append(Spacer(1, 6))
        
        # Code blocks
        elif line.startswith('```'):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            if code_lines:
                code_text = '\n'.join(code_lines)
                # Split long code lines
                formatted_code = []
                for code_line in code_lines:
                    if len(code_line) > 80:
                        # Break long lines
                        while len(code_line) > 80:
                            formatted_code.append(code_line[:80])
                            code_line = '  ' + code_line[80:]
                        if code_line.strip():
                            formatted_code.append(code_line)
                    else:
                        formatted_code.append(code_line)
                
                code_text = '\n'.join(formatted_code)
                story.append(Paragraph(code_text.replace('\n', '<br/>'), code_style))
                story.append(Spacer(1, 6))
        
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            list_item = line[2:].strip()
            story.append(Paragraph(f"• {list_item}", styles['Normal']))
        
        elif re.match(r'^\d+\. ', line):
            list_item = re.sub(r'^\d+\. ', '', line).strip()
            story.append(Paragraph(f"1. {list_item}", styles['Normal']))
        
        # Regular paragraphs
        else:
            # Clean up markdown formatting
            text = line
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Bold
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)      # Italic
            text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)  # Inline code
            
            if text.strip():
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 6))
        
        i += 1
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated: {output_pdf}")

def main():
    """Generate PDF documentation"""
    
    # Check if documentation exists
    doc_file = "../COMPLETE_SYSTEM_DOCUMENTATION.md"
    if not os.path.exists(doc_file):
        print(f"Documentation file not found: {doc_file}")
        return
    
    # Generate PDF
    output_file = "Multi_Agent_RAG_System_Documentation.pdf"
    
    try:
        markdown_to_pdf(doc_file, output_file)
        print(f"✅ PDF documentation generated successfully: {output_file}")
        
        # Also generate from README if exists
        readme_file = "UI_README.md"
        if os.path.exists(readme_file):
            ui_output = "UI_Documentation.pdf"
            markdown_to_pdf(readme_file, ui_output)
            print(f"✅ UI PDF documentation generated: {ui_output}")
        
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        os.system("pip install reportlab")
        print("Please run the script again after installation.")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")

if __name__ == "__main__":
    main()