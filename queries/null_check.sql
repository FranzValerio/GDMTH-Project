/* Revisión de datos nulos */

SELECT * FROM infraestructura_2021
	WHERE id_region IS NULL
    OR mes IS NULL
    OR distribucion IS NULL
    OR capacidad IS NULL; 
    
/*SELECT * FROM tarifas_2021
	WHERE id_region IS NULL
    OR mes IS NULL
    OR base IS NULL
    OR intermedia IS NULL
    OR punta IS NULL;