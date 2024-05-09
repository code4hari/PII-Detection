import pandas as pd
import re
import usaddress
import phonenumbers
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI()

# Function to validate and normalize phone numbers to 10 digits
# Function to validate and normalize phone numbers to 10 digits
def normalize_phone_number(number):
    try:
        # Remove all non-digit characters
        cleaned_number = re.sub(r'\D', '', number)
        # Check if the cleaned number has exactly 10 digits
        if len(cleaned_number) == 10:
            return cleaned_number
        else:
            return None
    except Exception:
        return None



# Function to detect PII using usaddress for address detection and regex for other types
def detect_pii(data):
    pii_types = {
        'ssn': r'\b(\d{3}[-]?\d{2}[-]?\d{4})\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    }
    results = []
    for column_name, column_data in data.items():
        for cell in column_data:
            found_pii = False
            pii_type = None
            
            # Check if it's a valid phone number and normalize it
            normalized_number = normalize_phone_number(cell)
            if normalized_number:
                pii_type = 'phone_number'
                found_pii = True
                cell = normalized_number
            
            # If not found as phone number or other PII types, check for address
            if not found_pii:
                # Replace newline characters with spaces
                cell = cell.replace('\r\n', ' ')
                parsed_address, address_type = usaddress.tag(cell)
                if address_type == 'Address':
                    found_pii = True
                    pii_type = 'address'
                    cell = parsed_address
            # If still not found as PII, check for other PII types
            if not found_pii:
                for pii_type, pattern in pii_types.items():
                    if re.findall(pattern, str(cell)):
                        found_pii = True
                        break
            
            # If still not found as PII, label it as not PII
            if not found_pii:
                pii_type = 'not_pii'
            
            results.append((column_name, pii_type, cell))
    return results





# Predefined file path
file_path = 'data/sample_data.csv'

# Define API endpoint for detecting PII
@app.get("/detect_pii")
async def detect_pii_endpoint():
    try:
        # Load CSV data
        data = pd.read_csv(file_path)
        # Detect PII
        pii_results = detect_pii(data)
        # Create DataFrame from results with alternating columns
        output_data = {}
        for column_name, pii_type, cell in pii_results:
            if column_name not in output_data:
                output_data[column_name] = []
                output_data[column_name + '_pii_type'] = []
            output_data[column_name].append(cell)
            output_data[column_name + '_pii_type'].append(pii_type)
        # Convert results to DataFrame
        pii_df = pd.DataFrame(output_data)
        
        # Add a blank record between each block
        spaced_records = []
        for index, record in enumerate(pii_df.to_dict(orient="records")):
            spaced_records.append(record)
            if index < len(pii_df) - 1:
                spaced_records.append({})
        
        # Return PII detection results with spaces between blocks
        return JSONResponse(content=spaced_records)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

# Define root endpoint to return a welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to the PII detection API! add /detect_pii to the link to go to the data."}

# Define endpoint to handle favicon requests and return 404
@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(status_code=404)

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.1.83", port=8888)
