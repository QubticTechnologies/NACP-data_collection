--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: user; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "user";


ALTER SCHEMA "user" OWNER TO postgres;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: age_group_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.age_group_enum AS ENUM (
    '1',
    '2',
    '3',
    '4',
    '5',
    '6'
);


ALTER TYPE public.age_group_enum OWNER TO postgres;

--
-- Name: agri_training_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.agri_training_enum AS ENUM (
    'Yes',
    'No'
);


ALTER TYPE public.agri_training_enum OWNER TO postgres;

--
-- Name: animal_age_group; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.animal_age_group AS ENUM (
    'Less than 6 months',
    '6 months to 1 year',
    '1 - 2 years',
    'More than 2 years'
);


ALTER TYPE public.animal_age_group OWNER TO postgres;

--
-- Name: animal_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.animal_type AS ENUM (
    'Cattle',
    'Sheep',
    'Goats',
    'Pigs',
    'Horse Kind'
);


ALTER TYPE public.animal_type OWNER TO postgres;

--
-- Name: crop_method_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.crop_method_enum AS ENUM (
    'tunnel',
    'open_field',
    'net_house',
    'greenhouse',
    'netting',
    'other'
);


ALTER TYPE public.crop_method_enum OWNER TO postgres;

--
-- Name: crop_type_code; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.crop_type_code AS ENUM (
    'P',
    'T'
);


ALTER TYPE public.crop_type_code OWNER TO postgres;

--
-- Name: disposal_method; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.disposal_method AS ENUM (
    'Sold',
    'Slaughtered',
    'Died',
    'Other'
);


ALTER TYPE public.disposal_method OWNER TO postgres;

--
-- Name: education_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.education_enum AS ENUM (
    'No Schooling',
    'Primary',
    'Junior Secondary',
    'Senior Secondary',
    'Undergraduate',
    'Masters',
    'Doctorate',
    'Vocational',
    'Professional Designation'
);


ALTER TYPE public.education_enum OWNER TO postgres;

--
-- Name: education_level_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.education_level_enum AS ENUM (
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9'
);


ALTER TYPE public.education_level_enum OWNER TO postgres;

--
-- Name: labour_option; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.labour_option AS ENUM (
    'Yes',
    'No',
    'Not Applicable'
);


ALTER TYPE public.labour_option OWNER TO postgres;

--
-- Name: land_clearing_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.land_clearing_enum AS ENUM (
    'regenerative',
    'hand_clearing',
    'slash_burn',
    'small_machine',
    'large_machine'
);


ALTER TYPE public.land_clearing_enum OWNER TO postgres;

--
-- Name: main_duties_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.main_duties_enum AS ENUM (
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7'
);


ALTER TYPE public.main_duties_enum OWNER TO postgres;

--
-- Name: main_purpose_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.main_purpose_enum AS ENUM (
    'for_sale_only',
    'mainly_sale_some_consumption',
    'for_consumption_only',
    'mainly_consumption_some_sale'
);


ALTER TYPE public.main_purpose_enum OWNER TO postgres;

--
-- Name: marital_status_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.marital_status_enum AS ENUM (
    'Single',
    'Married',
    'Divorced',
    'Separated',
    'Widowed',
    'Common-Law',
    'Prefer not to disclose'
);


ALTER TYPE public.marital_status_enum OWNER TO postgres;

--
-- Name: nationality_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.nationality_enum AS ENUM (
    'Bahamian',
    'Other'
);


ALTER TYPE public.nationality_enum OWNER TO postgres;

--
-- Name: parcel_block; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.parcel_block AS ENUM (
    'Main Parcel',
    'Parcel #2',
    'Parcel #3',
    'Parcel #4'
);


ALTER TYPE public.parcel_block OWNER TO postgres;

--
-- Name: position_title_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.position_title_enum AS ENUM (
    '1',
    '2',
    '3',
    '4',
    '5'
);


ALTER TYPE public.position_title_enum OWNER TO postgres;

--
-- Name: poultry_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.poultry_type AS ENUM (
    'Chicken',
    'Duck',
    'Goose',
    'Turkey'
);


ALTER TYPE public.poultry_type OWNER TO postgres;

--
-- Name: primary_occupation_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.primary_occupation_enum AS ENUM (
    'Agriculture',
    'Other'
);


ALTER TYPE public.primary_occupation_enum OWNER TO postgres;

--
-- Name: sex_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sex_enum AS ENUM (
    'Male',
    'Female',
    'Other'
);


ALTER TYPE public.sex_enum OWNER TO postgres;

--
-- Name: tenure_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tenure_enum AS ENUM (
    'privately_owned',
    'generational_commonage',
    'privately_leased_rented',
    'crown_leased_rented',
    'squatting_private_land',
    'squatting_crown_land',
    'borrowed',
    'other'
);


ALTER TYPE public.tenure_enum OWNER TO postgres;

--
-- Name: use_land_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.use_land_enum AS ENUM (
    'temporary_crops',
    'temporary_meadows_pastures',
    'temporary_fallow',
    'permanent_crops',
    'permanent_meadows_pastures',
    'forest_wooded_land',
    'wetland',
    'farm_buildings_yards',
    'other'
);


ALTER TYPE public.use_land_enum OWNER TO postgres;

--
-- Name: working_time_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.working_time_enum AS ENUM (
    'N',
    'F',
    'P',
    'P3',
    'P6',
    'P7'
);


ALTER TYPE public.working_time_enum OWNER TO postgres;

--
-- Name: create_holding_labour_rows(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.create_holding_labour_rows() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Insert default questions for the new holder
    INSERT INTO holding_labour (
        holder_id, question_no, question_text, male_count, female_count, total_count, option_response
    ) VALUES
    (NEW.holder_id, 2, 'How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?', 0, 0, 0, NULL),
    (NEW.holder_id, 3, 'How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?', 0, 0, 0, NULL),
    (NEW.holder_id, 4, 'What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?', 0, 0, 0, NULL),
    (NEW.holder_id, 5, 'Did any of your workers have work permits?', NULL, NULL, NULL, 'Not Applicable'),
    (NEW.holder_id, 6, 'Were there any volunteer workers on the holding (i.e. unpaid labourers)?', NULL, NULL, NULL, 'Not Applicable'),
    (NEW.holder_id, 7, 'Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?', NULL, NULL, NULL, 'Not Applicable');

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.create_holding_labour_rows() OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agents (
    id integer NOT NULL,
    name text NOT NULL,
    agency text NOT NULL,
    user_id integer
);


ALTER TABLE public.agents OWNER TO postgres;

--
-- Name: agents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agents_id_seq OWNER TO postgres;

--
-- Name: agents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agents_id_seq OWNED BY public.agents.id;


--
-- Name: availability_form; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.availability_form (
    id integer NOT NULL,
    registration_id integer,
    available_days text[],
    available_times text[],
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.availability_form OWNER TO postgres;

--
-- Name: availability_form_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.availability_form_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.availability_form_id_seq OWNER TO postgres;

--
-- Name: availability_form_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.availability_form_id_seq OWNED BY public.availability_form.id;


--
-- Name: crop_information; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_information (
    id integer NOT NULL,
    holding_id integer NOT NULL,
    parcel_block public.parcel_block NOT NULL,
    crop_code character varying(20) NOT NULL,
    crop_name text NOT NULL,
    cycle_number smallint NOT NULL,
    area_acres numeric(8,2) NOT NULL,
    plants_organized integer NOT NULL,
    plants_scattered integer NOT NULL,
    planting_material_code smallint NOT NULL,
    crop_type public.crop_type_code NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT crop_information_area_acres_check CHECK ((area_acres >= (0)::numeric)),
    CONSTRAINT crop_information_cycle_number_check CHECK ((cycle_number > 0)),
    CONSTRAINT crop_information_planting_material_code_check CHECK (((planting_material_code >= 1) AND (planting_material_code <= 8))),
    CONSTRAINT crop_information_plants_organized_check CHECK ((plants_organized >= 0)),
    CONSTRAINT crop_information_plants_scattered_check CHECK ((plants_scattered >= 0))
);


ALTER TABLE public.crop_information OWNER TO postgres;

--
-- Name: crop_information_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.crop_information_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.crop_information_id_seq OWNER TO postgres;

--
-- Name: crop_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.crop_information_id_seq OWNED BY public.crop_information.id;


--
-- Name: crop_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_type (
    code character(1) NOT NULL,
    description text NOT NULL,
    CONSTRAINT crop_type_code_check CHECK ((code = ANY (ARRAY['P'::bpchar, 'T'::bpchar])))
);


ALTER TABLE public.crop_type OWNER TO postgres;

--
-- Name: general_information; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.general_information (
    id integer NOT NULL,
    holder_id integer,
    holding_id character varying(20),
    interview_date date,
    respondent_name character varying(255),
    respondent_phone character varying(20),
    respondent_email character varying(255),
    is_holder boolean,
    holder_name character varying(255),
    holder_phone character varying(20),
    holding_name character varying(255),
    holding_phone character varying(20),
    area character varying(255),
    city character varying(255),
    subdivision character varying(255),
    latitude double precision,
    longitude double precision,
    island character varying(255),
    address_street character varying(255),
    address_po character varying(255),
    legal_status character varying(50),
    status character varying(20) DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.general_information OWNER TO postgres;

--
-- Name: general_information_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.general_information_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.general_information_id_seq OWNER TO postgres;

--
-- Name: general_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.general_information_id_seq OWNED BY public.general_information.id;


--
-- Name: harvest_information; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.harvest_information (
    id integer NOT NULL,
    holding_id integer NOT NULL,
    parcel_block public.parcel_block NOT NULL,
    crops_harvested_produce integer NOT NULL,
    crops_harvested_plants integer NOT NULL,
    area_harvested numeric(8,2) NOT NULL,
    harvested_quantity numeric(12,3) NOT NULL,
    market_trade_code smallint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT harvest_information_area_harvested_check CHECK ((area_harvested >= (0)::numeric)),
    CONSTRAINT harvest_information_crops_harvested_plants_check CHECK ((crops_harvested_plants >= 0)),
    CONSTRAINT harvest_information_crops_harvested_produce_check CHECK ((crops_harvested_produce >= 0)),
    CONSTRAINT harvest_information_harvested_quantity_check CHECK ((harvested_quantity >= (0)::numeric))
);


ALTER TABLE public.harvest_information OWNER TO postgres;

--
-- Name: harvest_information_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.harvest_information_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.harvest_information_id_seq OWNER TO postgres;

--
-- Name: harvest_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.harvest_information_id_seq OWNED BY public.harvest_information.id;


--
-- Name: holder_information; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holder_information (
    id integer NOT NULL,
    farm_id integer NOT NULL,
    holder_number smallint NOT NULL,
    full_name character varying(100) NOT NULL,
    sex public.sex_enum NOT NULL,
    date_of_birth date NOT NULL,
    marital_status public.marital_status_enum,
    nationality public.nationality_enum,
    nationality_other character varying(50),
    highest_education public.education_enum,
    agri_training public.agri_training_enum,
    primary_occupation public.primary_occupation_enum,
    primary_occupation_other character varying(50),
    secondary_occupation character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT holder_information_holder_number_check CHECK (((holder_number >= 1) AND (holder_number <= 3)))
);


ALTER TABLE public.holder_information OWNER TO postgres;

--
-- Name: holder_information_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holder_information_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holder_information_id_seq OWNER TO postgres;

--
-- Name: holder_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holder_information_id_seq OWNED BY public.holder_information.id;


--
-- Name: holder_survey_progress; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holder_survey_progress (
    id integer NOT NULL,
    holder_id integer NOT NULL,
    section_id integer NOT NULL,
    completed boolean DEFAULT false,
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.holder_survey_progress OWNER TO postgres;

--
-- Name: holder_survey_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holder_survey_progress_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holder_survey_progress_id_seq OWNER TO postgres;

--
-- Name: holder_survey_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holder_survey_progress_id_seq OWNED BY public.holder_survey_progress.id;


--
-- Name: holders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holders (
    holder_id integer NOT NULL,
    name text NOT NULL,
    owner_id integer,
    status character varying(20) DEFAULT 'pending'::character varying,
    submitted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    agent_reviewed_at timestamp without time zone,
    assigned_agent_id integer,
    agent_review_deadline timestamp without time zone,
    latitude double precision DEFAULT 0,
    longitude double precision DEFAULT 0,
    sex character varying(10),
    date_of_birth date,
    age integer,
    marital_status character varying(20),
    nationality character varying(50),
    nationality_other character varying(50),
    education_level character varying(50),
    agri_training character varying(10),
    primary_occupation character varying(50),
    primary_occupation_other character varying(50),
    secondary_occupation character varying(50),
    total_persons integer DEFAULT 1,
    persons_under_14_male integer DEFAULT 0,
    persons_under_14_female integer DEFAULT 0,
    persons_working_male integer DEFAULT 0,
    persons_working_female integer DEFAULT 0,
    farm_id integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    highest_education character varying(50)
);


ALTER TABLE public.holders OWNER TO postgres;

--
-- Name: holders_holder_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holders_holder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holders_holder_id_seq OWNER TO postgres;

--
-- Name: holders_holder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holders_holder_id_seq OWNED BY public.holders.holder_id;


--
-- Name: holders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holders_id_seq OWNER TO postgres;

--
-- Name: holders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holders_id_seq OWNED BY public.holders.holder_id;


--
-- Name: holding_labour; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holding_labour (
    id integer NOT NULL,
    holder_id integer,
    question_no smallint NOT NULL,
    question_text text NOT NULL,
    male_count smallint,
    female_count smallint,
    total_count smallint,
    option_response public.labour_option,
    CONSTRAINT chk_counts_or_option CHECK (((((question_no >= 2) AND (question_no <= 4)) AND (male_count IS NOT NULL) AND (female_count IS NOT NULL) AND (total_count IS NOT NULL) AND (option_response IS NULL)) OR (((question_no >= 5) AND (question_no <= 7)) AND (male_count IS NULL) AND (female_count IS NULL) AND (total_count IS NULL) AND (option_response IS NOT NULL)))),
    CONSTRAINT holding_labour_female_count_check CHECK (((female_count >= 0) AND (female_count <= 900))),
    CONSTRAINT holding_labour_male_count_check CHECK (((male_count >= 0) AND (male_count <= 900))),
    CONSTRAINT holding_labour_total_count_check CHECK (((total_count >= 0) AND (total_count <= 900)))
);


ALTER TABLE public.holding_labour OWNER TO postgres;

--
-- Name: holding_labour_permanent; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holding_labour_permanent (
    id integer NOT NULL,
    holding_id integer NOT NULL,
    position_title smallint NOT NULL,
    sex character(1) NOT NULL,
    age_code smallint NOT NULL,
    nationality text NOT NULL,
    education_code smallint NOT NULL,
    has_agri_training boolean DEFAULT false,
    main_duties_code smallint NOT NULL,
    working_time_code character varying(2) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT holding_labour_details_age_code_check CHECK (((age_code >= 1) AND (age_code <= 6))),
    CONSTRAINT holding_labour_details_education_code_check CHECK (((education_code >= 1) AND (education_code <= 9))),
    CONSTRAINT holding_labour_details_main_duties_code_check CHECK (((main_duties_code >= 1) AND (main_duties_code <= 7))),
    CONSTRAINT holding_labour_details_position_title_check CHECK (((position_title >= 1) AND (position_title <= 5))),
    CONSTRAINT holding_labour_details_sex_check CHECK ((sex = ANY (ARRAY['M'::bpchar, 'F'::bpchar]))),
    CONSTRAINT holding_labour_details_working_time_code_check CHECK (((working_time_code)::text = ANY ((ARRAY['N'::character varying, 'F'::character varying, 'P'::character varying, 'P3'::character varying, 'P6'::character varying, 'P7'::character varying])::text[])))
);


ALTER TABLE public.holding_labour_permanent OWNER TO postgres;

--
-- Name: holding_labour_details_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holding_labour_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holding_labour_details_id_seq OWNER TO postgres;

--
-- Name: holding_labour_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holding_labour_details_id_seq OWNED BY public.holding_labour_permanent.id;


--
-- Name: holding_labour_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holding_labour_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holding_labour_id_seq OWNER TO postgres;

--
-- Name: holding_labour_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holding_labour_id_seq OWNED BY public.holding_labour.id;


--
-- Name: holdings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holdings (
    id integer NOT NULL,
    farm_name character varying(100) NOT NULL,
    island_id integer
);


ALTER TABLE public.holdings OWNER TO postgres;

--
-- Name: holdings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holdings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holdings_id_seq OWNER TO postgres;

--
-- Name: holdings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holdings_id_seq OWNED BY public.holdings.id;


--
-- Name: household_information; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.household_information (
    id integer NOT NULL,
    holder_id integer,
    holder_number character varying(50),
    relationship_to_holder character varying(100),
    sex character varying(10),
    age integer,
    education_level character varying(100),
    primary_occupation character varying(100),
    secondary_occupation character varying(100),
    working_time_on_holding character varying(50),
    total_persons integer,
    persons_under_14_male integer,
    persons_under_14_female integer,
    persons_14plus_male integer,
    persons_14plus_female integer,
    persons_working_male_paid integer,
    persons_working_male_unpaid integer,
    persons_working_female_paid integer,
    persons_working_female_unpaid integer
);


ALTER TABLE public.household_information OWNER TO postgres;

--
-- Name: household_information_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.household_information_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.household_information_id_seq OWNER TO postgres;

--
-- Name: household_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.household_information_id_seq OWNED BY public.household_information.id;


--
-- Name: household_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.household_summary (
    holdings_id integer NOT NULL,
    holder_number integer NOT NULL,
    total_persons integer,
    persons_under_14_male integer,
    persons_under_14_female integer,
    persons_14plus_male integer,
    persons_14plus_female integer
);


ALTER TABLE public.household_summary OWNER TO postgres;

--
-- Name: islands; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.islands (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    island_group character varying(50),
    population integer,
    area_sqkm numeric(10,2),
    bounds public.geometry(Polygon,4326),
    settlements json,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.islands OWNER TO postgres;

--
-- Name: islands_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.islands_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.islands_id_seq OWNER TO postgres;

--
-- Name: islands_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.islands_id_seq OWNED BY public.islands.id;


--
-- Name: labour_questions_template; Type: TABLE; Schema: public; Owner: agri_user
--

CREATE TABLE public.labour_questions_template (
    question_no integer NOT NULL,
    question_text text NOT NULL
);


ALTER TABLE public.labour_questions_template OWNER TO agri_user;

--
-- Name: land_use; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.land_use (
    id integer NOT NULL,
    holding_id integer NOT NULL,
    total_area_acres numeric(10,2),
    years_agriculture numeric(5,2),
    main_purpose public.main_purpose_enum NOT NULL,
    num_parcels numeric(5,2),
    location character varying(200),
    crop_methods public.crop_method_enum[],
    CONSTRAINT land_use_num_parcels_check CHECK ((num_parcels > (0)::numeric)),
    CONSTRAINT land_use_total_area_acres_check CHECK ((total_area_acres > (0)::numeric)),
    CONSTRAINT land_use_years_agriculture_check CHECK ((years_agriculture >= (0)::numeric))
);


ALTER TABLE public.land_use OWNER TO postgres;

--
-- Name: land_use_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.land_use_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.land_use_id_seq OWNER TO postgres;

--
-- Name: land_use_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.land_use_id_seq OWNED BY public.land_use.id;


--
-- Name: land_use_parcels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.land_use_parcels (
    id integer NOT NULL,
    land_use_id integer NOT NULL,
    parcel_no numeric(5,2),
    total_acres numeric(10,2),
    developed_acres numeric(10,2),
    tenure public.tenure_enum NOT NULL,
    use_of_land public.use_land_enum NOT NULL,
    irrigated_area numeric(10,2),
    land_clearing public.land_clearing_enum NOT NULL,
    CONSTRAINT land_use_parcels_developed_acres_check CHECK ((developed_acres >= (0)::numeric)),
    CONSTRAINT land_use_parcels_irrigated_area_check CHECK ((irrigated_area >= (0)::numeric)),
    CONSTRAINT land_use_parcels_parcel_no_check CHECK ((parcel_no > (0)::numeric)),
    CONSTRAINT land_use_parcels_total_acres_check CHECK ((total_acres > (0)::numeric))
);


ALTER TABLE public.land_use_parcels OWNER TO postgres;

--
-- Name: land_use_parcels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.land_use_parcels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.land_use_parcels_id_seq OWNER TO postgres;

--
-- Name: land_use_parcels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.land_use_parcels_id_seq OWNED BY public.land_use_parcels.id;


--
-- Name: livestock_information; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.livestock_information (
    id integer NOT NULL,
    holding_id integer NOT NULL,
    animal_type public.animal_type NOT NULL,
    medicines_used text,
    animal_age_group public.animal_age_group NOT NULL,
    males_count integer NOT NULL,
    females_count integer NOT NULL,
    total_count integer GENERATED ALWAYS AS ((males_count + females_count)) STORED,
    disposal_method public.disposal_method,
    average_dressed_weight numeric(6,2),
    average_price_per_unit numeric(10,2),
    total_value numeric(12,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT livestock_information_females_count_check CHECK ((females_count >= 0)),
    CONSTRAINT livestock_information_males_count_check CHECK ((males_count >= 0))
);


ALTER TABLE public.livestock_information OWNER TO postgres;

--
-- Name: livestock_information_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.livestock_information_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.livestock_information_id_seq OWNER TO postgres;

--
-- Name: livestock_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.livestock_information_id_seq OWNED BY public.livestock_information.id;


--
-- Name: market_trade_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_trade_codes (
    code smallint NOT NULL,
    description text NOT NULL,
    CONSTRAINT market_trade_codes_code_check CHECK (((code >= 1) AND (code <= 11)))
);


ALTER TABLE public.market_trade_codes OWNER TO postgres;

--
-- Name: planting_material; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.planting_material (
    code smallint NOT NULL,
    description text NOT NULL,
    CONSTRAINT planting_material_code_check CHECK (((code >= 1) AND (code <= 8)))
);


ALTER TABLE public.planting_material OWNER TO postgres;

--
-- Name: registration_form; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registration_form (
    id integer NOT NULL,
    consent boolean NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(150),
    telephone character varying(20),
    cell character varying(20),
    communication_methods text[],
    island character varying(50) NOT NULL,
    settlement character varying(100) NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    available_days text[],
    available_times text[],
    interview_methods text[],
    street_address text,
    neighborhood text,
    postal_code text
);


ALTER TABLE public.registration_form OWNER TO postgres;

--
-- Name: registration_form_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registration_form_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registration_form_id_seq OWNER TO postgres;

--
-- Name: registration_form_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registration_form_id_seq OWNED BY public.registration_form.id;


--
-- Name: survey_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.survey_questions (
    id integer NOT NULL,
    section_id integer NOT NULL,
    question_no integer NOT NULL,
    question_text text NOT NULL
);


ALTER TABLE public.survey_questions OWNER TO postgres;

--
-- Name: survey_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.survey_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.survey_questions_id_seq OWNER TO postgres;

--
-- Name: survey_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.survey_questions_id_seq OWNED BY public.survey_questions.id;


--
-- Name: survey_responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.survey_responses (
    id integer NOT NULL,
    holder_id integer NOT NULL,
    question_id integer NOT NULL,
    option_response text,
    section text
);


ALTER TABLE public.survey_responses OWNER TO postgres;

--
-- Name: survey_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.survey_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.survey_responses_id_seq OWNER TO postgres;

--
-- Name: survey_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.survey_responses_id_seq OWNED BY public.survey_responses.id;


--
-- Name: type_of_poultry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_of_poultry (
    id integer NOT NULL,
    holding_id integer NOT NULL,
    poultry_type public.poultry_type NOT NULL,
    medicines_used text,
    number_of_cycles integer NOT NULL,
    number_of_broilers integer NOT NULL,
    number_of_layers integer NOT NULL,
    total_count integer GENERATED ALWAYS AS ((number_of_broilers + number_of_layers)) STORED,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT type_of_poultry_number_of_broilers_check CHECK ((number_of_broilers >= 0)),
    CONSTRAINT type_of_poultry_number_of_cycles_check CHECK ((number_of_cycles >= 0)),
    CONSTRAINT type_of_poultry_number_of_layers_check CHECK ((number_of_layers >= 0))
);


ALTER TABLE public.type_of_poultry OWNER TO postgres;

--
-- Name: type_of_poultry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_of_poultry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_of_poultry_id_seq OWNER TO postgres;

--
-- Name: type_of_poultry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_of_poultry_id_seq OWNED BY public.type_of_poultry.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password_hash text NOT NULL,
    role character varying(20) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    email character varying(255),
    status character varying(20),
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['Admin'::character varying, 'Agent'::character varying, 'Holder'::character varying])::text[]))),
    CONSTRAINT users_status_check CHECK (((status)::text = ANY (ARRAY['active'::text, 'pending'::text, 'inactive'::text, 'approved'::text])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: agents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agents ALTER COLUMN id SET DEFAULT nextval('public.agents_id_seq'::regclass);


--
-- Name: availability_form id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.availability_form ALTER COLUMN id SET DEFAULT nextval('public.availability_form_id_seq'::regclass);


--
-- Name: crop_information id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_information ALTER COLUMN id SET DEFAULT nextval('public.crop_information_id_seq'::regclass);


--
-- Name: general_information id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_information ALTER COLUMN id SET DEFAULT nextval('public.general_information_id_seq'::regclass);


--
-- Name: harvest_information id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.harvest_information ALTER COLUMN id SET DEFAULT nextval('public.harvest_information_id_seq'::regclass);


--
-- Name: holder_information id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holder_information ALTER COLUMN id SET DEFAULT nextval('public.holder_information_id_seq'::regclass);


--
-- Name: holder_survey_progress id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holder_survey_progress ALTER COLUMN id SET DEFAULT nextval('public.holder_survey_progress_id_seq'::regclass);


--
-- Name: holders holder_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holders ALTER COLUMN holder_id SET DEFAULT nextval('public.holders_holder_id_seq'::regclass);


--
-- Name: holding_labour id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holding_labour ALTER COLUMN id SET DEFAULT nextval('public.holding_labour_id_seq'::regclass);


--
-- Name: holding_labour_permanent id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holding_labour_permanent ALTER COLUMN id SET DEFAULT nextval('public.holding_labour_details_id_seq'::regclass);


--
-- Name: holdings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings ALTER COLUMN id SET DEFAULT nextval('public.holdings_id_seq'::regclass);


--
-- Name: household_information id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_information ALTER COLUMN id SET DEFAULT nextval('public.household_information_id_seq'::regclass);


--
-- Name: islands id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.islands ALTER COLUMN id SET DEFAULT nextval('public.islands_id_seq'::regclass);


--
-- Name: land_use id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_use ALTER COLUMN id SET DEFAULT nextval('public.land_use_id_seq'::regclass);


--
-- Name: land_use_parcels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_use_parcels ALTER COLUMN id SET DEFAULT nextval('public.land_use_parcels_id_seq'::regclass);


--
-- Name: livestock_information id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.livestock_information ALTER COLUMN id SET DEFAULT nextval('public.livestock_information_id_seq'::regclass);


--
-- Name: registration_form id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_form ALTER COLUMN id SET DEFAULT nextval('public.registration_form_id_seq'::regclass);


--
-- Name: survey_questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.survey_questions ALTER COLUMN id SET DEFAULT nextval('public.survey_questions_id_seq'::regclass);


--
-- Name: survey_responses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.survey_responses ALTER COLUMN id SET DEFAULT nextval('public.survey_responses_id_seq'::regclass);


--
-- Name: type_of_poultry id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_of_poultry ALTER COLUMN id SET DEFAULT nextval('public.type_of_poultry_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: agents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agents (id, name, agency, user_id) FROM stdin;
\.


--
-- Data for Name: availability_form; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.availability_form (id, registration_id, available_days, available_times, created_at) FROM stdin;
\.


--
-- Data for Name: crop_information; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_information (id, holding_id, parcel_block, crop_code, crop_name, cycle_number, area_acres, plants_organized, plants_scattered, planting_material_code, crop_type, created_at) FROM stdin;
\.


--
-- Data for Name: crop_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_type (code, description) FROM stdin;
P	Permanent
T	Temporary
\.


--
-- Data for Name: general_information; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.general_information (id, holder_id, holding_id, interview_date, respondent_name, respondent_phone, respondent_email, is_holder, holder_name, holder_phone, holding_name, holding_phone, area, city, subdivision, latitude, longitude, island, address_street, address_po, legal_status, status, created_at) FROM stdin;
1	2	1	2025-10-23	job gumbs	242 4684005	mycriticalthinking123@gmail.com	t	job gumbs	242 4684005	q-farms	242 668-9074	gladstone	nassau	south	25.3	75.2	New Providence	zion blv	N-59195	Joint-Partnership	pending	2025-10-06 13:40:41.166364
2	2	1	2025-10-22	job gumbs	242 568904	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	2426843567	nassau	foxhill	south	24.01456	77.20314	New Providence	loan street	N-59195	Household	pending	2025-10-06 20:28:52.281694
3	2	1	2025-10-23	job gumbs	242- 329-4567	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	(242)567-6789	nassau	foxhill	SOUTH	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 20:43:59.040265
4	2	1	2025-10-23	job gumbs	242-466-5576	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-466-5678	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 20:48:42.47947
5	2	1	2025-10-23	job gumbs	242-466-5576	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-466-5678	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 20:48:44.546435
6	2	1	2025-10-23	timothy gumbs	242-356-7891	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farm	242-567-8907	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 21:10:31.827923
7	2	1	2025-10-23	timothy gumbs	242-356-7891	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farm	242-567-8907	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 21:10:42.733138
8	2	1	2025-10-23	timothy gumbs	242-456-7689	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-456-6789	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 21:19:48.156219
9	2	1	2025-10-23	timothy gumbs	242-456-7689	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-456-6789	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 21:19:57.603685
10	2	1	2025-10-23	timothy gumbs	242567-8701	mycriticalthinking123@gmsil.com	t	job gumbs	242 668-9074	q-farms	242-468-45671	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 21:32:32.840216
11	2	1	2025-10-23	timothy gumbs	242-468-5055	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farm	242-468-4005	nassau	foxhill	south	24.01456	77.20314	New Providence	lawn street	N-59195	Household	pending	2025-10-06 21:46:57.820186
12	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Non-Household	pending	2025-10-06 22:15:52.671111
13	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-06 22:24:49.192279
14	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-06 22:30:53.257288
15	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-06 22:35:39.222887
16	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-06 22:56:22.032758
17	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 00:14:51.68503
18	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 00:18:17.795047
19	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 00:22:28.143535
20	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 00:29:32.31932
21	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 01:04:13.155372
22	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 01:32:06.776175
23	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 01:39:42.618794
24	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 01:45:10.353621
25	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 08:49:13.035761
26	2	1	2025-10-23	timothy gumbs	242-455-7009	mycriticalthinking123@gmail.com	t	job gumbs	242 668-9074	q-farms	242-468-45556	nassau	foxhill	south	25.023	77.32	New Providence	lawn street	N-59195	Household	pending	2025-10-07 08:54:42.276897
\.


--
-- Data for Name: harvest_information; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.harvest_information (id, holding_id, parcel_block, crops_harvested_produce, crops_harvested_plants, area_harvested, harvested_quantity, market_trade_code, created_at) FROM stdin;
\.


--
-- Data for Name: holder_information; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holder_information (id, farm_id, holder_number, full_name, sex, date_of_birth, marital_status, nationality, nationality_other, highest_education, agri_training, primary_occupation, primary_occupation_other, secondary_occupation, created_at) FROM stdin;
\.


--
-- Data for Name: holder_survey_progress; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holder_survey_progress (id, holder_id, section_id, completed, updated_at) FROM stdin;
8	2	6	f	2025-09-27 22:19:25.17902
15	5	6	f	2025-09-29 17:18:59.147783
13	5	4	t	2025-09-29 17:18:59.147783
14	5	5	t	2025-09-29 17:18:59.147783
3	2	1	t	2025-09-27 22:19:25.17902
4	2	2	t	2025-09-27 22:19:25.17902
5	2	3	t	2025-09-27 22:19:25.17902
6	2	4	t	2025-09-27 22:19:25.17902
7	2	5	t	2025-09-27 22:19:25.17902
10	5	1	t	2025-09-29 17:18:59.147783
11	5	2	t	2025-09-29 17:18:59.147783
12	5	3	t	2025-09-29 17:18:59.147783
\.


--
-- Data for Name: holders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holders (holder_id, name, owner_id, status, submitted_at, agent_reviewed_at, assigned_agent_id, agent_review_deadline, latitude, longitude, sex, date_of_birth, age, marital_status, nationality, nationality_other, education_level, agri_training, primary_occupation, primary_occupation_other, secondary_occupation, total_persons, persons_under_14_male, persons_under_14_female, persons_working_male, persons_working_female, farm_id, created_at, updated_at, highest_education) FROM stdin;
2	job gumbs	3	active	2025-09-27 19:52:33.448473	\N	\N	\N	25.023	-77.32	Male	1985-07-02	\N	Married	\N	\N	\N	Yes	Other	\N	machine operator	1	0	0	0	0	1	2025-09-30 10:31:06.098202	2025-10-13 21:46:11.336339	Senior Secondary
5	sherline chase	4	active	2025-09-29 17:18:59.147783	\N	\N	\N	25.01646	-77.35	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	1	0	0	0	0	1	2025-09-30 10:31:06.098202	2025-10-14 16:42:19.123508	\N
18	job gumbs	\N	pending	2025-09-30 00:44:23.306522	\N	\N	\N	0	0	Male	1985-07-02	40	\N	\N	\N	\N	\N	\N	\N	\N	1	0	0	0	0	1	2025-09-30 10:31:06.098202	2025-09-30 10:31:06.098202	\N
24	job gumbs	\N	pending	2025-10-01 18:58:53.014943	\N	\N	\N	0	0	Male	1985-07-02	\N	Married	Other	Trinidadian	\N	Yes	Other	IT	Farmer	1	0	0	0	0	1	2025-10-01 18:58:53.014943	2025-10-01 18:58:53.014943	Senior Secondary
25	Sherline Chase	\N	pending	2025-10-01 22:50:32.539787	\N	\N	\N	0	0	Female	1978-06-16	\N	Married	Other	Trinidadian	\N	Yes	Other	Pole Dancer	Agriculture	1	0	0	0	0	1	2025-10-01 22:50:32.539787	2025-10-01 22:50:32.539787	Doctorate
26	Reyon Caruth	\N	pending	2025-10-01 22:50:32.539787	\N	\N	\N	0	0	Male	2000-10-14	\N	Single	Bahamian		\N	Yes	Agriculture			1	0	0	0	0	1	2025-10-01 22:50:32.539787	2025-10-01 22:50:32.539787	No Schooling
27	job gumbs	\N	pending	2025-10-02 10:12:36.32756	\N	\N	\N	0	0	Male	1958-07-09	\N	Single	Other	Trinidadian	\N	Yes	Agriculture			1	0	0	0	0	1	2025-10-02 10:12:36.32756	2025-10-02 10:12:36.32756	No Schooling
\.


--
-- Data for Name: holding_labour; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holding_labour (id, holder_id, question_no, question_text, male_count, female_count, total_count, option_response) FROM stdin;
139	18	2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
140	18	3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
141	18	4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?	0	0	0	\N
142	18	5	Did any of your workers have work permits?	\N	\N	\N	No
143	18	6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?	\N	\N	\N	No
144	18	7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?	\N	\N	\N	No
12	5	7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?	\N	\N	\N	No
7	5	2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	2	1	3	\N
8	5	3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	1	0	1	\N
9	5	4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?	1	1	2	\N
10	5	5	Did any of your workers have work permits?	\N	\N	\N	Yes
11	5	6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?	\N	\N	\N	No
1	2	2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	4	2	6	\N
2	2	3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
3	2	4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?	1	0	1	\N
4	2	5	Did any of your workers have work permits?	\N	\N	\N	No
5	2	6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?	\N	\N	\N	Yes
6	2	7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?	\N	\N	\N	Yes
175	24	2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
176	24	3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
177	24	4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?	0	0	0	\N
178	24	5	Did any of your workers have work permits?	\N	\N	\N	Not Applicable
179	24	6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?	\N	\N	\N	Not Applicable
180	24	7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?	\N	\N	\N	Not Applicable
193	25	2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
194	25	3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
195	25	4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?	0	0	0	\N
196	25	5	Did any of your workers have work permits?	\N	\N	\N	Not Applicable
197	25	6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?	\N	\N	\N	Not Applicable
198	25	7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?	\N	\N	\N	Not Applicable
199	26	2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
200	26	3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
201	26	4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?	0	0	0	\N
202	26	5	Did any of your workers have work permits?	\N	\N	\N	Not Applicable
203	26	6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?	\N	\N	\N	Not Applicable
204	26	7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?	\N	\N	\N	Not Applicable
205	27	2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
206	27	3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?	0	0	0	\N
207	27	4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?	0	0	0	\N
208	27	5	Did any of your workers have work permits?	\N	\N	\N	Not Applicable
209	27	6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?	\N	\N	\N	Not Applicable
210	27	7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?	\N	\N	\N	Not Applicable
\.


--
-- Data for Name: holding_labour_permanent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holding_labour_permanent (id, holding_id, position_title, sex, age_code, nationality, education_code, has_agri_training, main_duties_code, working_time_code, created_at) FROM stdin;
\.


--
-- Data for Name: holdings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holdings (id, farm_name, island_id) FROM stdin;
\.


--
-- Data for Name: household_information; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.household_information (id, holder_id, holder_number, relationship_to_holder, sex, age, education_level, primary_occupation, secondary_occupation, working_time_on_holding, total_persons, persons_under_14_male, persons_under_14_female, persons_14plus_male, persons_14plus_female, persons_working_male_paid, persons_working_male_unpaid, persons_working_female_paid, persons_working_female_unpaid) FROM stdin;
\.


--
-- Data for Name: household_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.household_summary (holdings_id, holder_number, total_persons, persons_under_14_male, persons_under_14_female, persons_14plus_male, persons_14plus_female) FROM stdin;
2	2	6	2	1	1	1
\.


--
-- Data for Name: islands; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.islands (id, name, island_group, population, area_sqkm, bounds, settlements, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: labour_questions_template; Type: TABLE DATA; Schema: public; Owner: agri_user
--

COPY public.labour_questions_template (question_no, question_text) FROM stdin;
2	How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?
3	How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?
4	What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?
5	Did any of your workers have work permits?
6	Were there any volunteer workers on the holding (i.e. unpaid labourers)?
7	Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?
\.


--
-- Data for Name: land_use; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.land_use (id, holding_id, total_area_acres, years_agriculture, main_purpose, num_parcels, location, crop_methods) FROM stdin;
\.


--
-- Data for Name: land_use_parcels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.land_use_parcels (id, land_use_id, parcel_no, total_acres, developed_acres, tenure, use_of_land, irrigated_area, land_clearing) FROM stdin;
\.


--
-- Data for Name: livestock_information; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.livestock_information (id, holding_id, animal_type, medicines_used, animal_age_group, males_count, females_count, disposal_method, average_dressed_weight, average_price_per_unit, total_value, created_at) FROM stdin;
\.


--
-- Data for Name: market_trade_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.market_trade_codes (code, description) FROM stdin;
\.


--
-- Data for Name: planting_material; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.planting_material (code, description) FROM stdin;
1	Seeds
2	Seedlings
3	Cuttings
4	Tissue Plantlets
5	Suckers
6	Tubers
7	Buds
8	Other
\.


--
-- Data for Name: registration_form; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registration_form (id, consent, first_name, last_name, email, telephone, cell, communication_methods, island, settlement, latitude, longitude, created_at, available_days, available_times, interview_methods, street_address, neighborhood, postal_code) FROM stdin;
1	t	job	gumbs	mycriticalthinking123@gmail.com	242-468-4005	242-468-4005	{WhatsApp,"Phone Call"}	Abaco	Marsh Harbour	25.034300	-77.396300	2025-10-07 17:33:48.949154	{Monday,Sunday}	{"Morning (7-10am)","Evening (6-8pm)"}	\N	\N	\N	\N
2	t	Ma 	Pa	9elever9@gmail.com	466-5547	466-5547	{WhatsApp,Email}	New Providence	Nassau	25.034300	-77.396300	2025-10-07 21:27:10.199808	{Monday}	{"Afternoon (2-5pm)"}	\N	\N	\N	\N
3	t	Dragon	Lady	dr.sherlinechase1@gmail.com	345-6789	345-6789  	{WhatsApp,Email}	New Providence	Nassau	25.034300	-77.396300	2025-10-07 21:50:23.316569	{Saturday}	{"Morning (7-10am)"}	\N	Butter Close	\N	\N
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: survey_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.survey_questions (id, section_id, question_no, question_text) FROM stdin;
\.


--
-- Data for Name: survey_responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.survey_responses (id, holder_id, question_id, option_response, section) FROM stdin;
\.


--
-- Data for Name: type_of_poultry; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_of_poultry (id, holding_id, poultry_type, medicines_used, number_of_cycles, number_of_broilers, number_of_layers, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password_hash, role, "timestamp", email, status) FROM stdin;
5	admin	$2b$12$k1KSRF.fJZAQ5Vl1NOl9beGycp3h5a/sz/V8xvUQLLRNwv0dBoJPe	Admin	2025-08-27 22:22:59.621411	admin@example.com	approved
3	job gumbs	$2b$12$sVo3TziQ7QnvmhQT6f57e.vdT4gy9nRI.iJ1cELywHaRxR15L7Mwi	Holder	2025-08-26 12:10:41.4174	mycriticalthinking123@gmail.com	approved
4	sherline chase	$2b$12$uhnI3/vnq8d6Rhpm08xo8eKSql6Fp9biO/t69HdC8MelK4Pit5wQy	Holder	2025-08-26 12:30:38.274455	dr.sherlinechase@gmail.com	approved
8	ruth gumbs	$2b$12$m490xY3cVFkbwJVWvwnIs.tRLHhnvlRKGk6yqeJseyU5zrarh98gO	Holder	2025-10-07 09:27:40.772613	ruthsis@gmail.com	approved
9	leah gumbs	$2b$12$opQsUeOBOGMJ5FAY./BV5eoJnadVcr.Y9DGty/S.7tq2f4mhzKEOq	Holder	2025-10-07 10:12:15.862269	leah@gmail.com	approved
\.


--
-- Name: agents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agents_id_seq', 1, false);


--
-- Name: availability_form_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.availability_form_id_seq', 1, false);


--
-- Name: crop_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.crop_information_id_seq', 1, false);


--
-- Name: general_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.general_information_id_seq', 26, true);


--
-- Name: harvest_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.harvest_information_id_seq', 1, false);


--
-- Name: holder_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holder_information_id_seq', 1, false);


--
-- Name: holder_survey_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holder_survey_progress_id_seq', 3683, true);


--
-- Name: holders_holder_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holders_holder_id_seq', 41, true);


--
-- Name: holders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holders_id_seq', 23, true);


--
-- Name: holding_labour_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holding_labour_details_id_seq', 1, false);


--
-- Name: holding_labour_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holding_labour_id_seq', 300, true);


--
-- Name: holdings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holdings_id_seq', 1, false);


--
-- Name: household_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.household_information_id_seq', 1, false);


--
-- Name: islands_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.islands_id_seq', 1, false);


--
-- Name: land_use_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.land_use_id_seq', 1, false);


--
-- Name: land_use_parcels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.land_use_parcels_id_seq', 1, false);


--
-- Name: livestock_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.livestock_information_id_seq', 1, false);


--
-- Name: registration_form_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.registration_form_id_seq', 3, true);


--
-- Name: survey_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.survey_questions_id_seq', 1, false);


--
-- Name: survey_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.survey_responses_id_seq', 1, false);


--
-- Name: type_of_poultry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_of_poultry_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 9, true);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: availability_form availability_form_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.availability_form
    ADD CONSTRAINT availability_form_pkey PRIMARY KEY (id);


--
-- Name: crop_information crop_information_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_information
    ADD CONSTRAINT crop_information_pkey PRIMARY KEY (id);


--
-- Name: crop_type crop_type_description_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_type
    ADD CONSTRAINT crop_type_description_key UNIQUE (description);


--
-- Name: crop_type crop_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_type
    ADD CONSTRAINT crop_type_pkey PRIMARY KEY (code);


--
-- Name: general_information general_information_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_information
    ADD CONSTRAINT general_information_pkey PRIMARY KEY (id);


--
-- Name: harvest_information harvest_information_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.harvest_information
    ADD CONSTRAINT harvest_information_pkey PRIMARY KEY (id);


--
-- Name: holder_information holder_information_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holder_information
    ADD CONSTRAINT holder_information_pkey PRIMARY KEY (id);


--
-- Name: holder_survey_progress holder_survey_progress_holder_id_section_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holder_survey_progress
    ADD CONSTRAINT holder_survey_progress_holder_id_section_id_key UNIQUE (holder_id, section_id);


--
-- Name: holder_survey_progress holder_survey_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holder_survey_progress
    ADD CONSTRAINT holder_survey_progress_pkey PRIMARY KEY (id);


--
-- Name: holders holders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holders
    ADD CONSTRAINT holders_pkey PRIMARY KEY (holder_id);


--
-- Name: holding_labour_permanent holding_labour_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holding_labour_permanent
    ADD CONSTRAINT holding_labour_details_pkey PRIMARY KEY (id);


--
-- Name: holding_labour holding_labour_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holding_labour
    ADD CONSTRAINT holding_labour_pkey PRIMARY KEY (id);


--
-- Name: holdings holdings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings
    ADD CONSTRAINT holdings_pkey PRIMARY KEY (id);


--
-- Name: household_information household_information_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_information
    ADD CONSTRAINT household_information_pkey PRIMARY KEY (id);


--
-- Name: household_summary household_summary_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_summary
    ADD CONSTRAINT household_summary_pkey PRIMARY KEY (holdings_id, holder_number);


--
-- Name: islands islands_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.islands
    ADD CONSTRAINT islands_name_key UNIQUE (name);


--
-- Name: islands islands_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.islands
    ADD CONSTRAINT islands_pkey PRIMARY KEY (id);


--
-- Name: labour_questions_template labour_questions_template_pkey; Type: CONSTRAINT; Schema: public; Owner: agri_user
--

ALTER TABLE ONLY public.labour_questions_template
    ADD CONSTRAINT labour_questions_template_pkey PRIMARY KEY (question_no);


--
-- Name: land_use_parcels land_use_parcels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_use_parcels
    ADD CONSTRAINT land_use_parcels_pkey PRIMARY KEY (id);


--
-- Name: land_use land_use_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_use
    ADD CONSTRAINT land_use_pkey PRIMARY KEY (id);


--
-- Name: livestock_information livestock_information_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.livestock_information
    ADD CONSTRAINT livestock_information_pkey PRIMARY KEY (id);


--
-- Name: market_trade_codes market_trade_codes_description_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_trade_codes
    ADD CONSTRAINT market_trade_codes_description_key UNIQUE (description);


--
-- Name: market_trade_codes market_trade_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_trade_codes
    ADD CONSTRAINT market_trade_codes_pkey PRIMARY KEY (code);


--
-- Name: planting_material planting_material_description_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planting_material
    ADD CONSTRAINT planting_material_description_key UNIQUE (description);


--
-- Name: planting_material planting_material_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planting_material
    ADD CONSTRAINT planting_material_pkey PRIMARY KEY (code);


--
-- Name: registration_form registration_form_id_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_form
    ADD CONSTRAINT registration_form_id_pkey PRIMARY KEY (id);


--
-- Name: survey_questions survey_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.survey_questions
    ADD CONSTRAINT survey_questions_pkey PRIMARY KEY (id);


--
-- Name: survey_responses survey_responses_holder_id_question_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_holder_id_question_id_key UNIQUE (holder_id, question_id);


--
-- Name: survey_responses survey_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_pkey PRIMARY KEY (id);


--
-- Name: type_of_poultry type_of_poultry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_of_poultry
    ADD CONSTRAINT type_of_poultry_pkey PRIMARY KEY (id);


--
-- Name: holding_labour uq_holder_question; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holding_labour
    ADD CONSTRAINT uq_holder_question UNIQUE (holder_id, question_no);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_island_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_island_name ON public.islands USING btree (name);


--
-- Name: unique_holder_per_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_holder_per_user ON public.holders USING btree (owner_id) WHERE (owner_id IS NOT NULL);


--
-- Name: holders trg_create_holding_labour; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_create_holding_labour AFTER INSERT ON public.holders FOR EACH ROW EXECUTE FUNCTION public.create_holding_labour_rows();


--
-- Name: islands trg_update_islands_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_islands_updated_at BEFORE UPDATE ON public.islands FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: holders update_holders_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_holders_updated_at BEFORE UPDATE ON public.holders FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: agents agents_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: availability_form availability_form_registration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.availability_form
    ADD CONSTRAINT availability_form_registration_id_fkey FOREIGN KEY (registration_id) REFERENCES public.registration_form(id) ON DELETE CASCADE;


--
-- Name: crop_information crop_information_holding_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_information
    ADD CONSTRAINT crop_information_holding_id_fkey FOREIGN KEY (holding_id) REFERENCES public.holdings(id) ON DELETE CASCADE;


--
-- Name: general_information general_information_holder_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_information
    ADD CONSTRAINT general_information_holder_id_fkey FOREIGN KEY (holder_id) REFERENCES public.holders(holder_id);


--
-- Name: harvest_information harvest_information_holding_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.harvest_information
    ADD CONSTRAINT harvest_information_holding_id_fkey FOREIGN KEY (holding_id) REFERENCES public.holdings(id) ON DELETE CASCADE;


--
-- Name: harvest_information harvest_information_market_trade_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.harvest_information
    ADD CONSTRAINT harvest_information_market_trade_code_fkey FOREIGN KEY (market_trade_code) REFERENCES public.market_trade_codes(code);


--
-- Name: holder_information holder_information_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holder_information
    ADD CONSTRAINT holder_information_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.holdings(id) ON DELETE CASCADE;


--
-- Name: holder_survey_progress holder_survey_progress_holder_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holder_survey_progress
    ADD CONSTRAINT holder_survey_progress_holder_id_fkey FOREIGN KEY (holder_id) REFERENCES public.holders(holder_id) ON DELETE CASCADE;


--
-- Name: holders holders_assigned_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holders
    ADD CONSTRAINT holders_assigned_agent_id_fkey FOREIGN KEY (assigned_agent_id) REFERENCES public.users(id);


--
-- Name: holders holders_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holders
    ADD CONSTRAINT holders_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: holding_labour_permanent holding_labour_details_holding_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holding_labour_permanent
    ADD CONSTRAINT holding_labour_details_holding_id_fkey FOREIGN KEY (holding_id) REFERENCES public.holdings(id) ON DELETE CASCADE;


--
-- Name: holding_labour holding_labour_holder_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holding_labour
    ADD CONSTRAINT holding_labour_holder_id_fkey FOREIGN KEY (holder_id) REFERENCES public.holders(holder_id) ON DELETE CASCADE;


--
-- Name: holdings holdings_island_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings
    ADD CONSTRAINT holdings_island_id_fkey FOREIGN KEY (island_id) REFERENCES public.islands(id) ON DELETE CASCADE;


--
-- Name: land_use land_use_holding_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_use
    ADD CONSTRAINT land_use_holding_id_fkey FOREIGN KEY (holding_id) REFERENCES public.holdings(id);


--
-- Name: land_use_parcels land_use_parcels_land_use_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_use_parcels
    ADD CONSTRAINT land_use_parcels_land_use_id_fkey FOREIGN KEY (land_use_id) REFERENCES public.land_use(id);


--
-- Name: livestock_information livestock_information_holding_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.livestock_information
    ADD CONSTRAINT livestock_information_holding_id_fkey FOREIGN KEY (holding_id) REFERENCES public.holdings(id) ON DELETE CASCADE;


--
-- Name: survey_responses survey_responses_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.survey_questions(id);


--
-- Name: type_of_poultry type_of_poultry_holding_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_of_poultry
    ADD CONSTRAINT type_of_poultry_holding_id_fkey FOREIGN KEY (holding_id) REFERENCES public.holdings(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO agri_user;


--
-- Name: TABLE agents; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.agents TO agri_user;


--
-- Name: TABLE availability_form; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.availability_form TO agri_user;


--
-- Name: TABLE crop_information; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.crop_information TO agri_user;


--
-- Name: TABLE crop_type; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.crop_type TO agri_user;


--
-- Name: TABLE general_information; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.general_information TO agri_user;


--
-- Name: TABLE geography_columns; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.geography_columns TO agri_user;


--
-- Name: TABLE geometry_columns; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.geometry_columns TO agri_user;


--
-- Name: TABLE harvest_information; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.harvest_information TO agri_user;


--
-- Name: TABLE holder_information; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.holder_information TO agri_user;


--
-- Name: TABLE holder_survey_progress; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.holder_survey_progress TO agri_user;


--
-- Name: SEQUENCE holder_survey_progress_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.holder_survey_progress_id_seq TO agri_user;


--
-- Name: TABLE holders; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.holders TO agri_user;


--
-- Name: SEQUENCE holders_holder_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.holders_holder_id_seq TO agri_user;


--
-- Name: SEQUENCE holders_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.holders_id_seq TO agri_user;


--
-- Name: TABLE holding_labour; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.holding_labour TO agri_user;


--
-- Name: TABLE holding_labour_permanent; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.holding_labour_permanent TO agri_user;


--
-- Name: SEQUENCE holding_labour_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.holding_labour_id_seq TO agri_user;


--
-- Name: TABLE holdings; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.holdings TO agri_user;


--
-- Name: TABLE household_information; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.household_information TO agri_user;


--
-- Name: TABLE household_summary; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.household_summary TO agri_user;


--
-- Name: TABLE islands; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.islands TO agri_user;


--
-- Name: TABLE land_use; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.land_use TO agri_user;


--
-- Name: TABLE land_use_parcels; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.land_use_parcels TO agri_user;


--
-- Name: TABLE livestock_information; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.livestock_information TO agri_user;


--
-- Name: TABLE market_trade_codes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.market_trade_codes TO agri_user;


--
-- Name: TABLE planting_material; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.planting_material TO agri_user;


--
-- Name: TABLE registration_form; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.registration_form TO agri_user;


--
-- Name: TABLE spatial_ref_sys; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.spatial_ref_sys TO agri_user;


--
-- Name: TABLE survey_questions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.survey_questions TO agri_user;


--
-- Name: TABLE survey_responses; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.survey_responses TO agri_user;


--
-- Name: TABLE type_of_poultry; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.type_of_poultry TO agri_user;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.users TO agri_user;


--
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.users_id_seq TO agri_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO agri_user;


--
-- PostgreSQL database dump complete
--

