from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ccdata.db")

bank_data = [
  {
    "bank_name": "Sunshine Bank",
    "website": "https://www.sunshinebank.com",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94105",
    "address": "123 Sunshine St, Suite 400"
  },
  {
    "bank_name": "Greenfield Trust",
    "website": "https://www.greenfieldtrust.com",
    "city": "Chicago",
    "state": "IL",
    "zip": "60611",
    "address": "234 Greenfield Rd"
  },
  {
    "bank_name": "Pioneer Savings",
    "website": "https://www.pioneersavings.com",
    "city": "Dallas",
    "state": "TX",
    "zip": "75201",
    "address": "500 Pioneer Ave"
  },
  {
    "bank_name": "Oak Valley Bank",
    "website": "https://www.oakvalleybank.com",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "address": "60 Oak St"
  },
  {
    "bank_name": "Golden Gate Bank",
    "website": "https://www.goldengatebank.com",
    "city": "Los Angeles",
    "state": "CA",
    "zip": "90001",
    "address": "789 Golden Gate Blvd"
  },
  {
    "bank_name": "Clearwater Financial",
    "website": "https://www.clearwaterfinancial.com",
    "city": "Seattle",
    "state": "WA",
    "zip": "98101",
    "address": "123 Clearwater St"
  },
  {
    "bank_name": "Riverside National",
    "website": "https://www.riversidenational.com",
    "city": "Denver",
    "state": "CO",
    "zip": "80202",
    "address": "456 Riverside Dr"
  },
  {
    "bank_name": "Skyline Credit Union",
    "website": "https://www.skylinecu.com",
    "city": "Boston",
    "state": "MA",
    "zip": "02108",
    "address": "101 Skyline Rd"
  },
  {
    "bank_name": "Lakeshore Financial Group",
    "website": "https://www.lakeshorefinancial.com",
    "city": "Minneapolis",
    "state": "MN",
    "zip": "55101",
    "address": "678 Lakeshore Ave"
  },
  {
    "bank_name": "Summit Trust Bank",
    "website": "https://www.summittrustbank.com",
    "city": "Phoenix",
    "state": "AZ",
    "zip": "85001",
    "address": "234 Summit St"
  },
  ...
  {
    "bank_name": "Maple Valley Credit Union",
    "website": "https://www.maplevalleycu.com",
    "city": "Portland",
    "state": "OR",
    "zip": "97201",
    "address": "123 Maple Valley Rd"
  }
]



for bank in bank_data:
    if (bank["website"] == ""):
      bank["website"] = None
    db.execute("INSERT INTO banks (bank_name, website, city, zip, state, address) VALUES (?, ?, ?, ?, ?, ?)", bank["bank_name"], bank["website"], bank["city"], bank["zip"], bank["state"], bank["address"] )

print("All done!")

# OPTIONALLY: This SQL statement will insert all banks:

# INSERT INTO banks (bank_name, website, city, state, zip, address)
# VALUES
#   ('Sunshine Bank', 'https://www.sunshinebank.com', 'San Francisco', 'CA', '94105', '123 Sunshine St, Suite 400'),
#   ('Greenfield Trust', 'https://www.greenfieldtrust.com', 'Chicago', 'IL', '60611', '234 Greenfield Rd'),
#   ('Pioneer Savings', 'https://www.pioneersavings.com', 'Dallas', 'TX', '75201', '500 Pioneer Ave'),
#   ('Oak Valley Bank', 'https://www.oakvalleybank.com', 'New York', 'NY', '10001', '60 Oak St'),
#   ('Golden Gate Bank', 'https://www.goldengatebank.com', 'Los Angeles', 'CA', '90001', '789 Golden Gate Blvd'),
#   ('Clearwater Financial', 'https://www.clearwaterfinancial.com', 'Seattle', 'WA', '98101', '123 Clearwater St'),
#   ('Riverside National', 'https://www.riversidenational.com', 'Denver', 'CO', '80202', '456 Riverside Dr'),
#   ('Skyline Credit Union', 'https://www.skylinecu.com', 'Boston', 'MA', '02108', '101 Skyline Rd'),
#   ('Lakeshore Financial Group', 'https://www.lakeshorefinancial.com', 'Minneapolis', 'MN', '55101', '678 Lakeshore Ave'),
#   ('Summit Trust Bank', 'https://www.summittrustbank.com', 'Phoenix', 'AZ', '85001', '234 Summit St'),
#   ('Maple Valley Credit Union', 'https://www.maplevalleycu.com', 'Portland', 'OR', '97201', '123 Maple Valley Rd');

