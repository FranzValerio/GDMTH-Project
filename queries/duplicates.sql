/* Encontrando elementos duplicados en las tablas */

/* SELECT id_region, estado, municipio, division, COUNT(*) as count
	FROM region
		GROUP BY id_region, estado, municipio, division
			HAVING count > 1;

/* Tarifas */

SELECT id_region, mes, base, intermedia, punta, COUNT(*) as count
FROM tarifas_2021
GROUP BY id_region, mes, base, intermedia, punta
HAVING count > 1;

/* Infraestructura */

SELECT id_region, mes, distribucion, capacidad, COUNT(*) as count
FROM infraestructura_2021
GROUP BY id_region, mes, distribucion, capacidad
HAVING count > 1;
