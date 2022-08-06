

-- Somehow Django failed to create PK on the table - manual fix:
ALTER TABLE rules_skilllevel ADD PRIMARY KEY (id);

