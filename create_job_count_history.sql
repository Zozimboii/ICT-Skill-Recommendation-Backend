-- สร้างตาราง job_count_history ใน MySQL
CREATE TABLE job_count_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    main_category_id INT,
    main_category_name VARCHAR(255),
    sub_category_id INT,
    sub_category_name VARCHAR(255),
    job_count INT,
    snapshot_date DATETIME
);