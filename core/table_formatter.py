"""
Table and Alternative Content Format Generator
Creates tables, comparison charts, and other visual formats
"""

import re
from typing import Dict, List, Any, Optional

class TableFormatter:
    """Generate tables and alternative content formats"""
    
    def detect_table_opportunity(self, content: str, heading: str) -> bool:
        """
        Detect if content would benefit from table format
        
        Args:
            content: The content to analyze
            heading: The section heading
            
        Returns:
            True if table format would be beneficial
        """
        heading_lower = heading.lower()
        content_lower = content.lower()
        
        # Keywords that suggest table format
        table_indicators = [
            'comparison', 'compare', 'versus', 'vs',
            'differences', 'similarities',
            'specifications', 'specs', 'features',
            'pricing', 'plans', 'tiers',
            'requirements', 'compatibility',
            'performance', 'metrics', 'benchmarks',
            'pros and cons', 'advantages and disadvantages'
        ]
        
        # Check heading for indicators
        for indicator in table_indicators:
            if indicator in heading_lower:
                return True
        
        # Check for structured lists that could be tables
        if content.count('•') >= 5 or content.count('\n-') >= 5:
            # Check if items have consistent structure (e.g., "Term: Definition")
            lines = content.split('\n')
            colon_count = sum(1 for line in lines if ':' in line)
            if colon_count >= 3:
                return True
        
        # Check for comparison patterns
        comparison_patterns = [
            r'\b(?:while|whereas|but|however|on the other hand)\b',
            r'\b(?:first|second|third|finally)\b.*:',
            r'\b(?:option \d|type \d|tier \d)\b'
        ]
        
        for pattern in comparison_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    def convert_to_table(self, content: str, heading: str) -> Dict[str, Any]:
        """
        Convert appropriate content to table format
        
        Args:
            content: Content to convert
            heading: Section heading
            
        Returns:
            Dictionary with table HTML and metadata
        """
        heading_lower = heading.lower()
        
        # Determine table type based on content
        if any(word in heading_lower for word in ['comparison', 'compare', 'versus', 'vs']):
            return self._create_comparison_table(content, heading)
        elif any(word in heading_lower for word in ['specifications', 'specs', 'features']):
            return self._create_specs_table(content, heading)
        elif any(word in heading_lower for word in ['pricing', 'plans', 'tiers']):
            return self._create_pricing_table(content, heading)
        elif any(word in heading_lower for word in ['pros and cons', 'advantages']):
            return self._create_pros_cons_table(content, heading)
        else:
            return self._create_generic_table(content, heading)
    
    def _create_comparison_table(self, content: str, heading: str) -> Dict[str, Any]:
        """Create a comparison table"""
        lines = content.split('\n')
        rows = []
        
        # Extract comparison items
        current_item = None
        current_features = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a new item (usually starts with bullet or number)
            if line.startswith(('•', '-', '*')) or re.match(r'^\d+\.', line):
                if current_item and current_features:
                    rows.append({'item': current_item, 'features': current_features})
                current_item = re.sub(r'^[•\-\*\d\.]\s*', '', line).split(':')[0].strip()
                current_features = {}
            elif ':' in line and current_item:
                # It's a feature
                key, value = line.split(':', 1)
                current_features[key.strip()] = value.strip()
        
        # Add last item
        if current_item and current_features:
            rows.append({'item': current_item, 'features': current_features})
        
        # Build HTML table
        if rows:
            # Get all unique feature keys
            all_features = set()
            for row in rows:
                all_features.update(row['features'].keys())
            
            html = '<table class="comparison-table">\n'
            html += '  <thead>\n    <tr>\n'
            html += '      <th>Feature</th>\n'
            for row in rows:
                html += f'      <th>{row["item"]}</th>\n'
            html += '    </tr>\n  </thead>\n'
            html += '  <tbody>\n'
            
            for feature in sorted(all_features):
                html += '    <tr>\n'
                html += f'      <td><strong>{feature}</strong></td>\n'
                for row in rows:
                    value = row['features'].get(feature, '—')
                    html += f'      <td>{value}</td>\n'
                html += '    </tr>\n'
            
            html += '  </tbody>\n</table>'
            
            return {
                'html': html,
                'type': 'comparison',
                'row_count': len(all_features),
                'column_count': len(rows) + 1
            }
        
        return {'html': '', 'type': 'comparison', 'error': 'Could not parse comparison data'}
    
    def _create_specs_table(self, content: str, heading: str) -> Dict[str, Any]:
        """Create a specifications table"""
        lines = content.split('\n')
        specs = []
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                # Remove bullets if present
                line = re.sub(r'^[•\-\*\d\.]\s*', '', line)
                key, value = line.split(':', 1)
                specs.append({
                    'specification': key.strip(),
                    'value': value.strip()
                })
        
        if specs:
            html = '<table class="specs-table">\n'
            html += '  <thead>\n    <tr>\n'
            html += '      <th>Specification</th>\n'
            html += '      <th>Value</th>\n'
            html += '    </tr>\n  </thead>\n'
            html += '  <tbody>\n'
            
            for spec in specs:
                html += '    <tr>\n'
                html += f'      <td><strong>{spec["specification"]}</strong></td>\n'
                html += f'      <td>{spec["value"]}</td>\n'
                html += '    </tr>\n'
            
            html += '  </tbody>\n</table>'
            
            return {
                'html': html,
                'type': 'specifications',
                'row_count': len(specs),
                'column_count': 2
            }
        
        return {'html': '', 'type': 'specifications', 'error': 'No specifications found'}
    
    def _create_pricing_table(self, content: str, heading: str) -> Dict[str, Any]:
        """Create a pricing/plans table"""
        # This would parse pricing information
        # For now, using a generic approach
        return self._create_generic_table(content, heading)
    
    def _create_pros_cons_table(self, content: str, heading: str) -> Dict[str, Any]:
        """Create a pros and cons table"""
        lines = content.split('\n')
        pros = []
        cons = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if any(word in line.lower() for word in ['pros', 'advantages', 'benefits']):
                current_section = 'pros'
                continue
            elif any(word in line.lower() for word in ['cons', 'disadvantages', 'drawbacks']):
                current_section = 'cons'
                continue
            
            # Add items to appropriate section
            if line.startswith(('•', '-', '*')) or re.match(r'^\d+\.', line):
                item = re.sub(r'^[•\-\*\d\.]\s*', '', line).strip()
                if current_section == 'pros':
                    pros.append(item)
                elif current_section == 'cons':
                    cons.append(item)
        
        if pros or cons:
            max_rows = max(len(pros), len(cons))
            
            html = '<table class="pros-cons-table">\n'
            html += '  <thead>\n    <tr>\n'
            html += '      <th>✅ Pros</th>\n'
            html += '      <th>❌ Cons</th>\n'
            html += '    </tr>\n  </thead>\n'
            html += '  <tbody>\n'
            
            for i in range(max_rows):
                html += '    <tr>\n'
                pro = pros[i] if i < len(pros) else ''
                con = cons[i] if i < len(cons) else ''
                html += f'      <td>{pro}</td>\n'
                html += f'      <td>{con}</td>\n'
                html += '    </tr>\n'
            
            html += '  </tbody>\n</table>'
            
            return {
                'html': html,
                'type': 'pros_cons',
                'row_count': max_rows,
                'column_count': 2
            }
        
        return {'html': '', 'type': 'pros_cons', 'error': 'Could not identify pros and cons'}
    
    def _create_generic_table(self, content: str, heading: str) -> Dict[str, Any]:
        """Create a generic table from structured content"""
        lines = content.split('\n')
        rows = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove bullets
            line = re.sub(r'^[•\-\*\d\.]\s*', '', line)
            
            # Split by colon if present
            if ':' in line:
                parts = line.split(':', 1)
                rows.append({
                    'label': parts[0].strip(),
                    'value': parts[1].strip() if len(parts) > 1 else ''
                })
            else:
                rows.append({
                    'label': line,
                    'value': ''
                })
        
        if rows:
            html = '<table class="info-table">\n'
            html += '  <tbody>\n'
            
            for row in rows:
                html += '    <tr>\n'
                if row['value']:
                    html += f'      <td><strong>{row["label"]}</strong></td>\n'
                    html += f'      <td>{row["value"]}</td>\n'
                else:
                    html += f'      <td colspan="2">{row["label"]}</td>\n'
                html += '    </tr>\n'
            
            html += '  </tbody>\n</table>'
            
            return {
                'html': html,
                'type': 'generic',
                'row_count': len(rows),
                'column_count': 2
            }
        
        return {'html': '', 'type': 'generic', 'error': 'No structured data found'}
    
    def add_table_styles(self) -> str:
        """Return CSS styles for tables"""
        return """
        <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }
        
        th {
            background-color: #f5f5f5;
            font-weight: 600;
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #ddd;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background-color: #f9f9f9;
        }
        
        .comparison-table th:first-child {
            background-color: #e8f4f8;
        }
        
        .specs-table td:first-child {
            width: 40%;
            font-weight: 500;
        }
        
        .pros-cons-table th:first-child {
            color: #28a745;
        }
        
        .pros-cons-table th:last-child {
            color: #dc3545;
        }
        
        .info-table td[colspan="2"] {
            font-weight: 500;
            background-color: #f8f9fa;
        }
        
        @media (max-width: 768px) {
            table {
                font-size: 14px;
            }
            
            th, td {
                padding: 8px;
            }
        }
        </style>
        """