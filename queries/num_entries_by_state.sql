SELECT COUNT(*) FROM tarifas_2023 t 
    JOIN region r ON t.id_region = r.id_region
    WHERE t.mes = 'AGOSTO' AND r.estado = 'AGUASCALIENTES';