INSERT INTO users (username, email, password, is_admin) VALUES
('admin_user', 'admin@example.com', 'hashed_admin_password', 1),  -- Admin user
('regular_user', 'user@example.com', 'hashed_user_password', 0);   -- Regular user

INSERT INTO disease_descriptions (dname, description) VALUES
('Diabetes', 'A chronic condition that affects how the body processes blood sugar. It can lead to serious complications if not managed properly.');

INSERT INTO diseases (dname, prec1, prec2, prec3, prec4) VALUES
('Diabetes', 'Monitor blood sugar levels', 'Maintain a healthy diet', 'Exercise regularly', 'Take prescribed medication');
