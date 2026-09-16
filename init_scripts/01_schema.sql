--
-- PostgreSQL database dump
--


-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.usuario_rol DROP CONSTRAINT IF EXISTS usuario_rol_id_usuario_fkey;
ALTER TABLE IF EXISTS ONLY public.usuario_rol DROP CONSTRAINT IF EXISTS usuario_rol_id_rol_fkey;
ALTER TABLE IF EXISTS ONLY public.registro_personal DROP CONSTRAINT IF EXISTS registro_personal_id_sub_novedad_fkey;
ALTER TABLE IF EXISTS ONLY public.registro_personal DROP CONSTRAINT IF EXISTS registro_personal_id_reporte_fkey;
ALTER TABLE IF EXISTS ONLY public.registro_personal DROP CONSTRAINT IF EXISTS registro_personal_id_personal_fkey;
ALTER TABLE IF EXISTS ONLY public.usuario_rol DROP CONSTRAINT IF EXISTS usuario_rol_pkey;
ALTER TABLE IF EXISTS ONLY public.usuario DROP CONSTRAINT IF EXISTS usuario_pkey;
ALTER TABLE IF EXISTS ONLY public.usuario DROP CONSTRAINT IF EXISTS usuario_correo_key;
ALTER TABLE IF EXISTS ONLY public.sub_novedades DROP CONSTRAINT IF EXISTS sub_novedades_pkey;
ALTER TABLE IF EXISTS ONLY public.sub_novedades DROP CONSTRAINT IF EXISTS sub_novedades_nombre_key;
ALTER TABLE IF EXISTS ONLY public.rol DROP CONSTRAINT IF EXISTS rol_pkey;
ALTER TABLE IF EXISTS ONLY public.rol DROP CONSTRAINT IF EXISTS rol_nombre_key;
ALTER TABLE IF EXISTS ONLY public.reportes DROP CONSTRAINT IF EXISTS reportes_pkey;
ALTER TABLE IF EXISTS ONLY public.reportes DROP CONSTRAINT IF EXISTS reportes_fecha_key;
ALTER TABLE IF EXISTS ONLY public.registro_personal DROP CONSTRAINT IF EXISTS registro_personal_pkey;
ALTER TABLE IF EXISTS ONLY public.personal DROP CONSTRAINT IF EXISTS personal_pkey;
ALTER TABLE IF EXISTS ONLY public.personal DROP CONSTRAINT IF EXISTS personal_cedula_key;
ALTER TABLE IF EXISTS ONLY public.google_oauth_tokens DROP CONSTRAINT IF EXISTS google_oauth_tokens_pkey;
ALTER TABLE IF EXISTS public.usuario ALTER COLUMN id_usuario DROP DEFAULT;
ALTER TABLE IF EXISTS public.sub_novedades ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.rol ALTER COLUMN id_rol DROP DEFAULT;
ALTER TABLE IF EXISTS public.reportes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.registro_personal ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.personal ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS public.usuario_rol;
DROP SEQUENCE IF EXISTS public.usuario_id_usuario_seq;
DROP TABLE IF EXISTS public.usuario;
DROP SEQUENCE IF EXISTS public.sub_novedades_id_seq;
DROP TABLE IF EXISTS public.sub_novedades;
DROP SEQUENCE IF EXISTS public.rol_id_rol_seq;
DROP TABLE IF EXISTS public.rol;
DROP SEQUENCE IF EXISTS public.reportes_id_seq;
DROP TABLE IF EXISTS public.reportes;
DROP SEQUENCE IF EXISTS public.registro_personal_id_seq;
DROP TABLE IF EXISTS public.registro_personal;
DROP SEQUENCE IF EXISTS public.personal_id_seq;
DROP TABLE IF EXISTS public.personal;
DROP TABLE IF EXISTS public.google_oauth_tokens;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: google_oauth_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.google_oauth_tokens (
    correo_google character varying(255) NOT NULL,
    token_json text NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.google_oauth_tokens OWNER TO postgres;

--
-- Name: personal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personal (
    id integer NOT NULL,
    cedula bigint,
    nombre character varying(255),
    fecha_retiro character varying(50)
);


ALTER TABLE public.personal OWNER TO postgres;

--
-- Name: personal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.personal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.personal_id_seq OWNER TO postgres;

--
-- Name: personal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.personal_id_seq OWNED BY public.personal.id;


--
-- Name: registro_personal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registro_personal (
    id integer NOT NULL,
    id_reporte integer,
    id_personal integer,
    id_sub_novedad integer,
    descripcion text,
    fecha_inicio character varying(50),
    fecha_final character varying(50)
);


ALTER TABLE public.registro_personal OWNER TO postgres;

--
-- Name: registro_personal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registro_personal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registro_personal_id_seq OWNER TO postgres;

--
-- Name: registro_personal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registro_personal_id_seq OWNED BY public.registro_personal.id;


--
-- Name: reportes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reportes (
    id integer NOT NULL,
    fecha character varying(50),
    archivo character varying(255)
);


ALTER TABLE public.reportes OWNER TO postgres;

--
-- Name: reportes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reportes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reportes_id_seq OWNER TO postgres;

--
-- Name: reportes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reportes_id_seq OWNED BY public.reportes.id;


--
-- Name: rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol (
    id_rol integer NOT NULL,
    nombre character varying(255) NOT NULL,
    descripcion text
);


ALTER TABLE public.rol OWNER TO postgres;

--
-- Name: rol_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rol_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rol_id_rol_seq OWNER TO postgres;

--
-- Name: rol_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rol_id_rol_seq OWNED BY public.rol.id_rol;


--
-- Name: sub_novedades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sub_novedades (
    id integer NOT NULL,
    nombre character varying(255)
);


ALTER TABLE public.sub_novedades OWNER TO postgres;

--
-- Name: sub_novedades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sub_novedades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sub_novedades_id_seq OWNER TO postgres;

--
-- Name: sub_novedades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sub_novedades_id_seq OWNED BY public.sub_novedades.id;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    nombre character varying(255) NOT NULL,
    correo character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    activo boolean DEFAULT true,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ultimo_login timestamp without time zone
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_usuario_seq OWNER TO postgres;

--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_usuario_seq OWNED BY public.usuario.id_usuario;


--
-- Name: usuario_rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario_rol (
    id_usuario integer NOT NULL,
    id_rol integer NOT NULL
);


ALTER TABLE public.usuario_rol OWNER TO postgres;

--
-- Name: personal id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal ALTER COLUMN id SET DEFAULT nextval('public.personal_id_seq'::regclass);


--
-- Name: registro_personal id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_personal ALTER COLUMN id SET DEFAULT nextval('public.registro_personal_id_seq'::regclass);


--
-- Name: reportes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes ALTER COLUMN id SET DEFAULT nextval('public.reportes_id_seq'::regclass);


--
-- Name: rol id_rol; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol ALTER COLUMN id_rol SET DEFAULT nextval('public.rol_id_rol_seq'::regclass);


--
-- Name: sub_novedades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sub_novedades ALTER COLUMN id SET DEFAULT nextval('public.sub_novedades_id_seq'::regclass);


--
-- Name: usuario id_usuario; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuario_id_usuario_seq'::regclass);


--
-- Name: google_oauth_tokens google_oauth_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.google_oauth_tokens
    ADD CONSTRAINT google_oauth_tokens_pkey PRIMARY KEY (correo_google);


--
-- Name: personal personal_cedula_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal
    ADD CONSTRAINT personal_cedula_key UNIQUE (cedula);


--
-- Name: personal personal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal
    ADD CONSTRAINT personal_pkey PRIMARY KEY (id);


--
-- Name: registro_personal registro_personal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_personal
    ADD CONSTRAINT registro_personal_pkey PRIMARY KEY (id);


--
-- Name: reportes reportes_fecha_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes
    ADD CONSTRAINT reportes_fecha_key UNIQUE (fecha);


--
-- Name: reportes reportes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes
    ADD CONSTRAINT reportes_pkey PRIMARY KEY (id);


--
-- Name: rol rol_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_nombre_key UNIQUE (nombre);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- Name: sub_novedades sub_novedades_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sub_novedades
    ADD CONSTRAINT sub_novedades_nombre_key UNIQUE (nombre);


--
-- Name: sub_novedades sub_novedades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sub_novedades
    ADD CONSTRAINT sub_novedades_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_correo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_correo_key UNIQUE (correo);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- Name: usuario_rol usuario_rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_rol
    ADD CONSTRAINT usuario_rol_pkey PRIMARY KEY (id_usuario, id_rol);


--
-- Name: registro_personal registro_personal_id_personal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_personal
    ADD CONSTRAINT registro_personal_id_personal_fkey FOREIGN KEY (id_personal) REFERENCES public.personal(id);


--
-- Name: registro_personal registro_personal_id_reporte_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_personal
    ADD CONSTRAINT registro_personal_id_reporte_fkey FOREIGN KEY (id_reporte) REFERENCES public.reportes(id);


--
-- Name: registro_personal registro_personal_id_sub_novedad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_personal
    ADD CONSTRAINT registro_personal_id_sub_novedad_fkey FOREIGN KEY (id_sub_novedad) REFERENCES public.sub_novedades(id);


--
-- Name: usuario_rol usuario_rol_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_rol
    ADD CONSTRAINT usuario_rol_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol) ON DELETE CASCADE;


--
-- Name: usuario_rol usuario_rol_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_rol
    ADD CONSTRAINT usuario_rol_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--



--
-- Datos iniciales / Catálogo de roles y novedades (Semillas del sistema)
--

INSERT INTO public.rol (id_rol, nombre, descripcion) VALUES (1, 'ADMINISTRATIVO', 'Acceso de administración total al sistema') ON CONFLICT (id_rol) DO NOTHING;
SELECT pg_catalog.setval('public.rol_id_rol_seq', 2, true);

INSERT INTO public.sub_novedades (id, nombre) VALUES
  (1, 'CDO UNIDAD'),
  (2, 'VACACIONES'),
  (3, 'CICLO CODE'),
  (4, 'PERMISO'),
  (5, 'AREA OPERACIONES'),
  (6, 'CURSOS'),
  (7, 'PENDIENTE PRESENTACION'),
  (8, 'INCAPACIDAD'),
  (9, 'COMISION DE SERVICIO'),
  (10, 'RETIRO ASISTIDO'),
  (11, 'COMITÉ INCORPORACION'),
  (12, 'HOSPITALIZADOS'),
  (13, 'REENTREANAMIENTO'),
  (14, 'CURSO DE LEY'),
  (15, 'RETARDADO'),
  (16, 'I/R'),
  (17, 'DESERTOR'),
  (18, 'RETIRO EN TRAMITE'),
  (19, 'DETENIDO CENTRO PENITENCIARIO'),
  (20, 'TRATAMIENTO LESIHMANIASIS')
ON CONFLICT (id) DO NOTHING;
SELECT pg_catalog.setval('public.sub_novedades_id_seq', 20, true);
