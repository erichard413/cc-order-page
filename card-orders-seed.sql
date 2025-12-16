INSERT INTO users (username, password, first_name, last_name, email, join_date, is_admin, is_cc_admin)
VALUES ('ccadmin',
        'scrypt:32768:8:1$818gLjMNBgrpTPQf$770a29f2265714aced19415de02cd12cb37595593c8a98b3e0641c3fa43b374d814c7c5c988bd7f2fa8a7a05ddbb7d2b9a201e1c3e0a202f97a4b0104625d493',
        'Erik',
        'Richard',
        'cs@convenientcards.com',
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
