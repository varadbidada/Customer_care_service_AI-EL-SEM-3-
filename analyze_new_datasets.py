#!/usr/bin/env python3
"""
Analyze the new datasets to understand their structure for integration
"""

import pandas as pd
import json
from pathlib import Path

def analyze_csv_dataset():
    """Analyze the customer support tickets CSV"""
    print("=" * 60)
    print("📊 ANALYZING CUSTOMER SUPPORT TICKETS CSV")
    print("=" * 60)
    
    try:
        # Read CSV file
        df = pd.read_csv('datasets/customer_support_tickets.csv')
        
        print(f"📈 Dataset Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"\n🔍 Sample Data:")
        print(df.head(3).to_string())
        
        print(f"\n📊 Ticket Types:")
        print(df['Ticket Type'].value_counts())
        
        print(f"\n📊 Ticket Status:")
        print(df['Ticket Status'].value_counts())
        
        print(f"\n📊 Products:")
        print(df['Product Purchased'].value_counts().head(10))
        
        return df
        
    except Exception as e:
        print(f"❌ Error analyzing CSV: {e}")
        return None

def analyze_excel_dataset():
    """Analyze the realistic customer orders Excel"""
    print("\n" + "=" * 60)
    print("📊 ANALYZING REALISTIC CUSTOMER ORDERS EXCEL")
    print("=" * 60)
    
    try:
        # Read Excel file
        df = pd.read_excel('datasets/realistic_customer_orders_india.xlsx')
        
        print(f"📈 Dataset Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"\n🔍 Sample Data:")
        print(df.head(3).to_string())
        
        # Check for order-related columns
        if 'status' in df.columns or 'Status' in df.columns:
            status_col = 'status' if 'status' in df.columns else 'Status'
            print(f"\n📊 Order Status:")
            print(df[status_col].value_counts())
        
        # Check for product columns
        product_cols = [col for col in df.columns if 'product' in col.lower()]
        if product_cols:
            print(f"\n📊 Products (from {product_cols[0]}):")
            print(df[product_cols[0]].value_counts().head(10))
        
        return df
        
    except Exception as e:
        print(f"❌ Error analyzing Excel: {e}")
        return None

def create_integration_plan(csv_df, excel_df):
    """Create integration plan for the new datasets"""
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION PLAN")
    print("=" * 60)
    
    plan = {
        "csv_integration": {},
        "excel_integration": {},
        "unified_structure": {}
    }
    
    if csv_df is not None:
        print("\n📋 CSV Dataset Integration:")
        print("✅ Use for: Enhanced FAQ responses and ticket resolution patterns")
        print("✅ Key fields: Ticket Type, Ticket Subject, Ticket Description, Resolution")
        print("✅ Integration point: FAQ system enhancement")
        
        plan["csv_integration"] = {
            "purpose": "Enhanced FAQ and ticket resolution",
            "key_fields": ["Ticket Type", "Ticket Subject", "Ticket Description", "Resolution"],
            "integration_method": "FAQ enhancement and pattern matching"
        }
    
    if excel_df is not None:
        print("\n📋 Excel Dataset Integration:")
        print("✅ Use for: Extended order database with realistic Indian data")
        print("✅ Key fields: Order details, customer info, product data")
        print("✅ Integration point: Order lookup system expansion")
        
        plan["excel_integration"] = {
            "purpose": "Extended order database",
            "key_fields": list(excel_df.columns) if excel_df is not None else [],
            "integration_method": "Order data access layer expansion"
        }
    
    return plan

if __name__ == "__main__":
    print("🔍 ANALYZING NEW DATASETS FOR INTEGRATION")
    
    # Analyze datasets
    csv_df = analyze_csv_dataset()
    excel_df = analyze_excel_dataset()
    
    # Create integration plan
    plan = create_integration_plan(csv_df, excel_df)
    
    # Save analysis results
    with open('dataset_analysis_results.json', 'w') as f:
        json.dump(plan, f, indent=2, default=str)
    
    print(f"\n✅ Analysis complete! Results saved to dataset_analysis_results.json")