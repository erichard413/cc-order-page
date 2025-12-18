INSERT INTO users (username, password, first_name, last_name, email, join_date, is_admin, is_cc_admin)
VALUES ('ccadmin',
        'scrypt:32768:8:1$818gLjMNBgrpTPQf$770a29f2265714aced19415de02cd12cb37595593c8a98b3e0641c3fa43b374d814c7c5c988bd7f2fa8a7a05ddbb7d2b9a201e1c3e0a202f97a4b0104625d493',
        'admin',
        'user',
        'admin@admin.com',
        CURRENT_TIMESTAMP,
        TRUE,
        TRUE
        );

INSERT INTO products (product_id, product_name, product_type, unit_price, bundle_qty, description, img_src) VALUES (
        '123',
        'Convenient Visa Gift Card',
        'Gift',
        2.50,
        25,
        'The Convenient Visa® Gift Card is a single load card that is the perfect gift for any occasion.',
        'https://i.postimg.cc/Nj445NyK/123.png'
);
INSERT INTO products (product_id, product_name, product_type,unit_price, bundle_qty, description, img_src) VALUES (
        '124',
        'Convenient Visa Red Elegant Card',
        'Gift',
        2.50,
        25,
        'The Convenient Visa® Gift Card is a single load card that is the perfect gift for any occasion.',
        'https://i.postimg.cc/sgccvnBV/124.png '
);
INSERT INTO products (product_id, product_name, product_type, unit_price, bundle_qty, description, img_src) VALUES (
        '125',
        'Convenient Visa Formal Gift Card',
        'Gift',
        2.50,
        25,
        'The Convenient Visa® Gift Card is a single load card that is the perfect gift for any occasion.',
        'https://i.postimg.cc/FHZZ7Pff/125.png'
);
INSERT INTO products (product_id, product_name, product_type, unit_price, bundle_qty, description, img_src) VALUES (
        '211',
        'Convenient Access Visa Prepaid Card',
        'Access',
        2.50,
        15,
        'The Convenient Access Visa® Prepaid Card is a general purpose reloadable prepaid card with hundreds of applications.',
        'https://i.postimg.cc/FHZZ7Pfz/211.png'
);
INSERT INTO products (product_id, product_name, product_type, unit_price, bundle_qty, description, img_src) VALUES (
        '315',
        'Convenient Visa Incentive Card',
        'Incentive',
        2.50,
        15,
        'The Convenient Visa® Incentive Card is a single-load reward card designed for business customers.',
        'https://i.postimg.cc/qvLLzmtg/315.png'
);
INSERT INTO banks (bank_name, website, city, state, zip, address)
VALUES
  ('Sunshine Bank', 'https://www.sunshinebank.com', 'San Francisco', 'CA', '94105', '123 Sunshine St, Suite 400'),
  ('Greenfield Trust', 'https://www.greenfieldtrust.com', 'Chicago', 'IL', '60611', '234 Greenfield Rd'),
  ('Pioneer Savings', 'https://www.pioneersavings.com', 'Dallas', 'TX', '75201', '500 Pioneer Ave'),
  ('Oak Valley Bank', 'https://www.oakvalleybank.com', 'New York', 'NY', '10001', '60 Oak St'),
  ('Golden Gate Bank', 'https://www.goldengatebank.com', 'Los Angeles', 'CA', '90001', '789 Golden Gate Blvd'),
  ('Clearwater Financial', 'https://www.clearwaterfinancial.com', 'Seattle', 'WA', '98101', '123 Clearwater St'),
  ('Riverside National', 'https://www.riversidenational.com', 'Denver', 'CO', '80202', '456 Riverside Dr'),
  ('Skyline Credit Union', 'https://www.skylinecu.com', 'Boston', 'MA', '02108', '101 Skyline Rd'),
  ('Lakeshore Financial Group', 'https://www.lakeshorefinancial.com', 'Minneapolis', 'MN', '55101', '678 Lakeshore Ave'),
  ('Summit Trust Bank', 'https://www.summittrustbank.com', 'Phoenix', 'AZ', '85001', '234 Summit St'),
  ('Maple Valley Credit Union', 'https://www.maplevalleycu.com', 'Portland', 'OR', '97201', '123 Maple Valley Rd');
