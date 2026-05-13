create table if not exists studies(
    study_id integer primary key autoincrement,
    study_name varchar(255) not null,
    irb_number varchar(255) not null
);

create table if not exists patients(
    patient_id integer primary key autoincrement,
    iml_number varchar(255) not null,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    date_of_birth date,
    ccf_number varchar(255),
    uh_id varchar(255)
);

create table if not exists enrollments(
    enrollment_id integer primary key autoincrement,
    study_id integer not null,
    patient_id integer not null,
    enrollment_date date,
    foreign key (study_id) references studies(study_id),
    foreign key (patient_id) references patients(patient_id)
);

create table if not exists accessions(
    accession_id integer primary key autoincrement,
    enrollment_id integer not null,
    accession_date date not null,
    timepoint varchar(255),
    disease_type varchar(255),
    freezer_id varchar(255),
    tech_name varchar(255),
    notes text,
    foreign key (enrollment_id) references enrollments(enrollment_id)
);

create table if not exists accession_details(
    accession_detail_id integer primary key autoincrement,
    accession_id integer not null,
    field_name varchar(255),
    field_value varchar(255),
    foreign key (accession_id) references accessions(accession_id)
);

create table if not exists tube_types(
    tube_type_id integer primary key autoincrement,
    tube_type_name varchar(255) not null
);

create table if not exists tube_accessions(
    tube_accession_id integer primary key autoincrement,
    tube_type_id integer not null,
    accession_id integer not null,
    quantity integer,
    foreign key (accession_id) references accessions(accession_id),
    foreign key (tube_type_id) references tube_types(tube_type_id)
);