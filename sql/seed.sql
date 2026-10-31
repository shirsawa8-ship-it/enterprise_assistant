USE enterprise_assistant;

INSERT INTO enterprise_assistant
    (application_id, applicant_id, amount, status)
VALUES
    ('BX2026001', 'EMP001', 800.00, '已付款'),
    ('BX2026002', 'EMP002', 1500.00, '待部门负责人审批'),
    ('BX2026003', 'EMP001', 1000.00, '财务审核中'),
    ('BX2026004', 'EMP001', 350.00, '财务审核中'),
    ('BX2026005', 'EMP003', 200.00, '已付款')
ON DUPLICATE KEY UPDATE     -- 申请编号已经存在时，保持原记录不变；不存在时，插入新记录。
    application_id = application_id;

COMMIT;