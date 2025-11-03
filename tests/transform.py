import pandas as pd
import json
from nameparser import HumanName
from slugify import slugify

def transform_data(df):

    REQUIRED_COLUMNS = [
    'propertyStatus', 'price', 'numberOfBeds', 'numberOfBaths', 'sqft',
    'addr1', 'addr2', 'streetNumber', 'streetName', 'streetType',
    'preDirection', 'unitType', 'unitNumber', 'city', 'state', 'zipcode',
    'latitude', 'longitude', 'compassPropertyId', 'propertyType', 'yearBuilt',
    'presentedBy', 'brokeredBy', 'realtorMobile', 'sourcePropertyId',
    'list_date', 'pending_date', 'openHouse', 'listing_office_id',
    'listing_agent_id', 'email', 'pageLink', 'scraped_date']
    
    """Apply all 8 transformations to the dataframe"""
    
    print(f"Starting transformation on {len(df)} rows...")


    print("\n🔍 Step 0: Filtering columns...")
    print(f"Original columns: {len(df.columns)}")
    
    # Drop all unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    print(f"After dropping unnamed: {len(df.columns)}")
    
    # Keep only required columns that exist in the dataframe
    available_columns = [col for col in REQUIRED_COLUMNS if col in df.columns]
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    
    if missing_columns:
        print(f"⚠️  Warning: These required columns are missing: {missing_columns}")
    
    df = df[available_columns]
    print(f"✅ Filtered to {len(df.columns)} required columns")
    
    # 1. Column Renaming
    rename_map = {
        "propertyStatus": "status",
        "numberOfBeds": "bedrooms",
        "numberOfBaths": "bathrooms",
        "sqft": "square_feet",
        "addr1": "address_line_1",
        "addr2": "address_line_2",
        "streetNumber": "street_number",
        "streetName": "street_name",
        "streetType": "street_type",
        "preDirection": "pre_direction",
        "unitType": "unit_type",
        "unitNumber": "unit_number",
        "zipcode": "zip_code",
        "propertyType": "property_type",
        "yearBuilt": "year_built",
        "presentedBy": "presented_by",
        "brokeredBy": "brokered_by",
        "realtorMobile": "presented_by_mobile",
        "sourcePropertyId": "mls",
        "openHouse": "open_house",
        "compassPropertyId": "compass_property_id",
        "pageLink": "page_link"
    }
    df = df.rename(columns=rename_map)
    print("✅ Step 1: Column renaming complete")
    
    # 2. Status Standardization
    status_map = {
        'Active Under Contract': 'Pending',
        'New': 'Active',
        'Closed': 'Sold'
    }
    df['status'] = df['status'].map(status_map).fillna(df['status'])
    print("✅ Step 2: Status standardization complete")
    
    # 3. Name Parsing
    def parse_name(name):
        if pd.isna(name) or str(name).strip() == '':
            return pd.Series([None, None, None])
        try:
            human_name = HumanName(str(name))
            return pd.Series([human_name.first, human_name.middle, human_name.last])
        except:
            return pd.Series([None, None, None])
    
    df[['presented_by_first_name', 'presented_by_middle_name', 'presented_by_last_name']] = \
        df['presented_by'].apply(parse_name)
    print("✅ Step 3: Name parsing complete")
    
    # 4. Open House JSON Parsing
    def parse_open_house(oh_json):
        if pd.isna(oh_json) or str(oh_json).strip() == '':
            return pd.Series([None, None, None])
        try:
            oh_data = json.loads(oh_json)
            return pd.Series([
                oh_data.get('startTime'),
                oh_data.get('company'),
                oh_data.get('contactName')
            ])
        except:
            return pd.Series([None, None, None])
    
    df[['oh_startTime', 'oh_company', 'oh_contactName']] = \
        df['open_house'].apply(parse_open_house)
    df = df.drop('open_house', axis=1)
    print("✅ Step 4: Open house parsing complete")
    
    # 5. Full Address Generation
    def create_full_address(row):
        parts = []
        if pd.notna(row.get('address_line_1')) and str(row.get('address_line_1')).strip():
            parts.append(str(row.get('address_line_1')).strip())
        if pd.notna(row.get('address_line_2')) and str(row.get('address_line_2')).strip():
            parts.append(str(row.get('address_line_2')).strip())
        if pd.notna(row.get('city')) and str(row.get('city')).strip():
            parts.append(str(row.get('city')).strip())
        if pd.notna(row.get('state')) and str(row.get('state')).strip():
            parts.append(str(row.get('state')).strip())
        if pd.notna(row.get('zip_code')) and str(row.get('zip_code')).strip():
            parts.append(str(row.get('zip_code')).strip())
        return ', '.join(parts) if parts else None
    
    df['full_address'] = df.apply(create_full_address, axis=1)
    print("✅ Step 5: Full address generation complete")
    
    # 6. Email Splitting (safe version)
    if 'email' in df.columns:
        split_emails = df['email'].astype(str).str.split(',', n=1, expand=True)
        # Handle cases where only one email or none exist
        if split_emails.shape[1] == 1:
            split_emails[1] = None
        df['email_1'] = split_emails[0].str.strip()
        df['email_2'] = split_emails[1].str.strip()
    else:
        df['email_1'], df['email_2'] = None, None
    
    print("✅ Step 6: Email splitting complete")
    
    # 7. Transaction ID Generation
    def generate_id(row):
        parts = []
        for field in ['mls', 'address_line_1', 'address_line_2', 'city', 'state', 'zip_code']:
            val = row.get(field)
            if pd.notna(val) and str(val).strip():
                parts.append(str(val).strip())
        combined = '-'.join(parts) if parts else 'unknown'
        return slugify(combined)
    
    df['id'] = df.apply(generate_id, axis=1)
    print("✅ Step 7: Transaction ID generation complete")
    
    # 8. Phone Number Cleaning
    df['presented_by_mobile'] = df['presented_by_mobile'].astype(str).str.replace(r'\D', '', regex=True).str[:10]
    print("✅ Step 8: Phone number cleaning complete")
    
    print(f"\n✅ Transformation complete! Final columns: {len(df.columns)}")
    return df