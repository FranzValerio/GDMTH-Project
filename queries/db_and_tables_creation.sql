
/* Se crea la base de datos: */

CREATE DATABASE tarifas_anuales;

/* Creación de la tabla region: */

CREATE TABLE tarifas_anuales.region(
	id_region INT AUTO_INCREMENT PRIMARY KEY,
    estado VARCHAR(50) NOT NULL,
    municipio VARCHAR(70) NOT NULL,
    division VARCHAR(70),
    UNIQUE KEY unique_region (estado, municipio, division)
);

/* Creación de la tabla tarifas_2021 */


CREATE TABLE tarifas_anuales.tarifas_2021(
	id_tarifa INT AUTO_INCREMENT PRIMARY KEY,
    id_region INT NOT NULL,
    mes VARCHAR(15) NOT NULL,
    base DECIMAL(10,4),
    intermedia DECIMAL(10,4),
    punta DECIMAL(10,4),
    CONSTRAINT fk_region_tarifas_2021 FOREIGN KEY (id_region)
    REFERENCES tarifas_anuales.region(id_region)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/* Creación de la tabla infraestructura_2021 */


CREATE TABLE tarifas_anuales.infraestructura_2021 (
	id_infraestructura INT AUTO_INCREMENT PRIMARY KEY,
    id_region INT NOT NULL,
    mes VARCHAR(15) NOT NULL,
    distribucion DECIMAL(10,4),
    capacidad DECIMAL(10,4),
    CONSTRAINT fk_region_infraestructura_2021 FOREIGN KEY (id_region)
    REFERENCES tarifas_anuales.region(id_region)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
*/

	