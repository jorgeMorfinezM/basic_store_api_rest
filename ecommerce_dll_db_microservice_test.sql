-- DROP SCHEMA cargamos;

CREATE SCHEMA cargamos AUTHORIZATION postgres;

-- DROP TYPE cargamos."_product_api";

CREATE TYPE cargamos."_product_api" (
	INPUT = array_in,
	OUTPUT = array_out,
	RECEIVE = array_recv,
	SEND = array_send,
	ANALYZE = array_typanalyze,
	ALIGNMENT = 8,
	STORAGE = any,
	CATEGORY = A,
	ELEMENT = cargamos.product_api,
	DELIMITER = ',');

-- DROP TYPE cargamos."_store_api";

CREATE TYPE cargamos."_store_api" (
	INPUT = array_in,
	OUTPUT = array_out,
	RECEIVE = array_recv,
	SEND = array_send,
	ANALYZE = array_typanalyze,
	ALIGNMENT = 8,
	STORAGE = any,
	CATEGORY = A,
	ELEMENT = cargamos.store_api,
	DELIMITER = ',');

-- DROP TYPE cargamos."_user_auth_api";

CREATE TYPE cargamos."_user_auth_api" (
	INPUT = array_in,
	OUTPUT = array_out,
	RECEIVE = array_recv,
	SEND = array_send,
	ANALYZE = array_typanalyze,
	ALIGNMENT = 8,
	STORAGE = any,
	CATEGORY = A,
	ELEMENT = cargamos.user_auth_api,
	DELIMITER = ',');
-- cargamos.store_api definition

-- Drop table

-- DROP TABLE cargamos.store_api;

CREATE TABLE cargamos.store_api (
	id_store uuid NOT NULL, -- Identificador de la tienda
	store_name varchar NOT NULL, -- Nombre de la tienda
	store_code varchar NOT NULL, -- Identificador publico de la tienda
	store_street_address varchar NULL, -- Calle del domicilio de la tienda
	store_external_number varchar NULL, -- Numero exterior del domicilio de la tienda
	store_suburb_address varchar NULL, -- Colonia de la tienda
	store_city_address varchar NULL, -- Ciudad de la tienda
	store_country_address varchar NULL, -- Pais de la tienda
	store_zippostal_code varchar NULL, -- Codigo postal de la tienda
	store_min_inventory numeric NOT NULL DEFAULT 1, -- Inventario minimo en la tienda
	creation_date timestamp(0) NULL DEFAULT now(), -- Fecha de creacion de la tienda
	last_update_date timestamp(0) NULL DEFAULT now(),
	CONSTRAINT store_api_pk PRIMARY KEY (id_store),
	CONSTRAINT store_api_un UNIQUE (id_store, store_code)
);
CREATE INDEX store_api_store_code_idx ON cargamos.store_api USING btree (store_code);
COMMENT ON TABLE cargamos.store_api IS 'Contiene informacion de una tienda';

-- Column comments

COMMENT ON COLUMN cargamos.store_api.id_store IS 'Identificador de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_name IS 'Nombre de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_code IS 'Identificador publico de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_street_address IS 'Calle del domicilio de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_external_number IS 'Numero exterior del domicilio de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_suburb_address IS 'Colonia de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_city_address IS 'Ciudad de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_country_address IS 'Pais de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_zippostal_code IS 'Codigo postal de la tienda';
COMMENT ON COLUMN cargamos.store_api.store_min_inventory IS 'Inventario minimo en la tienda';
COMMENT ON COLUMN cargamos.store_api.creation_date IS 'Fecha de creacion de la tienda';

-- Constraint comments

COMMENT ON CONSTRAINT store_api_pk ON cargamos.store_api IS 'Llave primaria de la tienda';

-- Permissions

ALTER TABLE cargamos.store_api OWNER TO postgres;
GRANT ALL ON TABLE cargamos.store_api TO postgres;
GRANT SELECT(creation_date) ON cargamos.store_api TO pg_read_all_stats;


-- cargamos.user_auth_api definition

-- Drop table

-- DROP TABLE cargamos.user_auth_api;

CREATE TABLE cargamos.user_auth_api (
	user_id numeric NOT NULL,
	username varchar NOT NULL, -- Username to authenticate to the API
	"password" varchar NOT NULL, -- Password to authenticate to API
	password_hash bpchar NULL, -- Password hash authenticated
	creation_date timestamp(0) NULL,
	last_update_date timestamp(0) NULL,
	CONSTRAINT user_auth_api_pk PRIMARY KEY (user_id)
);
COMMENT ON TABLE cargamos.user_auth_api IS 'contain the data to authenticate to the API';

-- Column comments

COMMENT ON COLUMN cargamos.user_auth_api.username IS 'Username to authenticate to the API';
COMMENT ON COLUMN cargamos.user_auth_api."password" IS 'Password to authenticate to API';
COMMENT ON COLUMN cargamos.user_auth_api.password_hash IS 'Password hash authenticated';

-- Permissions

ALTER TABLE cargamos.user_auth_api OWNER TO postgres;
GRANT ALL ON TABLE cargamos.user_auth_api TO postgres;


-- cargamos.product_api definition

-- Drop table

-- DROP TABLE cargamos.product_api;

CREATE TABLE cargamos.product_api (
	product_id uuid NOT NULL, -- Contiene el identificador unico para el producto
	product_sku varchar NOT NULL, -- SKU del producto
	product_unspc varchar NULL, -- UNSPC SKU publico global
	product_brand varchar NULL, -- Marca del producto
	category_id numeric NULL, -- Identificador de la categoria del producto
	parent_category_id numeric NULL, -- Identificador de la categoria padre
	unit_of_measure varchar NULL, -- Unidad de medida del producto
	product_stock numeric NOT NULL, -- Inventario del producto por tienda
	product_store_id uuid NOT NULL, -- Tienda del producto
	product_name varchar NOT NULL, -- Nombre del producto
	product_title varchar NOT NULL, -- Titulo del producto
	product_long_description varchar NULL, -- Descripcion larga del producto
	product_photo varchar NULL, -- URL de la foto del producto
	product_price numeric(2) NOT NULL, -- Precio del producto
	product_tax numeric(6) NOT NULL, -- Impuesto del precio del producto
	product_currency varchar NULL DEFAULT 'MX'::character varying, -- Moneda del precio del producto
	product_status varchar NOT NULL DEFAULT 'Activo'::character varying, -- Estatus del producto
	product_published bool NULL DEFAULT true, -- Aplica para publicar producto en e-commerce
	product_manage_stock bool NULL DEFAULT true, -- Identifica si un producto puede tener o no inventario
	product_length numeric(4) NULL, -- Largo del producto en CM
	product_width numeric(4) NULL, -- Ancho del producto en CM
	product_height numeric(4) NULL, -- Altura del producto en CM
	product_weight numeric(4) NULL, -- Peso del producto en GRM
	creation_date timestamp(0) NULL DEFAULT now(), -- Fecha de creacion del producto
	last_update_date timestamp(0) NULL DEFAULT now(), -- Fecha de actualizacion del producto
	CONSTRAINT product_api_check CHECK (((product_status)::text = ANY (ARRAY[('Activo'::character varying)::text, ('Inactivo'::character varying)::text]))),
	CONSTRAINT product_api_pk PRIMARY KEY (product_id),
	CONSTRAINT product_api_un UNIQUE (product_id, product_sku, product_unspc),
	CONSTRAINT product_api_fk FOREIGN KEY (product_store_id) REFERENCES cargamos.store_api(id_store) ON UPDATE CASCADE ON DELETE CASCADE
);
COMMENT ON TABLE cargamos.product_api IS 'Contiene informacion por producto por tienda';

-- Column comments

COMMENT ON COLUMN cargamos.product_api.product_id IS 'Contiene el identificador unico para el producto';
COMMENT ON COLUMN cargamos.product_api.product_sku IS 'SKU del producto';
COMMENT ON COLUMN cargamos.product_api.product_unspc IS 'UNSPC SKU publico global';
COMMENT ON COLUMN cargamos.product_api.product_brand IS 'Marca del producto';
COMMENT ON COLUMN cargamos.product_api.category_id IS 'Identificador de la categoria del producto';
COMMENT ON COLUMN cargamos.product_api.parent_category_id IS 'Identificador de la categoria padre';
COMMENT ON COLUMN cargamos.product_api.unit_of_measure IS 'Unidad de medida del producto';
COMMENT ON COLUMN cargamos.product_api.product_stock IS 'Inventario del producto por tienda';
COMMENT ON COLUMN cargamos.product_api.product_store_id IS 'Tienda del producto';
COMMENT ON COLUMN cargamos.product_api.product_name IS 'Nombre del producto';
COMMENT ON COLUMN cargamos.product_api.product_title IS 'Titulo del producto';
COMMENT ON COLUMN cargamos.product_api.product_long_description IS 'Descripcion larga del producto';
COMMENT ON COLUMN cargamos.product_api.product_photo IS 'URL de la foto del producto';
COMMENT ON COLUMN cargamos.product_api.product_price IS 'Precio del producto';
COMMENT ON COLUMN cargamos.product_api.product_tax IS 'Impuesto del precio del producto';
COMMENT ON COLUMN cargamos.product_api.product_currency IS 'Moneda del precio del producto';
COMMENT ON COLUMN cargamos.product_api.product_status IS 'Estatus del producto';
COMMENT ON COLUMN cargamos.product_api.product_published IS 'Aplica para publicar producto en e-commerce';
COMMENT ON COLUMN cargamos.product_api.product_manage_stock IS 'Identifica si un producto puede tener o no inventario';
COMMENT ON COLUMN cargamos.product_api.product_length IS 'Largo del producto en CM';
COMMENT ON COLUMN cargamos.product_api.product_width IS 'Ancho del producto en CM';
COMMENT ON COLUMN cargamos.product_api.product_height IS 'Altura del producto en CM';
COMMENT ON COLUMN cargamos.product_api.product_weight IS 'Peso del producto en GRM';
COMMENT ON COLUMN cargamos.product_api.creation_date IS 'Fecha de creacion del producto';
COMMENT ON COLUMN cargamos.product_api.last_update_date IS 'Fecha de actualizacion del producto';

-- Permissions

ALTER TABLE cargamos.product_api OWNER TO postgres;
GRANT ALL ON TABLE cargamos.product_api TO postgres;




-- Permissions

GRANT ALL ON SCHEMA cargamos TO postgres;
